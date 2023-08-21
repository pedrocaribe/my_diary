import sqlite3

from cryptography.fernet import Fernet
from tkinter import *
from tkinter import ttk
from project_classes import User


def main(root):
    """Keep record of daily activities, stored in DB and password protected

    My Diary was developed to assist those in need to keep records of their
    daily activities and thoughts that they would like to keep records of,
    while maintaining their privacy and possibility to share if they want.

    Typical usage example:

    python3 project.py
    """

    root.withdraw()  # Hide main window until user is authenticated

    # Create new toplevel window for authentication process in center of screen
    w_pass = Toplevel()
    root.eval(f'tk::PlaceWindow {str(w_pass)} center')

    # Initiate authentication process
    setup_login_window(w_pass, root)


def setup_login_window(w_pass: Toplevel, w_root: Tk):
    """Setup User Login window

    This function sets up a login window, in which user can insert a username
    along with a registered password.
    It then triggers validate_login function to perform checks.

    Parameters:
        w_pass: A Toplevel window in which to build the login widgets.
        w_root: A Tk object which will be shown after authentication.

    Returns:
        This function does Not return anything.
    """

    w_pass.resizable(False, False)
    w_pass.title("My Diary - Login")

    # Create new frame
    f_pass = ttk.Frame(w_pass, padding=(3, 3, 12, 12))
    f_pass.grid(column=0, row=0, sticky="nsew")

    l_title = ttk.Label(f_pass, text="Please enter your credentials", anchor="center")
    l_title.grid(column=0, row=1, columnspan=3, sticky="nsew", pady=(5, 10))

    Label(f_pass, text="Account:").grid(column=0, row=2, sticky=W, padx=5)
    Label(f_pass, text="Password:").grid(column=0, row=3, sticky=W, padx=5)

    acc_str = StringVar()
    pw_str = StringVar()

    # Entry fields, cursor on account field
    e_acc = ttk.Entry(f_pass, textvariable=acc_str)
    e_acc.grid(column=1, row=2, columnspan=2, sticky="nsew")
    e_acc.focus()

    ttk.Entry(f_pass, textvariable=pw_str, show='*').grid(column=1, row=3, columnspan=2, sticky="nsew")

    # Submit and cancel buttons
    b_submit = ttk.Button(f_pass, text="Submit", command=lambda: validate_login(w_pass, acc_str, pw_str, f_pass, w_root))
    b_submit.grid(column=1, row=4, pady=(10, 0))

    b_close = ttk.Button(f_pass, text="Close", command=w_root.destroy)
    b_close.grid(column=2, row=4, pady=(10, 0))


def validate_login(w_tl: Toplevel, acc: StringVar, passwd: StringVar, parent: Frame, w_root: Tk):
    """Login Validation

    Validates login information provided by user.
    Provides feedback to user if account doesn't match DB.

    Parameters:
        w_tl: A TopLevel window in which user typed information.
        acc: A string containing the account name provided by user.
        passwd: A string containing password provided by user.
        parent: Frame which will hold all Widgets.
        w_root: Root window which contains main screen, hidden until login.

    Returns:
        This functions does Not return anything.
    """

    acc = acc.get()
    passwd = passwd.get()

    # Establish connection to DB and create table if it is first use
    db = sqlite3.connect("diary.db")
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS accounts ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "account TEXT, "
                "first_name TEXT, "
                "last_name TEXT, "
                "hashed_password BLOB, "
                "key_verification BLOB)")

    # Check if account provided by user already exists in DB
    check = cur.execute("SELECT * FROM accounts WHERE account = ?", (acc,)).fetchone()

    # Create return label for posterior checks
    l_return = ttk.Label(parent, text="", anchor="center")
    l_return.grid(column=0, row=5, columnspan=4, sticky="nsew")

    # Login Checks
    if not acc:
        l_return.configure(text="Account cannot be blank")  # If user doesn't provide account name
    elif not check:
        l_return.configure(text="Invalid account, please register")  # If account not registered in DB
        b_register = ttk.Button(parent, text="Register", command=lambda: create_login(db, l_return, b_register))
        b_register.grid(column=0, row=4, pady=(10, 0))

    # If account was found in DB, decrypt password provided with stored hash key and confirm login information
    else:
        hashed_pass = check[4]
        key = check[5]
        fernet = Fernet(key)
        raw_pass = fernet.decrypt(hashed_pass).decode()

        # Compare password provided with decrypted password
        if raw_pass == passwd:
            l_return.configure(text="Login Successful")

            # If login successful, destroy toplevel window and show main
            w_tl.destroy()
            user = User(w_root, acc)
            user.garbage_collector()  # Run garbage collector to clean-up empty entries in DB
            user.main_window()
            w_root.deiconify()
        else:
            l_return.configure(text="Incorrect Password")


