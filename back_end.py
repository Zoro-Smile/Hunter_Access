from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)   # Better secret key


# ================= DATABASE CONNECTION =================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="smile1",
    database="smile"
)


# ================= HOME =================
@app.route('/')
def home_page():
    return render_template('Homepage.html')


# ================= SIGNUP =================
@app.route('/signup')
def signup_page():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    cursor = db.cursor()

    sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"

    try:
        cursor.execute(sql, (name, email, password))
        db.commit()
        return redirect(url_for('login_page'))
    except mysql.connector.Error:
        return "Email already exists!"


# ================= LOGIN =================
@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    name = request.form['name']
    password = request.form['password']

    cursor = db.cursor(dictionary=True)

    sql = "SELECT user_id, name, email FROM users WHERE name = %s AND password = %s"
    cursor.execute(sql, (name, password))
    user = cursor.fetchone()

    if user:
        # Store only identity
        session['user_id'] = user['user_id']
        return redirect(url_for('dashboard'))
    else:
        return "Invalid Username or Password"


# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():
    # Authentication guard
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    cursor = db.cursor(dictionary=True)

    sql = "SELECT user_id, name, email FROM users WHERE user_id = %s"
    cursor.execute(sql, (session['user_id'],))
    user = cursor.fetchone()

    # Defensive check
    if not user:
        session.clear()
        return redirect(url_for('login_page'))

    return render_template('dashboard.html', user=user)


# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))


# ================= RUN APP =================
if __name__ == "__main__":
    app.run(debug=True)
