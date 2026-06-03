import requests
import subprocess
import tempfile
import os

# Prompt Processing - S:1 : SYSTEM ROLE PROMPT
SYSTEM_ROLE = """You are a software engineer who works only in Python.
Your job responsibility is to write clean, executable Python code.
You can write Python code.
You only output Python code.
You do no know any other programming language.
You do not explain your code. You do not chat.
You do not introduce yourself."""

# Prompt Processing - S:2 : NEGATIVE CONSTRAINTS
NEGATIVE_CONSTRAINTS = """
STRICT RULES - YOU MUST FOLLOW ALL OF THESE:
- You ONLY write Python code.
- If the user requests any other programming language, still write it in Python.
- Do NOT include any explanation, description, or analysis.
- Do NOT use markdown code fences (no ```python or ``` anywhere in your response).
- Do NOT write introductory sentences such as "Sure!", "Here is the code", or "Of course!".
- Do NOT add conclusion or summary after the code.
- Do NOT repeat the user request back to them.
- Output ONLY the raw, executable Python code. NOTHING else.
"""

# Prompt Processing - S:3 : FEW-SHOT EXAMPLE
FEW_SHOT_EXAMPLE = """
EXAMPLE OF THE CORRECT OUTPUT FORMAT:
User Request: Write a function that checks if a number is even or odd.
Output:
def even_odd_checker(number):
    # Returns 'Even' if the number is even, 'Odd' otherwise
    if number % 2 == 0:
        return "Even"
    else:
        return "Odd"
# Usage example
result = even_odd_checker(4)
print(result)   # Should be Even
result = even_odd_checker(7)
print(result)   # Should be Odd
"""

# Assemble / Concat all the PROMPT
def build_prompt(user_input):

    full_prompt = (
        SYSTEM_ROLE # Layer 1: System role
        + "\n\n"
        + NEGATIVE_CONSTRAINTS # Layer 2: Negative constraints
        + "\n\n"
        + FEW_SHOT_EXAMPLE # Layer 3: Few-shot example
        + "\n\n"
        # Transition line to let LLM know to analyze the main task
        + "Now complete the following request using exactly the same format as the example above:\n"
        + "User Request: "
        + user_input # The actual user input fetched from Dashboard
        + "\n\n"
        + "Output:" # Completion trigger
    )
    return full_prompt

# Post Processing Step
def post_process(response):
    response = response.replace("```python", "") # Delete markdown code fences if exist
    response = response.replace("```", "")
    # Delete common introductory phrases if exist
    unwanted_phrases = [
        "Sure!",
        "Sure, ",
        "Of course!",
        "Here is the code:",
        "Here's the code:",
        "Here is your Python code:",
        "Here's your Python code:",
        "Here is your code:",
        "Here's your code:",
    ]
    for phrase in unwanted_phrases:
        response = response.replace(phrase, "")
    response = response.strip() # Strip leading and trailing blank lines
    return response

# Code validation by Pylint
def validate_code(code_string):

    # S:1 : Keep the generated code to temp Python file
    with tempfile.NamedTemporaryFile(
        suffix=".py",
        mode="w",
        delete=False,
        encoding="utf-8"
    ) as tmp_file:
        tmp_file.write(code_string)
        tmp_path = tmp_file.name
    try:
        # S:2 : Run pylint on the temp file
        result = subprocess.run(
            ["pylint", tmp_path, "--errors-only"],
            capture_output=True,
            text=True
        )
        # S:3 : Combine standard output and error from pylint into one string
        pylint_output = result.stdout + result.stderr
        # Step 4: Build a readable result message for the user
        if pylint_output.strip() == "":
            validation_result = "No errors found by Pylint." # # pylint produced no output = no error
        else:
            # pylint found issues — show them to the user
            # Remove the temporary file path from the output so it looks clean
            clean_output = pylint_output.replace(tmp_path, "generated_code.py")
            validation_result = "PyLint found the following issues:\n\n" + clean_output

    except FileNotFoundError:
        validation_result = (
            "PyLint is not installed."
        )
    finally:
        # S:4 : Delete temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return validation_result

# Concatinate the prompts
# Main Function - generate_response()
def generate_response(user_prompt):

    # S:1 : Build the full prompt by calling build_prompt method and passing user_prompt param
    full_prompt = build_prompt(user_prompt)
    try:
        # S:2 : Send the combined prompt to the Ollama local API
        # Note: Ollama must be running before calling this
        # Command Prompt: ollama serve
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model":  "llama3.1:8b", # pre-trained model
                "prompt": full_prompt,
                "stream": False, # wait for the complete response before returning
                # LLM Configuration Parameters
                "options": {
                    "temperature":    0.3, # temperature = 0.3  = low value enforces deterministic
                    "num_predict":    2048, # num_predict = 2048 = maximum tokens the model can generate
                    "top_p":          0.9, # top_p = 0.9 = nucleus sampling, keeps output focused
                    "repeat_penalty": 1.1, # repeat_penalty = 1.1 = discourages repeating the same code lines
                },
            },
            timeout=120, # wait up to 120 seconds for the model to respond
        )
        # S:3 : Extract the raw text from the Ollama API response JSON
        raw_response = response.json().get("response", "No response received from model.")
        # S:4 : Remove any markdown fences or introductory phrases
        clean_response = post_process(raw_response)
        # S:5 : Return the clean Python code to dashboard.py for display
        return clean_response
    except requests.exceptions.ConnectionError:
        # Ollama is not running — guide the user to start it
        return (
            "Error: Could not connect to Ollama.\n\n"
            "Check that Ollama is running.\n"
            "Open a terminal and run: ollama serve"
        )
    except requests.exceptions.Timeout:
        # No response within Timer (120 Seconds)
        return (
            "Error: The model took too long to respond.\n\n"
            "Please try again."
        )
