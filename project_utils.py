import tkinter.messagebox

from fpdf import FPDF
from tkinter import *
from tkinter import ttk
from tkcalendar import Calendar
import sqlite3
from datetime import date, datetime
from project_clases import ToPrint, Entries
import json
import requests
import asyncio
from cryptography.fernet import Fernet

DB_NAME = "diary.db"


def about(root):
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


def print_save(command, db_entry):

    entry = ToPrint(db_entry)
    if command == "save":
        pdf = FPDF(orientation="portrait", format="A4")
        pdf.add_page()
        pdf.set_y(0)

        pdf.output(f"exported_diary_{entry.date}.pdf")
    elif command == "print":
        ...
    else:
        raise ValueError("Invalid Command")


def multi(root: Tk, cal: Calendar, r_date: Label, lb: Listbox, db, acc: str, text_box: Text):

    # Variable assignment for readability
    selected_date = cal.get_date()
    r_date.config(text=f"Selected Date is: {selected_date}")

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

    # Add entries to Listbox and create a dict of entries
    entries_list = []
    for count, entry in list(enumerate(entries)):
        entry_temp = Entries(count, entry[0], entry[1], entry[2])
        entries_list.append(entry_temp)
        lb.insert(entry_temp.count_id, entry_temp.entry)

    def selected(event):
        sel_index = lb.curselection()  # Selected index
        # Find object in list that has attribute count_id == selected index
        sel_entry = next(x for x in entries_list if x.count_id == sel_index[0])
        text = text_box.get("1.0", END)  # Actual text within text box
        if len(text) > 1:
            print(type(text))
            print(text)
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


