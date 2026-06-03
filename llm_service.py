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
