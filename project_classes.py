from tkinter import *
from tkinter import filedialog, messagebox, ttk, scrolledtext
from tkcalendar import Calendar
from cryptography.fernet import Fernet
from datetime import date
from fpdf import FPDF
from PIL import Image, ImageTk

import win32api
import win32print
import sqlite3
import re
import requests
import json
import webbrowser


class User:
    """User class

    User class to be initialized when user logs in, contains several attributes.

    Attributes:
        id: A string containing account id under DB.
        username: A string containing username.
        f_name: A string containing user's first name.
        l_name: A string containing user's last name.
        hashed_passwd: A string containing hashed password.
        hash_key: A string containing hash key.
        root: The root window in which main window will be confirmed.
        current_selection_entry: A string containing the old entry's text to
            be compared with actual entry when changed
        current_selection_id: An integer representing old the entry's id to
         be compared with actual entry's id when changed
    """
    def __init__(self, root: Tk, user):
        """Initializes the user based on successful login.

        Args:
            root: Root Tk window in which to display the main window frame.
            user: username provided by user after successfully logging in.
        """
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
        self.current_selection_entry = self.current_selection_id = None

    def main_window(self):
        """Application's main window

        Window used to display all Widgets after successfully logging in.

        Returns:
             This method does Not return anything.
        """

        # Force main window to open in center of screen
        root = self.root
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

        # Create table for accounts
        db = self.db
        db.execute("CREATE TABLE IF NOT EXISTS entries ("
                   "account_id INTEGER, "
                   "entry_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                   "entry TEXT, "
                   "date DATE);")

        # Create Window Menu
        menubar = Menu(root)
        root.config(menu=menubar)

        # Create menu and add cascade for account options
        m_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=m_menu, underline=0)

        # Icons for m_menu commands
        m_menu.pass_icon = icon("icon_pass.png")
        m_menu.email_icon = icon("icon_email.png")

        # Add commands to m_menu menu
        m_menu.add_command(label="Change Password",
                           command=lambda: self.change_info("pass"), image=m_menu.pass_icon, compound="left")
        m_menu.add_command(label="Change E-mail",
                           command=lambda: self.change_info("email"), image=m_menu.email_icon, compound="left")

        # Create menu and add cascade for help options
        m_help = Menu(menubar, tearoff=0)
        m_contact = Menu(tearoff=0)  # No parent/master

        # Add properties to store fixed values
        email = "pho.caribe@gmail.com"
        linkedin = "https://www.linkedin.com/in/pedro-caribe/"

        # Icon for m_contact definitions
        m_contact.email_icon = icon("icon_email_contact.png")
        m_contact.linkedin_icon = icon("icon_linkedin.png")

        menubar.add_cascade(label="Help", menu=m_help, underline=0)

        # Add submenus
        m_help.add_cascade(label="Contact", menu=m_contact)
        m_contact.add_command(
            label="E-mail",
            command=lambda: webbrowser.open(
                                    f"mailto:?to={email}&subject=Feedback on My Diary", new=1),
            image=m_contact.email_icon, compound="left"
        )
        m_contact.add_command(
            label="LinkedIn",
            command=lambda: webbrowser.open(linkedin),
            image=m_contact.linkedin_icon, compound="left"
        )

        m_help.add_command(label="About", command=lambda: about(root))

        # Create main window frame
        f_main = ttk.Frame(root, padding=(3, 3, 12, 12), borderwidth=2)
        f_main.grid(column=0, row=0, sticky="nsew")

        # Row 0 -> Title
        title = Label(f_main, text="My Diary", anchor="center", pady=3, font=("Arial", 18), relief="sunken")
        title.grid(column=0, row=0, sticky="nsew", columnspan=5)

        ####################
        # Column 0 -> Left #
        ####################

        c0_title = Label(f_main, text=f"Entries for the Date:", anchor="center", font=("Arial", 10))
        c0_title.grid(column=0, row=1, sticky="nsew", padx=(10, 10))

        # Instantiating Listbox with fixed size, single selection, not exporting selection to avoid bugs
        lst_entry = Listbox(f_main, height=20, width=41, selectmode=SINGLE, exportselection=False)
        lst_entry.grid(column=0, row=2, pady=10, padx=10)

        # Instantiating Calendar, default date to today's date
        # Date pattern used to match Date pattern from DB
        today_y, today_m, today_d = map(int, str(date.today()).split("-"))
        cal = Calendar(f_main, selectmode="day", year=today_y, month=today_m, day=today_d, date_pattern='y-mm-dd')
        cal.grid(column=0, row=3, pady=10, padx=10)

        # Setting empty space to return confirmation string from function
        l_date = Label(f_main, text="")
        l_date.grid(column=0, row=5)

        # Calling method to update calendar and retrieve entries from DB
        b_cal = ttk.Button(f_main, text="Get Entries", command=lambda: self.get_entries(cal, l_date, lst_entry, e_c1))
        b_cal.grid(column=0, row=4)
        createtooltip(b_cal, text="Get entries for selected date")

        ############
        # Column 1 #
        ############

        l_title = Label(f_main, text="My thoughts:", anchor="center", font=("Arial", 10))
        l_title.grid(column=1, row=1, padx=10, pady=10, sticky="nsew", columnspan=3)

        # Instantiating Text Box (entry_column1) with Scrollbar, fixed size
        e_c1 = scrolledtext.ScrolledText(f_main, wrap=WORD, width=70, height=20)
        e_c1.grid(column=1, row=2, padx=2, pady=10, sticky="nsew", rowspan=2, columnspan=3)

        # Button to Clear and Create new Entry
        b_new_entry = ttk.Button(f_main, text="New", command=lambda: self.new_entry(e_c1))
        b_new_entry.grid(column=1, row=4)
        createtooltip(b_new_entry, text="Clears box and creates new entry")

        ############
        # Column 2 #
        ############

        # Button to Save current entry
        b_save = ttk.Button(f_main, text="Save", command=lambda: self.save_entry(
            e_c1, None if not self.current_selection_id else self.current_selection_id), width=20)
        b_save.grid(column=2, row=4)
        createtooltip(b_save, text="Saves box content")

        ############
        # Column 3 #
        ############

        # Button to clear text box
        b_clear = ttk.Button(f_main, text="Clear", command=lambda: self.clear_entry(e_c1), width=20)
        b_clear.grid(column=3, row=4)
        createtooltip(b_clear, text="Clears box and keeps editing current entry")

        #####################
        # Column 4 -> Right #
        #####################

        # Create new frame
        f_c3 = Frame(f_main, padx=3, pady=10)
        f_c3.grid(column=4, row=2, sticky="nsew")

        # Calling External function to save
        b_pdf = ttk.Button(f_c3, text="Save to PDF", command=lambda: self.print_pdf("save", e_c1, cal), width=20)
        b_pdf.grid(column=4, row=1)

        # Calling External function to print
        b_print = ttk.Button(f_c3, text="Print", command=lambda: self.print_pdf("print", e_c1, cal), width=20)
        b_print.grid(column=4, row=2)

        b_email = ttk.Button(f_c3, text="Send as E-mail", command=lambda: self.print_pdf("email", e_c1, cal), width=20)
        b_email.grid(column=4, row=3)

        ##################
        # Row 6 - Footer #
        ##################

        # Footer Frame
        f_footer = ttk.Frame(f_main, padding=(3, 3, 12, 12), borderwidth=3, relief="sunken")
        f_footer.grid(column=0, row=6, sticky="nsew", columnspan=5)

        f_footer.columnconfigure(0, weight=1)  # Set footer column 0 to fill all frame width

        # Footer Labels
        l_footer = Label(f_footer, text="Phrase of the day:", anchor="center")
        l_footer.grid(column=0, row=0, sticky="nsew")
        l_phrase = Label(f_footer, text=str(motivate()), anchor="center", font=("Arial", 16))  # External function
        l_phrase.grid(column=0, row=1, sticky="nsew", pady=5)

    def new_entry(self, text_box: Text):
        """Clear box and begin a new entry.

        Method used to clear the actual entry within the scrolledtext Text box,
        without maintaining the index of the actual entry.

        Args:
            text_box: Text box used to create the new entry.

        Returns:
            This method does Not return anything.
        """

        res = messagebox.askyesno("Confirmation", "Are you sure you would like to create a new entry?\n"
                                  "All current text within the text box will be lost!")
        if res:
            self.current_selection_entry = None
            self.current_selection_id = None
            text_box.delete("1.0", END)

    def clear_entry(self, box: Text):
        """Clear box and keep entry index

        Method used to clear the actual entry within the scrolledtext Text box,
        maintaining the entry's index, and giving the user the option to save a
        new value to this entry.

        Args:
            box: Text box in which text is being editted.

        Returns:
            This method does Not return anything.
        """
        box.delete("1.0", END)

    def change_info(self, command: str):

        # Variable assignment for easier understanding
        acc = self.username
        db = self.db

        # Create popup and set attributes
        w_popup = Toplevel()
        w_popup.resizable(False, False)  # Not resizable
        w_popup.grab_set()  # Disable actions to windows in background
        w_popup.attributes("-topmost", "true")  # Focus when created
        w_popup.configure(pady=10, padx=10)
        f_popup = ttk.Frame(w_popup)
        f_popup.grid(column=0, row=0, sticky="nsew")

        # Varied actions depending on option selected
        if command == "pass":
            # Title
            Label(f_popup, text="Change Password", anchor="center").grid(column=0, row=0, columnspan=2, pady=(0, 5))

            # Field Labels
            Label(f_popup, text="Current Password:").grid(column=0, row=1)
            Label(f_popup, text="New Password:").grid(column=0, row=2)
            Label(f_popup, text="Confirm Password:").grid(column=0, row=3)

            # Information fetching
            curr_pass = StringVar()
            new_pass = StringVar()
            conf_pass = StringVar()

            Entry(f_popup, textvariable=curr_pass, show="*", width=30).grid(column=1, row=1)
            Entry(f_popup, textvariable=new_pass, show="*", width=30).grid(column=1, row=2)
            Entry(f_popup, textvariable=conf_pass, show="*", width=30).grid(column=1, row=3)

            def changepass():
                o_pass = curr_pass.get()  # Old password
                n_pass = new_pass.get()  # New password
                c_pass = conf_pass.get()  # Confirmation password

                # Fetch Hashed Pass and Key from DB
                h_pass, key = db.execute("SELECT accounts.hashed_password, accounts.key_verification "
                                         "FROM accounts "
                                         "WHERE account = ?", (acc,)).fetchone()

                # Decrypt password provided
                fernet = Fernet(key)
                u_pass = fernet.decrypt(h_pass).decode()

                # User mistyping scenarios
                if o_pass != u_pass:
                    messagebox.showinfo("Info", "Password inserted does Not match current password")
                elif n_pass == o_pass:
                    messagebox.showinfo("Info", "New password can Not be the same as the current password")
                elif n_pass != c_pass:
                    messagebox.showinfo("Info", "Passwords do Not match")
                else:
                    nh_pass = fernet.encrypt(n_pass.encode())  # Encrypt new password
                    db.execute("UPDATE accounts SET hashed_password = ? WHERE account = ?", (nh_pass, acc,))
                    db.commit()
                    messagebox.showinfo("Success", "Password changed successfully")
                    w_popup.destroy()

            # Create buttons to submit or `cancel` changes
            b_cancel = ttk.Button(f_popup, text="Cancel", command=w_popup.destroy, width=20)
            b_cancel.grid(column=1, row=4, padx=5, pady=(10, 0))
            b_submit = ttk.Button(f_popup, text="Submit", command=changepass, width=20)
            b_submit.grid(column=0, row=4, padx=5, pady=(10, 0))

        # Change e-mail << STILL TO IMPLEMENT >>
        elif command == "email":
            w_popup.destroy()
            messagebox.showinfo("Unable to proceed", "This feature is still to be implemented.")

    # Garbage collector, to delete any empty entries from DB
    def garbage_collector(self):

        """
        sqlite3 supports REGEXP but does not have it included
        In order to use it, you have to use parametrized SQL
        Docs: https://www.sqlite.org/c3ref/create_function.html
        """

        def regexp(expr, item):
            reg = re.compile(expr)
            return reg.search(item) is not None

        db = self.db
        db.create_function("REGEXP", 2, regexp)
        try:
            db.execute("DELETE FROM entries WHERE entry REGEXP ?", ['^[ \r\n]*$'])
        except sqlite3.OperationalError:
            pass
        else:
            db.commit()

    # Method to populate listbox and entry box
    def get_entries(self, cal: Calendar, r_field: Label, lb: Listbox, text_box: Text):
        # Variable assignment for readability
        selected_date = cal.get_date()
        r_field.config(text=f"Selected Date is: {selected_date}")

        entries_list = self.fill_list(lb, selected_date)

        def selected(event):

            sel_index = lb.curselection()[0]  # User selected entry's index
            sel_entry = next(_ for _ in entries_list if _.count_id == sel_index)
            sel_entry.entry = re.sub(r"\n$", "", sel_entry.entry)
            text = text_box.get("1.0", "end-1c")

            if len(text) > 1:
                if text != self.current_selection_entry:
                    res = messagebox.askyesno("Save Entry",
                                              "Would you like to save the current entry?\n"
                                              "All changes will be lost!")
                    if res:
                        self.save_entry(text_box, sel_entry.entry_id)
                        self.fill_list(lb, selected_date)
                    else:
                        text_box.delete("1.0", END)
                        text_box.insert("1.0", sel_entry.entry)
                        self.current_selection_id = sel_entry.entry_id
                        self.current_selection_entry = sel_entry.entry
                else:
                    text_box.delete("1.0", END)
                    text_box.insert("1.0", sel_entry.entry)
                    self.current_selection_id = sel_entry.entry_id
                    self.current_selection_entry = sel_entry.entry

            else:
                self.current_selection_entry = sel_entry.entry
                self.current_selection_id = sel_entry.entry_id
                text_box.insert("1.0", sel_entry.entry)

        lb.bind('<<ListboxSelect>>', selected)

    def print_pdf(self, command: str, entry: Text, cal: Calendar):

        class PDF(FPDF):
            def header(self):
                # Setting font: helvetica bold 15
                self.set_font("helvetica", "B", 15)
                # Moving cursor to the right
                self.cell(80)
                # Printing title
                self.cell(30, 10, "My Diary", align="C")
                # Performing a line break
                self.ln(20)

            def footer(self):
                # Position cursor at 1.5cm from bottom
                self.set_y(-15)
                # Setting font: helvetica italic 8
                self.set_font("helvetica", "I", 8)
                # Printing author credits
                self.cell(0, 10, f"My Diary - Your thoughts, safe!", align="C")

            def entry_title(self, entry_date: str):
                # Setting font: helvetica 12
                self.set_font("helvetica", "", 12)
                # Setting background color
                self.set_fill_color(200, 220, 255)
                # Printing entry date
                self.cell(0, 6, f"Entry Date: {entry_date}", new_x="LMARGIN", new_y="NEXT", align="L", fill=True)
                # Performing a line break
                self.ln(4)

            def entry_body(self, txt: str):
                # Setting font: Times 12
                self.set_font("Times", size=12)
                # Printing justified text
                self.multi_cell(0, 5, txt)
                # Performing a line break
                self.ln()
                # Final mention in italics
                self.set_font(style="I")
                self.cell(0, 5, "(End of Entry)")

            def print_entry(self, entry_date, txt):
                self.add_page()
                self.entry_title(entry_date)
                self.entry_body(txt)

        text = entry.get("1.0", 'end-1c')
        text_date = cal.get_date()
        pdf = PDF(orientation="portrait", format="A4")
        pdf.set_margin(10)
        pdf.set_author(f"{self.username}")
        pdf.set_title("My Diary")
        pdf.print_entry(text_date, text)

        output_name = f"exported_diary_{text_date}.pdf"

        if command == "save":
            if len(text) > 1:
                try:
                    pdf.output(
                        filedialog.asksaveasfilename(
                            initialdir="/",
                            initialfile=output_name,
                            title="Select Folder",
                            filetypes=(("PDF File", "*.pdf"), ("all files", "*.*")),
                            defaultextension=".pdf"
                        )
                    )
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            else:
                messagebox.showinfo("Info", "There is nothing to be saved")

        elif command == "print":
            # Check if there is text to be printed
            if len(text) > 1:
                # Create text box to confirm action (True|False)
                res = messagebox.askyesno("Confirmation", "Would you like to print the current entry?")
                if res:
                    # Create variable to flag exception error
                    er = False
                    # Generate PDF and Print
                    try:
                        pdf.output(
                            win32api.ShellExecute(
                                0,
                                "print",
                                output_name,
                                '"%s"' % win32print.GetDefaultPrinter(),
                                ".",
                                0
                            ))
                    # Catch exceptions
                    # If AttributeError, ignore
                    except AttributeError("'int' object has no attribute 'write'"):
                        pass
                    except Exception as e:
                        er = True
                        messagebox.showerror("Error", str(e))
                    finally:
                        if not er:
                            messagebox.showinfo("Success", "Success!")
            else:
                messagebox.showinfo("Info", "There's nothing to be printed")

        elif command == "email":
            # Added re.sub to convert \n to a %0D%0A to conform wth Mailto URI Scheme
            # https://www.rfc-editor.org/rfc/rfc6068#section-5
            body = (f"My Diary - {text_date}\n\n"
                    f"-------------------\n\n"
                    f"{text}")
            body = re.sub("\n", "%0D%0A", body)
            webbrowser.open(f"mailto:?subject=My Diary - {text_date}&body={body}")

        else:
            raise ValueError("Invalid Command")

    def fill_list(self, lb: Listbox, selected_date):

        # Variable assignement for easier referencing
        acc = self.username
        db = self.db

        # Retrieve entries from DB for the specified user and date
        entries = db.execute("SELECT entries.entry_id, entries.entry, entries.date "
                             "FROM entries "
                             "JOIN accounts "
                             "ON accounts.id = entries.account_id "
                             "WHERE accounts.account = ? "
                             "AND entries.date = ?", (acc, selected_date,)).fetchall()

        # Clear entries from Listbox
        lb.delete(0, END)
        lb.selection_clear(0, END)

        # Add entries to Listbox and create a list of entries
        entries_list = []

        for count, entry in list(enumerate(entries)):
            entry_temp = Entries(count, entry[0], entry[1], entry[2])
            entries_list.append(entry_temp)
            if entry_temp.entry != "":
                lb.insert(entry_temp.count_id, entry_temp.entry)

        return entries_list

    def save_entry(self, entry_box: Text, index=None):
        acc = self.username
        text = entry_box.get("1.0", "end-1c")
        db = self.db
        acc_id = db.execute("SELECT id FROM accounts WHERE account = ?", (acc,)).fetchone()
        try:
            if index:
                db.execute("UPDATE entries "
                           "SET entry = ? "
                           "WHERE entry_id = ? "
                           "AND account_id = ?", (text, index, acc_id[0]))
            else:
                db.execute("INSERT INTO entries (account_id, entry, date) "
                           "VALUES (?, ?, ?)",
                           (acc_id[0], text, date.today(),))
            db.commit()
        except Exception as e:
            messagebox.showerror("Error", f"Failed, contact Administrator.\n{e}")
        else:
            messagebox.showinfo("Success", "Entry Saved.")
            self.clear_entry(entry_box)

    def __str__(self):
        return [self.id, self.username, self.f_name, self.l_name]


class Entries:
    def __init__(self, n: int, e_id: int, e: str, d: str):
        self.count_id = n  # Index on list
        self.entry_id = e_id  # Index on DB
        self.entry = e  # Entry's content
        self.date = d  # Entry's date


# Display-message-when-hovering-over-something-with-mouse-cursor-in-python
#   Source: https://stackoverflow.com/questions/20399243/
class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.text = None

    def showtip(self, text):
        # "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 70
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


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


def motivate():
    url = "https://complimentr.com/api"
    return (json.loads(requests.get(url).text))['compliment'].capitalize()


# Function to create tooltips whenever hovering over widgets
def createtooltip(widget, text):
    tooltip = ToolTip(widget)

    def enter(event):
        tooltip.showtip(text)

    def leave(event):
        tooltip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


def icon(icon_file):
    return ImageTk.PhotoImage(Image.open(icon_file).resize((12, 12), Image.Resampling.LANCZOS))
