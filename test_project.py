# import pytest
import os.path

from project import main, setup_login_window, validate_login, create_login
import sqlite3
from tkinter import *
from tkinter import ttk


def test_setup_login_window():
    root_window = Tk()
    w_pass = Toplevel(root_window)
    setup_login_window(w_pass, root_window)

    # Assert that components of the login window are correctly set up
    assert isinstance(w_pass, Toplevel)
    assert isinstance(w_pass.winfo_children()[0], ttk.Frame)


def test_validate_login():
    # Create a test data or mocks for validation
    root_window = Tk()
    w_tl = Toplevel(root_window)
    acc = StringVar(value="test_account")
    passwd = StringVar(value="test_password")
    parent = ttk.Frame(w_tl)

    print(w_tl.winfo_children())
    # Call the function and assert that it doesn't return anything
    assert validate_login(w_tl, acc, passwd, parent, root_window) is None


def test_create_login():
    # Create a memory DB
    db = sqlite3.connect(":memory:")
    l_back_window = ttk.Label()
    b_reg = ttk.Button()

    # Call function and check if successfully accepts arguments
    create_login(db, l_back_window, b_reg)

    # Check if db was successfully created
    assert os.path.exists("diary.db") is True

    # Check if db is unlocked
    db = sqlite3.connect("diary.db")

    assert db is not None

    # Check if db was created with correct table
    cursor = db.execute("SELECT sql FROM sqlite_master WHERE name = ?", ["accounts"])
    schema = cursor.fetchone()[0]

    assert schema == ("CREATE TABLE accounts ("
                      "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                      "account TEXT, "
                      "first_name TEXT, "
                      "last_name TEXT, "
                      "hashed_password BLOB, "
                      "key_verification BLOB)"
                      )
