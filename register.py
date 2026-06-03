import tkinter as tk
from tkinter import messagebox
import authenticator


class Register(tk.Toplevel):

    def __init__(self, master, on_register_success):
        super().__init__(master)
        self.on_register_success = on_register_success
        self.title("Register & Login")
        self.configure(bg="white")
        self.resizable(True, True)
        self.grab_set()  # make it modal

        # centre the popup on top of the main window
        self.update_idletasks()
        width = 400
        height = 280
        mx = master.winfo_x() + master.winfo_width() // 2
        my = master.winfo_y() + master.winfo_height() // 2
        self.geometry(f"{width}x{height}+{mx - width // 2}+{my - height // 2}")

        self.build()

    def build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        center = tk.Frame(self, bg="white")
        center.grid(row=0, column=0)

        # username
        tk.Label(center, text="Username",
                 font=("Arial", 11), bg="white", fg="black").grid(
            row=0, column=0, padx=10, pady=12, sticky="e")

        self.username_entry = tk.Entry(center, font=("Arial", 11), width=22)
        self.username_entry.grid(row=0, column=1, padx=10, pady=12, sticky="w")

        # password
        tk.Label(center, text="Password",
                 font=("Arial", 11), bg="white", fg="black").grid(
            row=1, column=0, padx=10, pady=12, sticky="e")

        self.password_entry = tk.Entry(center, font=("Arial", 11),
                                       width=22, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=12, sticky="w")

        # buttons
        btn_frame = tk.Frame(center, bg="white")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)

        tk.Button(btn_frame, text="REGISTER & LOGIN",
                  font=("Arial", 11),
                  width=20,
                  command=self.handle_register).pack(pady=6)

        tk.Button(btn_frame, text="CLOSE",
                  font=("Arial", 11),
                  width=20,
                  command=self.destroy).pack(pady=6)

    def handle_register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        success, message = authenticator.register_user(username, password)
        if success:
            self.destroy()
            self.on_register_success(username)
        else:
            messagebox.showerror("Registration Failed", message, parent=self)

