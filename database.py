import sqlite3
DB = "canteen.db"

def init_db():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            balance REAL DEFAULT 0)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            type TEXT NOT NULL,
            item TEXT,
            amount REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        con.commit()

def add_member(phone, name):
    with sqlite3.connect(DB) as con:
        try:
            con.execute("INSERT INTO members (phone, name) VALUES (?, ?)", (phone, name))
            con.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def get_member(phone):
    with sqlite3.connect(DB) as con:
        cur = con.execute("SELECT * FROM members WHERE phone = ?", (phone,))
        return cur.fetchone()

def get_all_members():
    with sqlite3.connect(DB) as con:
        cur = con.execute("SELECT * FROM members ORDER BY name")
        return cur.fetchall()

def add_take(phone, item, amount):
    with sqlite3.connect(DB) as con:
        con.execute("UPDATE members SET balance = balance + ? WHERE phone = ?", (amount, phone))
        con.execute("INSERT INTO transactions (phone, type, item, amount) VALUES (?, 'take', ?, ?)", (phone, item, amount))
        con.commit()

def add_payment(phone, amount):
    with sqlite3.connect(DB) as con:
        con.execute("UPDATE members SET balance = balance - ? WHERE phone = ?", (amount, phone))
        con.execute("INSERT INTO transactions (phone, type, amount) VALUES (?, 'payment', ?)", (phone, amount))
        con.commit()

def get_transactions(phone=None):
    with sqlite3.connect(DB) as con:
        if phone:
            cur = con.execute("SELECT * FROM transactions WHERE phone = ? ORDER BY timestamp DESC", (phone,))
        else:
            cur = con.execute("SELECT * FROM transactions ORDER BY timestamp DESC")
        return cur.fetchall()
