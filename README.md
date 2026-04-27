# 🔐 AuthShield

A secure and modern **Multi-Factor Authentication (MFA) system** built using Flask and Google Authenticator (TOTP).
AuthShield enhances login security by combining password-based authentication with time-based one-time passwords.

---

## 🚀 Features

* 🔑 User Registration & Login
* 🔐 Password Hashing using Werkzeug
* 📱 Google Authenticator Integration (TOTP)
* 📊 QR Code Generation for MFA setup
* 🚫 Login Attempt Limiting (Account Lock after 3 failed attempts)
* ⏱ Temporary Account Lock (2 minutes)
* 🔒 Strong Password Validation
* 🎨 Responsive UI with Bootstrap & Custom CSS
* ⚡ Clean and minimal design with glassmorphism

---

## 🛠 Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML, CSS, Bootstrap
* **Database:** SQLite
* **Authentication:** PyOTP (TOTP)
* **Other Libraries:** QRCode, Pillow, Werkzeug

---

## 📂 Project Structure

```
AuthShield/
│
├── app.py
├── requirements.txt
├── Procfile
├── users.db
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── verify.html
│   └── dashboard.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── qr/
```

## 🔐 How It Works

1. User registers with email and password
2. System generates a **unique secret key**
3. QR code is displayed and scanned using Google Authenticator
4. User logs in with email & password
5. OTP verification is required
6. On successful verification → access granted

---

## 🛡 Security Features

* Password hashing using Werkzeug
* TOTP-based authentication (time-based OTP)
* Login attempt tracking
* Temporary account lock after multiple failures
* Strong password enforcement

---

## 👨‍💻 Author

**Hazra Shaikh**


