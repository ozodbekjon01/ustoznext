from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3

bp = Blueprint('admin', __name__)
DB_NAME = "database.db"

# ================= DATABASE HELPER =================
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ================= ADMIN DASHBOARD =================
@bp.route('/')
def dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM courses")
    courses = c.fetchall()
    conn.close()
    return render_template('admin/dashboard.html', courses=courses)

# ================= KURS QO'SHISH =================
@bp.route('/course/add', methods=['GET','POST'])
def add_course():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        if not title:
            flash("Iltimos, kurs nomini kiriting!")
            return redirect(url_for('admin.add_course'))

        conn = get_db()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO courses (title) VALUES (?)", (title,))
            conn.commit()
            flash("Kurs muvaffaqiyatli qo‘shildi!")
        except:
            flash("Bunday kurs mavjud!")
        conn.close()
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/add_course.html')

# ================= KURSNI O'CHIRISH =================
@bp.route('/course/delete/<int:course_id>')
def delete_course(course_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM topics WHERE course_id = ?", (course_id,))
    c.execute("DELETE FROM courses WHERE id = ?", (course_id,))
    conn.commit()
    conn.close()
    flash("Kurs o‘chirildi!")
    return redirect(url_for('admin.dashboard'))

# ================= MAVZU RO‘YXATI =================
@bp.route('/course/<int:course_id>/topics')
def topics(course_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    course = c.fetchone()
    c.execute("SELECT * FROM topics WHERE course_id = ? ORDER BY position", (course_id,))
    topics = c.fetchall()
    conn.close()
    return render_template('admin/topics.html', course=course, topics=topics)

# ================= MAVZU QO'SHISH =================
@bp.route('/course/<int:course_id>/topic/add', methods=['GET','POST'])
def add_topic(course_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        video_url = request.form.get('video_url')
        content = request.form.get('content')
        position = int(request.form.get('position') or 1)

        conn = get_db()
        c = conn.cursor()
        c.execute("""
            INSERT INTO topics (course_id, title, video_url, content, position)
            VALUES (?, ?, ?, ?, ?)
        """, (course_id, title, video_url, content, position))
        conn.commit()
        conn.close()
        flash("Mavzu qo‘shildi!")
        return redirect(url_for('admin.topics', course_id=course_id))

    return render_template('admin/add_topic.html', course_id=course_id)

# ================= MAVZU O'CHIRISH =================
@bp.route('/topic/delete/<int:topic_id>')
def delete_topic(topic_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT course_id FROM topics WHERE id = ?", (topic_id,))
    course_id = c.fetchone()['course_id']
    c.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
    conn.commit()
    conn.close()
    flash("Mavzu o‘chirildi!")
    return redirect(url_for('admin.topics', course_id=course_id))

# ================= MAVZUNI TAHRIRLASH =================
@bp.route('/topic/edit/<int:topic_id>', methods=['GET','POST'])
def edit_topic(topic_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM topics WHERE id = ?", (topic_id,))
    topic = c.fetchone()

    if request.method == 'POST':
        title = request.form.get('title')
        video_url = request.form.get('video_url')
        content = request.form.get('content')
        position = int(request.form.get('position') or 1)

        c.execute("""
            UPDATE topics
            SET title=?, video_url=?, content=?, position=?
            WHERE id=?
        """, (title, video_url, content, position, topic_id))
        conn.commit()
        conn.close()
        flash("Mavzu tahrirlandi!")
        return redirect(url_for('admin.topics', course_id=topic['course_id']))

    conn.close()
    return render_template('admin/edit_topic.html', topic=topic)


# ================= FOYDALANUVCHILAR RO‘YXATI =================
@bp.route('/users')
def users():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db()
    c = conn.cursor()

    # LEFT JOIN user_id orqali
    c.execute("""
        SELECT
            logins.id,
            users.full_name,
            logins.login,
            users.phone,
            logins.role
        FROM logins
        LEFT JOIN users ON users.id = logins.user_id
        ORDER BY logins.id DESC
    """)
    users = c.fetchall()

    c.execute("SELECT COUNT(*) FROM logins")
    users_count = c.fetchone()[0]

    conn.close()

    return render_template(
        'admin/users.html',
        users=users,
        users_count=users_count
    )
