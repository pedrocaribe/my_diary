import tkinter
import tkinter.scrolledtext
from project_utils import *
import sqlite3

from project_utils import DB_NAME


def main(root):
    # First screen to protect access by password
    # password_protection(root)

    # Testing main window
    garbage_collector()
    main_window(root, "teste")


def main_window(root, acc=None):
    # Force main window to open in center of screen
    root.wm_attributes('-alpha', 0)  # Hide window to avoid flicking screen while calculating center

    # Window size
    w = 1024
    h = 768

    root.geometry(f"{w}x{h}")  # Fixed window size
    root.title("My Diary")
    root.resizable(False, False)
    screen_w = root.winfo_screenwidth()  # Width of screen
    screen_h = root.winfo_screenheight()  # Height of screen

    # Calculate X and Y coordinates for screen positioning
    x = (screen_w / 2) - (w / 2)
    y = (screen_h / 2) - (h / 2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    root.wm_attributes('-alpha', 1)  # Show window after calculations

    # Establish connection to DB
    db = sqlite3.connect(DB_NAME)
    db.execute("CREATE TABLE IF NOT EXISTS entries ("
               "account_id INTEGER, "
               "entry_id INTEGER PRIMARY KEY AUTOINCREMENT, "
               "entry TEXT, "
               "date DATE);")

    # Create Window Menu
    menubar = Menu(root)
    root.config(menu=menubar)
    m_help = Menu(menubar, tearoff=0)
    m_help.add_command(label="About", command=lambda: about(root))
    menubar.add_cascade(label="Help", menu=m_help, underline=0)

    root.config(menu=menubar)

    # Create main window frame
    f_main = ttk.Frame(root, padding=(3, 3, 12, 12), borderwidth=2)
    f_main.grid(column=0, row=0, sticky="nsew")

    # Row 0 -> Title
    title = Label(f_main, text="My Diary", anchor="center", pady=3, font=("Arial", 18), relief="sunken")
    title.grid(column=0, row=0, sticky="nsew", columnspan=4)

    # Column 0 -> Left
    c0_title = Label(f_main, text=f"Entries for the Date:", anchor="center", font=("Arial", 10))
    c0_title.grid(column=0, row=1, sticky="nsew", padx=(10, 10))

    # Instantiating Listbox with fixed size
    lst_entry = Listbox(f_main, height=20, width=41)
    lst_entry.grid(column=0, row=2, pady=10, padx=10)

    # Instantiating Calendar, default date to today's date
    # Date pattern used to match Date pattern from DB
    today_y, today_m, today_d = map(int, str(date.today()).split("-"))
    cal = Calendar(f_main, selectmode="day", year=today_y, month=today_m, day=today_d, date_pattern='y-mm-dd')
    cal.grid(column=0, row=3, pady=10, padx=10)

    # Setting empty space to return confirmation string from function
    l_date = Label(f_main, text="")
    l_date.grid(column=0, row=5)

    # Column 1 -> Middle
    l_title = Label(f_main, text="My thoughts:", anchor="center", font=("Arial", 10))
    l_title.grid(column=1, row=1, padx=10, pady=10, sticky="nsew", columnspan=2)

    # Instantiating Text Box (entry_column1) with Scrollbar, fixed size
    e_c1 = tkinter.scrolledtext.ScrolledText(f_main, wrap=tkinter.WORD, width=70, height=20)
    e_c1.grid(column=1, row=2, padx=2, pady=10, sticky="nsew", rowspan=2, columnspan=2)

    # Calling external function to update calendar and retrieve entries from DB
    b_cal = ttk.Button(f_main, text="Get Entries", command=lambda: multi(root, cal, l_date, lst_entry, db, acc, e_c1))
    b_cal.grid(column=0, row=4)

    # Setting empty space to return confirmation string for save
    r_save = Label(f_main, text="")
    r_save.grid(column=1, row=4, columnspan=2)

    b_save = ttk.Button(f_main, text="Save", command=lambda: save_clear("save", e_c1, db, acc, r_save), width=20)
    b_save.grid(column=1, row=4)

    # Column 2
    b_clear = ttk.Button(f_main, text="Clear", command=lambda: save_clear("clear", e_c1, db, acc, r_save), width=20)
    b_clear.grid(column=2, row=4)

    # Column 3
    # Create new frame
    f_c3 = Frame(f_main, padx=3, pady=10)
    f_c3.grid(column=3, row=2, sticky="nsew")

    # Calling External function to save
    b_pdf = ttk.Button(f_c3, text="Save to PDF", command=lambda: print_save("save", entry), width=20)
    b_pdf.grid(column=3, row=1)

    # Calling External function to print
    b_print = ttk.Button(f_c3, text="Print", command=lambda: print_save("print", entry), width=20)
    b_print.grid(column=3, row=2)

    # Row 6 - Footer
    # Footer Frame
    f_footer = ttk.Frame(f_main, padding=(3, 3, 12, 12), borderwidth=3, relief="sunken")
    f_footer.grid(column=0, row=6, sticky="nsew", columnspan=4)

    f_footer.columnconfigure(0, weight=1)  # Set footer column 0 to fill all frame width

    # Footer Labels
    l_footer = Label(f_footer, text="Phrase of the day:", anchor="center")
    l_footer.grid(column=0, row=0, sticky="nsew")
    l_phrase = Label(f_footer, text=str(motivate()), anchor="center", font=("Arial", 16))  # External function
    l_phrase.grid(column=0, row=1, sticky="nsew", pady=5)


def password_protection(root):
    root.withdraw()  # Hide main window until user is authenticated

    # Create new toplevel window
    w_pass = Toplevel()

    w_pass.resizable(False, False)
    w_pass.title("My Diary - Login")

    # Create new frame
    f_pass = ttk.Frame(w_pass, padding=(3, 3, 12, 12))
    f_pass.grid(column=0, row=0, sticky="nsew")

    l_title = ttk.Label(f_pass, text="Please enter your credentials", anchor="center")
    l_title.grid(column=0, row=0, columnspan=3, sticky="nsew")

    l_acc = ttk.Label(f_pass, text="Account:")
    l_acc.grid(column=0, row=1, sticky=W, padx=5)

    l_pass = ttk.Label(f_pass, text="Password:")
    l_pass.grid(column=0, row=2, sticky=W, padx=5)

    acc_str = StringVar()
    pw_str = StringVar()

    e_acc = ttk.Entry(f_pass, textvariable=acc_str)
    e_acc.grid(column=1, row=1, columnspan=2, sticky="nsew")

    e_pw = ttk.Entry(f_pass, textvariable=pw_str, show='*')
    e_pw.grid(column=1, row=2, columnspan=2, sticky="nsew")

    b_submit = ttk.Button(f_pass, text="Submit", command=lambda: validate_login(w_pass, acc_str, pw_str, f_pass, root))
    b_submit.grid(column=1, row=3, pady=(10, 0))

    b_close = ttk.Button(f_pass, text="Close", command=root.destroy)
    b_close.grid(column=2, row=3, pady=(10, 0))

    e_acc.focus()


def validate_login(w_tl: Toplevel, acc: StringVar, passwd: StringVar, parent: Frame, w_root: Tk):
    acc = acc.get()
    passwd = passwd.get()

    # Establish connection to DB and create table if it is first use
    db = sqlite3.connect(DB_NAME)
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS accounts ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "account TEXT, "
                "first_name TEXT, "
                "last_name TEXT, "
                "hashed_password BLOB, "
                "key_verification BLOB)")

    # Check if user provided already exists in DB
    check = cur.execute("SELECT * FROM accounts WHERE account = ?", (acc,)).fetchone()

    # Create return label for posterior checks
    l_return = ttk.Label(parent, text="", anchor="center")
    l_return.grid(column=0, row=4, columnspan=4, sticky="nsew")

    # Login Checks
    if not acc:
        l_return.configure(text="Account cannot be blank")  # If user doesn't insert account name
    elif not check:
        l_return.configure(text="Invalid account, please register")  # If account not registered
        b_register = ttk.Button(parent, text="Register", command=lambda: create_login(db, l_return, b_register))
        b_register.grid(column=0, row=3, pady=(10, 0))

    # If user is already registered, decrypt password provided with stored hash key and confirm login information
    else:
        hashed_pass = check[4]
        key = check[5]
        fernet = Fernet(key)
        unhashed_pass = fernet.decrypt(hashed_pass).decode()

        # Compare password provided with decrypted password
        if unhashed_pass == passwd:
            l_return.configure(text="Login Successful")

            # If successful login, destroy toplevel window and show main
            w_tl.destroy()
            main_window(w_root, acc)
            w_root.deiconify()
        else:
            l_return.configure(text="Incorrect Password")


def create_login(db, l_back_window: Label, b_reg: ttk.Button):

    # Create new window for registration fields
    w_reg = Toplevel()
    w_reg.grab_set()  # Disable windows in background
    w_reg.attributes("-topmost", "true")
    w_reg.configure(pady=10, padx=10)
    w_reg.resizable(False, False)

    # Create fields and variables for fetching data inputted from user
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

        # If all checks passed, register user after encrypting password by committing to DB
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
