import telebot
from telebot import types
import sqlite3
import hashlib

TOKEN = "7799643295:AAFyEXdUT6VUZwKRQa1DNqjifArRTbQgyd0"
bot = telebot.TeleBot(TOKEN)
DB_NAME = "database.db"

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db()
    c = conn.cursor()

    # USERS jadvali
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        phone TEXT UNIQUE
    )
    """)

    # LOGINS jadvali
    c.execute("""
    CREATE TABLE IF NOT EXISTS logins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE,
        password TEXT,
        role TEXT,
        user_id INTEGER UNIQUE,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    conn.commit()
    conn.close()

create_tables()

# ================= STATES =================
user_states = {}
temp_data = {}

# ================= START =================
@bot.message_handler(commands=["start"])
def start(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("📱 Kontakt yuborish", request_contact=True))
    bot.send_message(
        message.chat.id,
        "Ro‘yxatdan o‘tish yoki parolni tiklash uchun kontakt yuboring 👇",
        reply_markup=kb
    )

# ================= CONTACT =================
@bot.message_handler(content_types=["contact"])
def contact_handler(message):
    chat_id = message.chat.id
    contact = message.contact
    phone = contact.phone_number
    full_name = f"{contact.first_name or ''} {contact.last_name or ''}".strip()

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    user = c.fetchone()

    # ===== FOYDALANUVCHI BOR =====
    if user:
        user_id = user['id']

        # recovery holat
        if user_states.get(chat_id) == "recovery_confirm":
            temp_data[chat_id] = {"user_id": user_id}
            user_states[chat_id] = "recovery_login"
            bot.send_message(chat_id, "🔁 Loginni yangilash uchun yangi login kiriting:")
            conn.close()
            return

        # birinchi marta aniqlansa
        user_states[chat_id] = "recovery_confirm"
        bot.send_message(
            chat_id,
            "ℹ️ Siz allaqachon ro‘yxatdan o‘tgansiz.\n"
            "Agar login yoki parolingizni unutgan bo‘lsangiz,\n"
            "parolni tiklash uchun kontaktni yana bir bor yuboring."
        )
        conn.close()
        return

    # ===== YANGI FOYDALANUVCHI =====
    c.execute("INSERT INTO users (full_name, phone) VALUES (?, ?)", (full_name, phone))
    user_id = c.lastrowid
    conn.commit()
    conn.close()

    temp_data[chat_id] = {"user_id": user_id}
    user_states[chat_id] = "register_login"
    bot.send_message(chat_id, "✅ Endi login kiriting:")

# ================= REGISTER LOGIN =================
@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "register_login")
def register_login(message):
    chat_id = message.chat.id
    login = message.text.strip()

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM logins WHERE login = ?", (login,))
    if c.fetchone():
        bot.send_message(chat_id, "❌ Bu login band. Boshqa login kiriting:")
        conn.close()
        return
    conn.close()

    temp_data[chat_id]["login"] = login
    user_states[chat_id] = "register_password"
    bot.send_message(chat_id, "🔐 Parol kiriting (kamida 6 ta belgi):")

# ================= REGISTER PASSWORD =================
@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "register_password")
def register_password(message):
    chat_id = message.chat.id
    password = message.text.strip()

    if len(password) < 6:
        bot.send_message(chat_id, "❌ Parol juda qisqa. Qayta kiriting:")
        return

    hashed = hashlib.sha256(password.encode()).hexdigest()
    user_id = temp_data[chat_id]["user_id"]
    login = temp_data[chat_id]["login"]

    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO logins (login, password, role, user_id) VALUES (?, ?, ?, ?)",
        (login, hashed, "student", user_id)
    )
    conn.commit()
    conn.close()

    user_states.pop(chat_id)
    temp_data.pop(chat_id)
    bot.send_message(chat_id, "🎉 Ro‘yxatdan o‘tish muvaffaqiyatli! Endi saytga login va parol bilan kirishingiz mumkin.")

# ================= RECOVERY LOGIN =================
@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "recovery_login")
def recovery_login(message):
    chat_id = message.chat.id
    login = message.text.strip()
    user_id = temp_data[chat_id]["user_id"]

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM logins WHERE login = ? AND user_id != ?", (login, user_id))
    if c.fetchone():
        bot.send_message(chat_id, "❌ Bu login band. Boshqasini kiriting:")
        conn.close()
        return
    conn.close()

    temp_data[chat_id]["login"] = login
    user_states[chat_id] = "recovery_password"
    bot.send_message(chat_id, "🔐 Yangi parol kiriting:")

# ================= RECOVERY PASSWORD =================
@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "recovery_password")
def recovery_password(message):
    chat_id = message.chat.id
    password = message.text.strip()
    if len(password) < 6:
        bot.send_message(chat_id, "❌ Parol juda qisqa. Qayta kiriting:")
        return

    hashed = hashlib.sha256(password.encode()).hexdigest()
    user_id = temp_data[chat_id]["user_id"]
    login = temp_data[chat_id]["login"]

    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE logins SET login = ?, password = ? WHERE user_id = ?", (login, hashed, user_id))
    conn.commit()
    conn.close()

    user_states.pop(chat_id)
    temp_data.pop(chat_id)
    bot.send_message(chat_id, "✅ Login va parol muvaffaqiyatli yangilandi. Endi yangi ma’lumotlar bilan saytga kirishingiz mumkin.")

bot.infinity_polling()
