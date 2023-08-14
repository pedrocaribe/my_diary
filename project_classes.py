from tkinter import *

class User:
    def __init__(self, username, first_name, last_name, hashed_pass, key):
        self.username = username
        self.f_name = first_name
        self.l_name = last_name
        self.hashed_passwd = hashed_pass
        self.hash_key = key

    def main_window(self, root: Tk, acc=None):
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
        m_menu = Menu(menubar, tearoff=0)
        m_menu.add_command(label="Change Password", command=lambda: change_info("pass", root, db, acc))
        m_menu.add_command(label="Change E-mail", command=lambda: change_info("email", root, db, acc))
        menubar.add_cascade(label="Menu", menu=m_menu, underline=0)
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
        b_cal = ttk.Button(f_main, text="Get Entries",
                           command=lambda: multi(root, cal, l_date, lst_entry, db, acc, e_c1))
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


class Entries:
    def __init__(self, n, e_id, e, d):
        self.count_id = n
        self.entry_id = e_id
        self.entry = e
        self.date = d


class ToPrint:
    def __init__(self, db_e):
        self.owner = db_e[0]
        self.entry_id = db_e[1]
        self.entry = db_e[2]
        self.date = db_e[3]

