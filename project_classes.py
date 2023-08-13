class User:
    def __init__(self, username, first_name, last_name, hashed_pass, key):
        self.username = username
        self.f_name = first_name
        self.l_name = last_name
        self.hashed_passwd = hashed_pass
        self.hash_key = key


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

