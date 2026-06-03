# welcome_page.py - Welcome / Login screen

import tkinter as tk
from tkinter import messagebox
import authenticator


class Login(tk.Frame):

    def __init__(self, master, on_login_success, on_guest_login, on_open_register):
        super().__init__(master, bg="white")
        self.on_login_success = on_login_success
        self.on_guest_login = on_guest_login
        self.on_open_register = on_open_register
        self.build()

    def build(self):
        # centre column
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        center = tk.Frame(self, bg="white")
        center.grid(row=0, column=0)

        # header
        tk.Label(center, text="Welcome to Helping Hand",
                 font=("Arial", 20, "bold"),
                 bg="white", fg="black").grid(row=0, column=0, columnspan=2,
                                              pady=(40, 4))

        tk.Label(center, text="Draw your imagination...",
                 font=("Arial", 11, "italic"),
                 bg="white", fg="black").grid(row=1, column=0, columnspan=2,
                                              pady=(0, 30))

        # username
        tk.Label(center, text="Username",
                 font=("Arial", 11), bg="white", fg="black").grid(
            row=2, column=0, padx=10, pady=8, sticky="e")

        self.username_entry = tk.Entry(center, font=("Arial", 11), width=25)
        self.username_entry.grid(row=2, column=1, padx=10, pady=8, sticky="w")

        # password
        tk.Label(center, text="Password",
                 font=("Arial", 11), bg="white", fg="black").grid(
            row=3, column=0, padx=10, pady=8, sticky="e")

        self.password_entry = tk.Entry(center, font=("Arial", 11),
                                       width=25, show="*")
        self.password_entry.grid(row=3, column=1, padx=10, pady=8, sticky="w")

        # buttons
        btn_frame = tk.Frame(center, bg="white")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=30)

        tk.Button(btn_frame, text="LOGIN",
                  font=("Arial", 11),
                  width=20,
                  command=self.handle_login).pack(pady=6)

        tk.Button(btn_frame, text="REGISTER & LOGIN",
                  font=("Arial", 11),
                  width=20,
                  command=self.on_open_register).pack(pady=6)

        tk.Button(btn_frame, text="GUEST USER LOGIN",
                  font=("Arial", 11),
                  width=20,
                  command=self.on_guest_login).pack(pady=6)

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username == "" or password == "":
            messagebox.showwarning("Error!",
                                   "Username and Password is required.")
            return

        if authenticator.validate_login(username, password):
            self.on_login_success(username)
        else:
            messagebox.showerror("Error!",
                                 "Correct username or password is required.") 