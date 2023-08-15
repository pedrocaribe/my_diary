import os.path
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import date
from cryptography.fernet import Fernet
import sqlite3
import tkinter.scrolledtext
import re
import requests
from fpdf import FPDF
import json
from PIL import Image, ImageTk


class User:
    def __init__(self, root: Tk, user):
        self.db = sqlite3.connect("diary.db")
        db_id, username, first_name, last_name, hashed_pass, key = self.db.execute("SELECT * "
                                                                                   "FROM accounts "
                                                                                   "WHERE account = ?", (user,)
                                                                                   ).fetchone()
        self.id = db_id
        self.username = username
        self.f_name = first_name
        self.l_name = last_name
        self.hashed_passwd = hashed_pass
        self.hash_key = key
        self.root = root

    def main_window(self):
        # Force main window to open in center of screen
        root = self.root
        acc = self.username
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
        db = self.db
        db.execute("CREATE TABLE IF NOT EXISTS entries ("
                   "account_id INTEGER, "
                   "entry_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                   "entry TEXT, "
                   "date DATE);")

        # Create Window Menu
        menubar = Menu(root)
        root.config(menu=menubar)

        # img = PhotoImage(file="password.png")
        img = Image.open("password.png").resize((10, 10))
        img = ImageTk.PhotoImage(img)

        m_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=m_menu, underline=0)
        m_menu.add_command(label="Change Password", command=lambda: self.change_info("pass"), image=img, compound='left')
        m_menu.add_command(label="Change E-mail", command=lambda: self.change_info("email"))

        m_help = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=m_help, underline=0)
        m_help.add_command(label="About", command=lambda: about(root))

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
                           command=lambda: self.multi(cal, l_date, lst_entry, db, acc, e_c1))
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
        b_pdf = ttk.Button(f_c3, text="Save to PDF", command=lambda: self.multi.print_save("save", e_c1, cal), width=20)
        b_pdf.grid(column=3, row=1)

        # Calling External function to print
        b_print = ttk.Button(f_c3, text="Print", command=lambda: self.print_save("print", e_c1, cal), width=20)
        b_print.grid(column=3, row=2)

        b_email = ttk.Button(f_c3, text="Send as E-mail", command=lambda: self.print_save("email", e_c1, cal), width=20)
        b_email.grid(column=3, row=3)

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

    def change_info(self, command: str):
        acc = self.username
        db = self.db
        w_popup = Toplevel()
        w_popup.resizable(False, False)
        w_popup.grab_set()
        w_popup.attributes("-topmost", "true")
        w_popup.configure(pady=10, padx=10)
        f_popup = ttk.Frame(w_popup)
        f_popup.grid(column=0, row=0, sticky="nsew")
        l_title = Label(f_popup, text="", anchor="center")
        l_title.grid(column=0, row=0, columnspan=2)
        if command == "pass":
            l_title.configure(text="Change Password")
            curr_pass = StringVar()
            new_pass = StringVar()
            conf_pass = StringVar()

            Label(f_popup, text="Current Password:").grid(column=0, row=1)
            Label(f_popup, text="New Password:").grid(column=0, row=2)
            Label(f_popup, text="Confirm Password:").grid(column=0, row=3)
            l_return = Label(f_popup, text="", anchor="center")
            l_return.grid(column=0, row=5, columnspan=2)

            Entry(f_popup, textvariable=curr_pass, show="*", width=30).grid(column=1, row=1)
            Entry(f_popup, textvariable=new_pass, show="*", width=30).grid(column=1, row=2)
            Entry(f_popup, textvariable=conf_pass, show="*", width=30).grid(column=1, row=3)

            def changepass(w, bt_s, bt_c):
                o_pass = curr_pass.get()  # Old password
                n_pass = new_pass.get()  # New password
                c_pass = conf_pass.get()  # Confirmation password
                check_pass = db.execute("SELECT accounts.hashed_password, accounts.key_verification "
                                        "FROM accounts "
                                        "WHERE account = ?", (acc,)).fetchone()
                h_pass = check_pass[0]
                key = check_pass[1]

                fernet = Fernet(key)
                u_pass = fernet.decrypt(h_pass).decode()

                if o_pass != u_pass:
                    l_return.configure(text="Password inserted does Not match current password")
                elif n_pass == o_pass:
                    l_return.configure(text="New password can Not be the same as the current password")
                elif n_pass != c_pass:
                    l_return.configure(text="Passwords do Not match")
                else:
                    nh_pass = fernet.encrypt(n_pass.encode())
                    db.execute("UPDATE accounts SET hashed_password = ? WHERE account = ?", (nh_pass, acc,))
                    db.commit()
                    l_return.configure(text="Password changed Successfully!")
                    bt_s.destroy()
                    bt_c.destroy()
                    b_temp = ttk.Button(w, text="Close", command=w.destroy, width=20)
                    b_temp.grid(column=0, row=4, padx=5, pady=(10, 0), columnspan=2)

            b_cancel = ttk.Button(f_popup, text="Cancel", command=w_popup.destroy, width=20)
            b_cancel.grid(column=1, row=4, padx=5, pady=(10, 0))
            b_submit = ttk.Button(f_popup, text="Submit", command=lambda: changepass(w_popup, b_submit, b_cancel), width=20)
            b_submit.grid(column=0, row=4, padx=5, pady=(10, 0))


        elif command == "email":
            ...

    def garbage_collector(self):

        # sqlite3 supports REGEXP but does not have it included
        # In order to use it you have to user parametrized SQL
        # Docs: https://www.sqlite.org/c3ref/create_function.html
        def regexp(expr, item):
            reg = re.compile(expr)
            return reg.search(item) is not None

        db = self.db
        db.create_function("REGEXP", 2, regexp)
        db.execute("DELETE FROM entries WHERE entry REGEXP ?", ['^[ \r\n]*$'])
        db.commit()

    def multi(self, cal: Calendar, r_field: Label, lb: Listbox, db, user: str, text_box: Text):
        # Variable assignment for readability
        root = self.root
        selected_date = cal.get_date()
        r_field.config(text=f"Selected Date is: {selected_date}")
        acc = user

        # Clear entries from Listbox and allow single selection
        lb.delete(0, tkinter.END)
        lb.config(selectmode=SINGLE)

        # Retrieve entries from DB for the specified user and date
        entries = db.execute("SELECT entries.entry_id, entries.entry, entries.date "
                             "FROM entries "
                             "JOIN accounts "
                             "ON accounts.id = entries.account_id "
                             "WHERE accounts.account = ? "
                             "AND entries.date = ?", (acc, selected_date,)).fetchall()

        # Add entries to Listbox and create a list of entries
        entries_list = []
        for count, entry in list(enumerate(entries)):
            entry_temp = Entries(count, entry[0], entry[1], entry[2])
            entries_list.append(entry_temp)
            if entry_temp.entry != "":
                lb.insert(entry_temp.count_id, entry_temp.entry)

        def selected():
            sel_index = lb.curselection()[0]  # User selected entry's index

            # Find object in list that has attribute count_id == selected index
            sel_entry = next(x for x in entries_list if x.count_id == sel_index)
            text = text_box.get("1.0", END)  # Fetch text within text box

            # Check if there is text within text box, in order to allow user
            # to save any changes done to the entry selected
            if len(text) > 1:

                # Create popup window and "disable" actions to window in background
                popup = Toplevel()
                popup.grab_set()
                popup.attributes("-topmost", "true")
                popup.resizable(False, False)
                f_popup = ttk.Frame(popup, padding=(3, 3, 12, 12))
                f_popup.grid(column=0, row=0, sticky="nsew")
                l_popup = Label(f_popup, text="All changes will be lost.\n"
                                              "Would you like to save the current entry?", anchor="center")
                l_popup.grid(column=0, row=0, sticky="nsew", columnspan=2)

                def yes():
                    save_clear("save", text_box, db, acc, index=sel_entry.entry_id)
                    popup.destroy()

                b_yes = ttk.Button(f_popup, text="Yes", command=yes, width=10)
                b_yes.grid(column=0, row=1)

                def no():
                    save_clear("clear", text_box, db, acc)
                    popup.destroy()
                    text_box.insert("1.0", sel_entry.entry)

                b_no = ttk.Button(f_popup, text="No", command=no, width=10)
                b_no.grid(column=1, row=1)
                root.eval(f'tk::PlaceWindow {str(popup)} center')
            else:
                text_box.delete("1.0", END)
                text_box.insert("1.0", sel_entry.entry)

        lb.bind('<<ListboxSelect>>', selected)

    def print_save(self, command: str, entry: Text, cal: Calendar):
        text = entry.get("1.0", END)
        text_date = cal.get_date()
        if command == "save":
            pdf = FPDF(orientation="portrait", format="A4")
            pdf.add_page()
            pdf.set_y(0)

            pdf.output(f"exported_diary_{text_date}.pdf")
        elif command == "print":
            ...
        else:
            raise ValueError("Invalid Command")

    def __str__(self):
        return [self.id, self.username, self.f_name, self.l_name]


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


