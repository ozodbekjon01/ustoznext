import sqlite3
import hashlib

conn = sqlite3.connect("database.db")
c = conn.cursor()

# ================= USERS JADVALI =================
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT
);
""")

# ================= LOGINS JADVALI =================
c.execute("""
CREATE TABLE IF NOT EXISTS logins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    user_id INTEGER UNIQUE,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
""")

# ================= COURSES JADVALI =================
c.execute("""
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE NOT NULL
);
""")

# ================= TOPICS JADVALI =================
c.execute("""
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER,
    title TEXT,
    video_url TEXT,
    content TEXT,
    position INTEGER,
    FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
);
""")

# ================= ADMIN FOYDALANUVCHI =================
# full_name = "Admin User"
# phone = "998901234567"

# # Avval users jadvaliga qo‘shamiz
# c.execute("SELECT * FROM users WHERE full_name = ?", (full_name,))
# user = c.fetchone()
# if not user:
#     c.execute("INSERT INTO users (full_name, phone) VALUES (?, ?)", (full_name, phone))
#     user_id = c.lastrowid
# else:
#     user_id = user[0]

# login = "admin"
# password = "2006..eerr"
# role = "admin"
# hashed = hashlib.sha256(password.encode()).hexdigest()

# c.execute("SELECT * FROM logins WHERE login = ?", (login,))
# if not c.fetchone():
#     c.execute(
#         "INSERT INTO logins (login, password, role, user_id) VALUES (?, ?, ?, ?)",
#         (login, hashed, role, user_id)
#     )

conn.commit()
conn.close()
