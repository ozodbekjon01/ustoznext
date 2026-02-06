from flask import Flask, session, redirect, url_for, request
from routes import auth , admin, dashboard, student


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.permanent_session_lifetime= 5200

# Blueprint-larni ro'yxatdan o'tkazish
app.register_blueprint(auth.bp)
app.register_blueprint(admin.bp, url_prefix='/admin')
app.register_blueprint(dashboard.bp,)
app.register_blueprint(student.bp,)

@app.route('/')
def index():
    return redirect('/login')

# App ishga tushirish
if __name__ == "__main__":
    app.run(debug=False)