def about(root: Tk):
    w_about = Toplevel()
    w_about.resizable(False, False)
    w_about.title("About My Diary")
    f_about = ttk.Frame(w_about, padding=(3, 3, 12, 12))
    f_about.grid(column=0, row=0, sticky="nsew")

    l_title = Label(f_about, text="My Diary", font="Arial 12 bold", anchor="center")
    l_title.grid(column=0, row=0, sticky="nsew")
    about_desc = """
    Author: Pedro Caribé

    Created as final project
    for CS50p Course.
    Year: 2023

    Version: 1.00
    """
    l_about = Label(f_about, text=about_desc)
    l_about.grid(column=0, row=1, sticky="nsew")

    # Force TopLevel to open in center of screen
    root.eval(f'tk::PlaceWindow {str(w_about)} center')




def save_clear(command: str, entry: Text, db, account: str, r_save: Label = None, index: int = None):
    if command == "save":
        text = entry.get("1.0", END)
        acc_id = db.execute("SELECT id FROM accounts WHERE account = ?", (account,)).fetchone()
        try:
            if index:
                db.execute("UPDATE entries SET entry = ? WHERE entry_id = ? AND account_id = ?", (text, index, acc_id))
            else:
                db.execute("INSERT INTO entries (account_id, entry, date) VALUES (?, ?, ?)",
                           (acc_id[0], text, date.today(),))
            db.commit()
        except Exception as e:
            r_save.config(text=f"Failed, contact Administrator.{e}")
        else:
            r_save.config(text="Entry Saved.")
            save_clear("clear", entry, db, account, r_save)

    elif command == "clear":
        entry.delete("1.0", END)

    else:
        raise ValueError("Invalid Command")


def motivate():
    url = "https://complimentr.com/api"
    return (json.loads(requests.get(url).text))['compliment'].capitalize()