def create_login(db, l_back_window: Label, b_reg: ttk.Button):
    """Create login if user not found in DB.

    Parameters:
        db: Database in which user will be registered.
        l_back_window: Label to give a registration feedback to user
        b_reg: Button to disable onde registration is complete

    Returns:
        This functions does Not return anything.
    """

    # Create new window for registration fields
    w_reg = Toplevel()
    w_reg.grab_set()  # Disable windows in background
    w_reg.attributes("-topmost", "true")
    w_reg.configure(pady=10, padx=10)
    w_reg.resizable(False, False)

    # Create fields and variables for fetching data inputted by user
    Label(w_reg, text="First Name:").grid(column=0, row=1)
    Label(w_reg, text="Last Name:").grid(column=0, row=2)
    Label(w_reg, text="Account:").grid(column=0, row=3)
    Label(w_reg, text="Password:").grid(column=0, row=4)
    Label(w_reg, text="Password Confirmation:").grid(column=0, row=5)

    first_str = StringVar()
    last_str = StringVar()
    acc_str = StringVar()
    pass_str = StringVar()
    pass_conf_str = StringVar()

    Entry(w_reg, textvariable=first_str).grid(column=1, row=1, columnspan=2)
    Entry(w_reg, textvariable=last_str).grid(column=1, row=2, columnspan=2)
    Entry(w_reg, textvariable=acc_str).grid(column=1, row=3, columnspan=2)
    Entry(w_reg, textvariable=pass_str, show="*").grid(column=1, row=4, columnspan=2)
    Entry(w_reg, textvariable=pass_conf_str, show="*").grid(column=1, row=5, columnspan=2)

    f_new = ttk.Frame(w_reg)
    f_new.grid(column=0, row=6, columnspan=3)

    # Definition of function for registration process
    def register():
        """Register user to DB

        This Function has responsibility to check DB and confirm
        if user provided is existent or not and if all fields were
        entered by user.

        Parameters:
            This function takes no parameters.

        Returns:
            This function does Not return anything.
        """

        # Information fetching
        parent = w_reg  # reassigned variable name for easier understanding within scope
        first = first_str.get()
        last = last_str.get()
        acc = acc_str.get()
        passwd = pass_str.get()
        conf_passwd = pass_conf_str.get()

        # Check if user provided already exists in DB
        check = db.execute("SELECT * FROM accounts WHERE account = ?", (acc,)).fetchone()

        # Create return label for posterior checks
        l_register = Label(parent, text="", anchor="center")
        l_register.grid(column=0, row=7, columnspan=4, sticky="nsew")

        # Diverse checks
        if check:
            l_register.configure(text="Account already exists")
        elif not acc:
            l_register.configure(text="Account cannot be blank")
        elif not passwd:
            l_register.configure(text="Password cannot be blank")

        if passwd != conf_passwd:
            l_register.configure(text="Passwords do Not match")

        # If all checks passed, register user after encrypting password, by committing to DB
        else:
            key = Fernet.generate_key()
            fernet = Fernet(key)
            hashed_pass = fernet.encrypt(passwd.encode())
            db.execute("INSERT INTO accounts ("
                       "account, "
                       "first_name, "
                       "last_name, "
                       "hashed_password, "
                       "key_verification) "
                       "VALUES (?, ?, ?, ?, ?)", (acc, first, last, hashed_pass, key,))

            db.commit()

            # Return to user and disable Register button in background window
            l_back_window.configure(text="Registered Successfully")
            b_reg.configure(state="disabled")
            parent.destroy()

    # Submit and Cancel buttons
    ttk.Button(f_new, text="Register", command=register).grid(column=0, row=0, padx=5, pady=(10, 0))
    ttk.Button(f_new, text=" Cancel", command=w_reg.destroy).grid(column=1, row=0, padx=5, pady=(10, 0))


if __name__ == "__main__":
    root_window = Tk()
    main(root_window)

    root_window.mainloop()
