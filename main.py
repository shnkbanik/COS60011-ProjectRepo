import tkinter as tk
import configuration
# import classes (components of application) from files

#from login import Login
from register import Register
#from dashboard import Dashboard


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title(configuration.APP_TITLE)
        self.configure(bg="white") # Background Color Setup
        self.resizable(True, True) # Window Flexible Size Define

        # minimum size of the window
        self.minsize(600, 500)
        # starting size of the window
        self.geometry("850x620")

        # centre on screen
        self.update_idletasks()
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        x = (screenwidth - 850) // 2
        y = (screenheight - 620) // 2
        self.geometry(f"850x620+{x}+{y}")

        # single cell that fills the whole window
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.current_frame = None
        # Display login page at first
        self.show_login()

    def switch_to(self, frame):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame
        frame.grid(row=0, column=0, sticky="nsew")

    # Login Page Function
    def show_login(self):
        self.title("Helping Hand")
        page = Login(
            master=self,
            on_login_success=self.show_dashboard_user, # for successful login
            on_guest_login=self.show_dashboard_guest, # for guest user login
            on_open_register=self.open_register_popup, # for registration journey
        )
        self.switch_to(page)

    def open_register_popup(self):
        Register(
            master=self,
            on_register_success=self.show_dashboard_user, # for successful registration
        )

    def show_dashboard_user(self, username):
        self.title("Helping Hand - Dashboard")
        page = Dashboard(
            master=self,
            username=username,
            is_guest=False,
            on_logout=self.show_login,
        )
        self.switch_to(page)

    def show_dashboard_guest(self):
        self.title("Helping Hand - Dashboard")
        page = Dashboard(
            master=self,
            username=None,
            is_guest=True,
            on_logout=self.show_login,
        )
        self.switch_to(page)


if __name__ == "__main__":
    app = App()
    app.mainloop()
