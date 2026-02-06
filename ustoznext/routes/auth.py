from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
import hashlib

bp = Blueprint('auth', __name__)
DB_NAME = "database.db"

# ================= DATABASE HELPER =================
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ================= LOGIN ROUTE =================
@bp.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        login_input = request.form.get('login')
        password_input = request.form.get('password')

        if not login_input or not password_input:
            message = "❌ Iltimos, login va parolni kiriting."
            return render_template('login.html', message=message)

        hashed_input = hashlib.sha256(password_input.encode()).hexdigest()

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM logins WHERE login = ?", (login_input,))
        user = c.fetchone()
        conn.close()

        if user and user['password'] == hashed_input:
            # SUCCESS
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['login'] = user['login']
            if session['role']=="student":
                return redirect('/student/courses')  # dashboard route app.py da bo'lishi kerak
            elif session['role']=="admin":
                return redirect('/admin')
                
        else:
            message = "❌ Login yoki parol noto‘g‘ri."

    return render_template('login.html', message=message)

# ================= LOGOUT ROUTE =================
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
