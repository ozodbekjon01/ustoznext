from flask import Blueprint, render_template, session, redirect, url_for, request
import sqlite3

bp = Blueprint('student', __name__,)
DB_NAME = "database.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ================= KURS RO'YXATI (kartalar bilan) =================
@bp.route('/student/courses')
def courses():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db()
    c = conn.cursor()
    # Har bir kurs uchun mavzular sonini hisoblaymiz
    c.execute("""
        SELECT 
            id, title, 
            (SELECT COUNT(*) FROM topics WHERE course_id=courses.id) AS topics_count 
        FROM courses
    """)
    courses = c.fetchall()
    conn.close()
    return render_template('student/courses.html', courses=courses)

# ================= TANLANGAN KURS Mavzulari =================
@bp.route('/course/<int:course_id>')
def course(course_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT id, title FROM courses WHERE id = ?", (course_id,))
    course = c.fetchone()

    c.execute("""
        SELECT id
        FROM topics
        WHERE course_id = ?
        ORDER BY position
        LIMIT 1
    """, (course_id,))
    first_topic = c.fetchone()

    conn.close()

    if not first_topic:
        return "Darslar yo‘q", 404

    return redirect(
        url_for(
            'student.topic',
            course_id=course_id,
            topic_id=first_topic['id']
        )
    )


@bp.route('/course/<int:course_id>/topic/<int:topic_id>')
def topic(course_id, topic_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db()
    c = conn.cursor()

    # Kurs
    c.execute("SELECT id, title FROM courses WHERE id = ?", (course_id,))
    course = c.fetchone()

    # Barcha darslar
    c.execute("""
        SELECT id, title, position
        FROM topics
        WHERE course_id = ?
        ORDER BY position
    """, (course_id,))
    topics = c.fetchall()

    # Joriy dars
    c.execute("""
        SELECT id, title, content, video_url, position
        FROM topics
        WHERE id = ? AND course_id = ?
    """, (topic_id, course_id))
    topic = c.fetchone()

    # KEYINGI DARS
    c.execute("""
        SELECT id
        FROM topics
        WHERE course_id = ?
          AND position > ?
        ORDER BY position
        LIMIT 1
    """, (course_id, topic['position']))
    next_topic = c.fetchone()

    conn.close()

    return render_template(
        'student/topic.html',
        course=course,
        topics=topics,
        topic=topic,
        active_topic_id=topic_id,
        next_topic=next_topic
    )
