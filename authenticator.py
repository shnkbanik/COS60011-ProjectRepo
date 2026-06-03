import json
import os

USERS_FILE = os.path.join(os.path.dirname(__file__), "user.json")


def load_users():
    with open(USERS_FILE, "r") as f:
        data = json.load(f)
    return data.get("users", [])


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump({"users": users}, f, indent=2)


def validate_login(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return True
    return False


def user_exists(username):
    users = load_users()
    for user in users:
        if user["username"] == username:
            return True
    return False


def register_user(username, password):
    if username == "":
        return False, "Username is required."
    if password == "":
        return False, "Password is required."
    if user_exists(username):
        return False, "Username already exists. Please choose another."

    users = load_users()
    users.append({"username": username, "password": password})
    save_users(users)
    return True, "OK"

