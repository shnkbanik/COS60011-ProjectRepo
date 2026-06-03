# dashboard.py - Main Dashboard screen

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import llm_service


class Dashboard(tk.Frame):

    def __init__(self, master, username, is_guest, on_logout):
        super().__init__(master, bg="white")
        self.username = username if username else "Guest"
        self.is_guest = is_guest
        self.on_logout = on_logout
        self.build()

    def build(self):
        # make this frame fill the whole window
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Top bar
        top_bar = tk.Frame(self, bg="white", bd=1, relief="solid")
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.columnconfigure(0, weight=1)

        tk.Label(top_bar, text=f"Logged in as: {self.username}",
                 font=("Arial", 10), bg="white", fg="black").grid(
            row=0, column=0, padx=10, pady=6, sticky="w")

        if self.is_guest:
            btn_text = "Go to Login Page"
        else:
            btn_text = "LOG OUT"

        tk.Button(top_bar, text=btn_text,
                  font=("Arial", 10),
                  command=self.on_logout).grid(
            row=0, column=1, padx=10, pady=6, sticky="e")

        # Title
        header = tk.Frame(self, bg="white")
        header.grid(row=1, column=0, sticky="ew")

        tk.Label(header, text="Helping Hand",
                 font=("Arial", 18, "bold"),
                 bg="white", fg="black").pack(pady=(16, 2))

        tk.Label(header, text="Draw your imagination...",
                 font=("Arial", 11, "italic"),
                 bg="white", fg="black").pack(pady=(0, 10))

        tk.Frame(self, bg="black", height=1).grid(
            row=2, column=0, sticky="ew")

        # Chat area - scrollable field
        chat_outer = tk.Frame(self, bg="white")
        chat_outer.grid(row=3, column=0, sticky="nsew", padx=10, pady=6)
        chat_outer.rowconfigure(0, weight=1)
        chat_outer.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        self.chat_canvas = tk.Canvas(chat_outer, bg="white",
                                     highlightthickness=0)
        self.chat_canvas.grid(row=0, column=0, sticky="nsew")

        chat_scroll = tk.Scrollbar(chat_outer, orient="vertical",
                                   command=self.chat_canvas.yview)
        chat_scroll.grid(row=0, column=1, sticky="ns")
        self.chat_canvas.configure(yscrollcommand=chat_scroll.set)

        # inner frame that holds all chat bubbles
        self.chat_inner = tk.Frame(self.chat_canvas, bg="white")
        self.chat_window_id = self.chat_canvas.create_window(
            (0, 0), window=self.chat_inner, anchor="nw")

        self.chat_inner.bind("<Configure>", self.update_scroll_region)
        self.chat_canvas.bind("<Configure>", self.on_canvas_resize)
        self.chat_canvas.bind("<Enter>", self.bind_mousewheel)
        self.chat_canvas.bind("<Leave>", self.unbind_mousewheel)

        # Bottom controls
        bottom = tk.Frame(self, bg="white", bd=1, relief="solid")
        bottom.grid(row=4, column=0, sticky="ew")
        bottom.columnconfigure(1, weight=1)

        tk.Label(bottom, text="User Input :",
                 font=("Arial", 11), bg="white", fg="black").grid(
            row=0, column=0, padx=(10, 4), pady=(10, 10), sticky="nw")

        input_frame = tk.Frame(bottom, bg="white")
        input_frame.grid(row=0, column=1, padx=(0, 10),
                         pady=(10, 10), sticky="ew")
        input_frame.columnconfigure(0, weight=1)

        self.input_box = tk.Text(input_frame, height=3,
                                 font=("Arial", 11), wrap="word")
        self.input_box.grid(row=0, column=0, sticky="ew")

        input_scrollbar = tk.Scrollbar(input_frame, orient="vertical",
                                       command=self.input_box.yview)
        self.input_box.configure(yscrollcommand=input_scrollbar.set)
        input_scrollbar.grid(row=0, column=1, sticky="ns")

        tk.Button(bottom, text="Search",
                  font=("Arial", 11),
                  command=self.handle_search).grid(
            row=0, column=2, padx=(0, 10), pady=(10, 10), sticky="s")

    # Scroll bar
    def update_scroll_region(self, event=None):
        self.chat_canvas.configure(
            scrollregion=self.chat_canvas.bbox("all"))

    def on_canvas_resize(self, event):
        self.chat_canvas.itemconfig(self.chat_window_id, width=event.width)

    def bind_mousewheel(self, event):
        self.chat_canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def unbind_mousewheel(self, event):
        self.chat_canvas.unbind_all("<MouseWheel>")

    def on_mousewheel(self, event):
        self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def scroll_to_bottom(self):
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    # User message bubble
    def add_user_bubble(self, prompt_text):
        frame = tk.Frame(self.chat_inner, bg="white")
        frame.pack(fill="x", padx=10, pady=(8, 2))

        tk.Label(frame, text="You  👤",
                 font=("Arial", 10, "bold"),
                 bg="white", fg="black",
                 anchor="e").pack(side="top", anchor="e")

        # sub-frame with grid so scrollbar is always visible
        msg_frame = tk.Frame(frame, bg="white")
        msg_frame.pack(fill="x", anchor="e")
        msg_frame.columnconfigure(0, weight=1)

        msg_box = tk.Text(msg_frame, font=("Arial", 11), wrap="word",
                          height=3, bg="#F0F0F0",
                          relief="solid", bd=1)
        msg_box.grid(row=0, column=0, sticky="ew")

        user_scrollbar = tk.Scrollbar(msg_frame, orient="vertical",
                                      command=msg_box.yview)
        msg_box.configure(yscrollcommand=user_scrollbar.set)
        user_scrollbar.grid(row=0, column=1, sticky="ns")

        msg_box.insert("1.0", prompt_text)
        msg_box.configure(state="disabled")

        self.scroll_to_bottom()

    # LLM response bubble
    def add_llm_bubble(self, response_text):
        frame = tk.Frame(self.chat_inner, bg="white")
        frame.pack(fill="x", padx=10, pady=(2, 8))

        tk.Label(frame, text="💡  Helping Hand",
                 font=("Arial", 10, "bold"),
                 bg="white", fg="black",
                 anchor="w").pack(side="top", anchor="w")

        # generated code text box with scrollbar
        resp_frame = tk.Frame(frame, bg="white")
        resp_frame.pack(fill="x")
        resp_frame.columnconfigure(0, weight=1)

        resp_box = tk.Text(resp_frame, font=("Arial", 11), wrap="word",
                           height=8, bg="#F9F9F9",
                           relief="solid", bd=1)
        resp_box.grid(row=0, column=0, sticky="ew")

        resp_scrollbar = tk.Scrollbar(resp_frame, orient="vertical",
                                      command=resp_box.yview)
        resp_box.configure(yscrollcommand=resp_scrollbar.set)
        resp_scrollbar.grid(row=0, column=1, sticky="ns")

        resp_box.insert("1.0", response_text)
        resp_box.configure(state="disabled")

        # Copy and Save Button
        btn_row = tk.Frame(frame, bg="white")
        btn_row.pack(anchor="w", pady=(4, 0))

        tk.Button(btn_row, text="Copy",
                  font=("Arial", 10),
                  command=lambda: self.copy_text(response_text)).pack(
            side="left", padx=(0, 6))

        tk.Button(btn_row, text="Save as .txt",
                  font=("Arial", 10),
                  command=lambda: self.save_text(response_text)).pack(
            side="left", padx=(0, 6))

        # Validate button — passes the generated code to pylint via llm_service
        tk.Button(btn_row, text="Validate Code by PyLint",
                  font=("Arial", 10),
                  command=lambda: self.run_validation(
                      response_text, validation_box
                  )).pack(side="left")

        # Validation result box
        val_frame = tk.Frame(frame, bg="white")
        val_frame.pack(fill="x", pady=(6, 0))
        val_frame.columnconfigure(0, weight=1)

        validation_box = tk.Text(val_frame,
                                 font=("Arial", 10),
                                 wrap="word",
                                 height=0,        # hidden until validation runs
                                 bg="#FFFBEA",    # light yellow background
                                 relief="solid",
                                 bd=1)
        validation_box.grid(row=0, column=0, sticky="ew")

        val_scrollbar = tk.Scrollbar(val_frame, orient="vertical",
                                     command=validation_box.yview)
        validation_box.configure(yscrollcommand=val_scrollbar.set)
        val_scrollbar.grid(row=0, column=1, sticky="ns")

        self.scroll_to_bottom()

    # PyLint Validation Handler
    def run_validation(self, code_text, validation_box):
        validation_box.configure(state="normal", height=3)
        validation_box.delete("1.0", tk.END)
        validation_box.insert("1.0", "Running PyLint validation, please wait...")
        validation_box.configure(state="disabled")
        self.scroll_to_bottom()

        def worker():
            result = llm_service.validate_code(code_text)
            self.after(0, lambda: show_result(result))

        def show_result(result):
            validation_box.configure(state="normal")
            validation_box.delete("1.0", tk.END)
            validation_box.insert("1.0", result)
            # Expand height based on result length, capped at 10 lines
            line_count = result.count("\n") + 2
            validation_box.configure(
                state="disabled",
                height=min(line_count, 10)
            )
            self.scroll_to_bottom()

        threading.Thread(target=worker, daemon=True).start()

    # ── Thinking indicator ────────────────────────────────────────────────
    def add_thinking_label(self):
        frame = tk.Frame(self.chat_inner, bg="white")
        frame.pack(fill="x", padx=10, pady=4)
        lbl = tk.Label(frame, text="Helping Hand is thinking...",
                       font=("Arial", 10, "italic"),
                       bg="white", fg="gray")
        lbl.pack(anchor="w")
        return frame

    # Copy Button and Save Button in Output
    def copy_text(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Response copied to clipboard.")

    def save_text(self, text):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.isdir(desktop):
            desktop = os.path.expanduser("~")
        filepath = filedialog.asksaveasfilename(
            initialdir=desktop,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Response")
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Saved", f"File saved to:\n{filepath}")

    # Search button handler
    def handle_search(self):
        prompt = self.input_box.get("1.0", tk.END).strip()
        if prompt == "":
            messagebox.showwarning("Empty Input",
                                   "Please type something before searching.")
            return

        self.input_box.delete("1.0", tk.END)

        self.add_user_bubble(prompt)
        thinking = self.add_thinking_label()

        def worker():
            response = llm_service.generate_response(prompt)
            self.after(0, lambda: finish(response))

        def finish(response):
            thinking.destroy()
            self.add_llm_bubble(response)

        threading.Thread(target=worker, daemon=True).start()