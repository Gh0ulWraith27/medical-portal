"""
MediCare Portal - Flask backend
Run with: python app.py

This is an educational prototype. It uses SQLite for storage and Werkzeug
for password hashing. A real healthcare system needs stronger authentication,
authorization, audit logs, encryption, privacy controls, and regulatory review.
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
from pathlib import Path
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "medicare.db"

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY"

def get_db():
    """Open a SQLite connection. Row objects let us access columns by name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create tables the first time the program starts."""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL CHECK(role IN ('doctor','patient')),
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER NOT NULL,
        patient_id INTEGER NOT NULL,
        medicine TEXT NOT NULL,
        dosage TEXT NOT NULL,
        frequency TEXT NOT NULL,
        duration TEXT NOT NULL,
        instructions TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (doctor_id) REFERENCES users(id),
        FOREIGN KEY (patient_id) REFERENCES users(id)
    );
    """)
    conn.commit()
    conn.close()

def login_required(role=None):
    """Decorator that blocks pages unless the user is logged in.
    If role is supplied, the account must have that role."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("home"))
            if role and session.get("role") != role:
                return redirect(url_for("dashboard"))
            return view(*args, **kwargs)
        return wrapped
    return decorator

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def signup():
    """Create a doctor or patient account and store only a password hash."""
    role = request.form.get("role")
    name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if role not in ("doctor", "patient") or not name or not email or len(password) < 6:
        flash("Please complete all fields. Password must be at least 6 characters.")
        return redirect(url_for("home"))

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (role, full_name, email, password_hash) VALUES (?, ?, ?, ?)",
            (role, name, email, generate_password_hash(password))
        )
        conn.commit()
        flash("Account created. You can now log in.")
    except sqlite3.IntegrityError:
        flash("That email is already registered.")
    finally:
        conn.close()
    return redirect(url_for("home"))

@app.route("/login", methods=["POST"])
def login():
    """Verify credentials and create a server-side session."""
    role = request.form.get("role")
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ? AND role = ?", (email, role)
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        flash("Invalid email, password, or account type.")
        return redirect(url_for("home"))

    session["user_id"] = user["id"]
    session["role"] = user["role"]
    session["name"] = user["full_name"]
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required()
def dashboard():
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    if session["role"] == "doctor":
        patients = conn.execute(
            "SELECT id, full_name, email FROM users WHERE role='patient' ORDER BY full_name"
        ).fetchall()
        prescriptions = conn.execute("""
            SELECT p.*, u.full_name AS patient_name
            FROM prescriptions p
            JOIN users u ON u.id = p.patient_id
            WHERE p.doctor_id = ?
            ORDER BY p.created_at DESC
        """, (session["user_id"],)).fetchall()
    else:
        patients = []
        prescriptions = conn.execute("""
            SELECT p.*, u.full_name AS doctor_name
            FROM prescriptions p
            JOIN users u ON u.id = p.doctor_id
            WHERE p.patient_id = ?
            ORDER BY p.created_at DESC
        """, (session["user_id"],)).fetchall()

    conn.close()
    return render_template(
        "dashboard.html",
        user=user,
        patients=patients,
        prescriptions=prescriptions
    )

@app.route("/prescribe", methods=["POST"])
@login_required("doctor")
def prescribe():
    """Only a logged-in doctor can create a prescription."""
    patient_id = request.form.get("patient_id")
    medicine = request.form.get("medicine", "").strip()
    dosage = request.form.get("dosage", "").strip()
    frequency = request.form.get("frequency", "").strip()
    duration = request.form.get("duration", "").strip()
    instructions = request.form.get("instructions", "").strip()

    if not all([patient_id, medicine, dosage, frequency, duration]):
        flash("Please complete all required prescription fields.")
        return redirect(url_for("dashboard"))

    conn = get_db()
    patient = conn.execute(
        "SELECT id FROM users WHERE id = ? AND role='patient'", (patient_id,)
    ).fetchone()

    if not patient:
        conn.close()
        flash("Selected patient does not exist.")
        return redirect(url_for("dashboard"))

    conn.execute("""
        INSERT INTO prescriptions
        (doctor_id, patient_id, medicine, dosage, frequency, duration, instructions)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        session["user_id"], patient_id, medicine, dosage,
        frequency, duration, instructions
    ))
    conn.commit()
    conn.close()

    flash("Prescription saved successfully.")
    return redirect(url_for("dashboard"))

@app.route("/api/prescriptions")
@login_required()
def api_prescriptions():
    """Small JSON endpoint demonstrating how JavaScript can read backend data."""
    conn = get_db()
    if session["role"] == "doctor":
        rows = conn.execute("""
            SELECT p.id, p.medicine, p.dosage, p.frequency, p.duration,
                   p.instructions, p.created_at, u.full_name AS person
            FROM prescriptions p JOIN users u ON u.id=p.patient_id
            WHERE p.doctor_id=? ORDER BY p.created_at DESC
        """, (session["user_id"],)).fetchall()
    else:
        rows = conn.execute("""
            SELECT p.id, p.medicine, p.dosage, p.frequency, p.duration,
                   p.instructions, p.created_at, u.full_name AS person
            FROM prescriptions p JOIN users u ON u.id=p.doctor_id
            WHERE p.patient_id=? ORDER BY p.created_at DESC
        """, (session["user_id"],)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
