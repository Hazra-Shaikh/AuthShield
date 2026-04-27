from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import pyotp
import qrcode
import re
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "MFA"


def is_valid_password(password):
    # At least 6 chars, 1 letter, 1 number, 1 special char
    if len(password) < 6:
        return False
    if not re.search(r"[A-Za-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[@$!%*?&]", password):
        return False
    return True

DB = os.path.join(os.path.dirname(__file__), "users.db")

# ---------------- DB SETUP ----------------
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT UNIQUE,
            password TEXT,
            secret TEXT,
            attempts INTEGER DEFAULT 0,
            lock_until TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return redirect('/login')

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if not is_valid_password(password):
            return render_template("register.html", error="Password must be 6+ chars, include letter, number, and special character")
        password = generate_password_hash(request.form['password'])

        secret = pyotp.random_base32()

        try:
            conn = sqlite3.connect(DB)
            c = conn.cursor()

            c.execute("INSERT INTO users (username, email, password, secret) VALUES (?, ?, ?, ?)",
                    (username, email, password, secret))

            conn.commit()
            conn.close()

        except sqlite3.IntegrityError:
            return render_template("register.html", error="Email already registered")

        # QR Code
        uri = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name="MFA-App")
        img = qrcode.make(uri)
        path = f"static/qr/{email}.png"
        img.save(path)

        return render_template("register.html", qr=path)

    return render_template("register.html", qr=None)

# ---------- LOGIN ----------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        user = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

        if user:
            attempts = user[5]
            lock_until = user[6]

            # Check if locked
            if lock_until:
                lock_time = datetime.fromisoformat(lock_until)
                if datetime.now() < lock_time:
                    remaining = (lock_time - datetime.now()).seconds
                    conn.close()
                    return render_template("login.html", error=f"Account locked. Try again in {remaining//60 + 1} min")

            # Check password
            if check_password_hash(user[3], password):
                # Reset attempts
                c.execute("UPDATE users SET attempts=0, lock_until=NULL WHERE email=?", (email,))
                conn.commit()
                conn.close()

                session['temp_user'] = user
                return redirect('/verify')

            else:
                attempts += 1

                if attempts >= 3:
                    lock_time = datetime.now() + timedelta(minutes=2)
                    c.execute("UPDATE users SET attempts=?, lock_until=? WHERE email=?",
                              (attempts, lock_time.isoformat(), email))
                    conn.commit()
                    conn.close()

                    return render_template("login.html", error="Too many attempts. Account locked for 2 minutes.")

                else:
                    c.execute("UPDATE users SET attempts=? WHERE email=?", (attempts, email))
                    conn.commit()
                    conn.close()

                    return render_template("login.html", error=f"Invalid credentials. Attempts left: {3 - attempts}")

        conn.close()
        return render_template("login.html", error="User not found")

    return render_template("login.html")

# ---------- VERIFY OTP ----------
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        otp = request.form['otp']
        user = session.get('temp_user')

        if user:
            secret = user[4]
            totp = pyotp.TOTP(secret)

            if totp.verify(otp):
                session['user'] = user[1]
                session.pop('temp_user', None)
                return redirect('/dashboard')

        return render_template("verify.html", error="Invalid OTP")

    return render_template("verify.html")

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template("dashboard.html", user=session['user'])
    return redirect('/login')

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run()