# MediCare Prescription Portal

A beginner-friendly Flask + SQLite healthcare portal prototype with separate
Doctor and Patient accounts.

## What it does

- Doctor signup/login
- Patient signup/login
- Passwords are hashed instead of stored as plain text
- SQLite database is created automatically
- Doctors can select registered patients and create prescriptions
- Patients can view their prescriptions
- Role-based route protection
- Responsive hospital-style interface
- JavaScript tab interaction and alert handling
- Optional C++ validation utility

## Project structure

```text
medicare_portal/
├── app.py                  # Python backend / Flask server
├── requirements.txt        # Python packages
├── run_windows.bat         # Easy Windows launcher
├── run_mac_linux.sh        # Easy macOS/Linux launcher
├── prescription_helper.cpp # Optional C++ utility
├── data/
│   └── medicare.db         # Created automatically after first run
├── templates/
│   ├── index.html          # Login/signup page
│   └── dashboard.html      # Doctor/patient dashboard
└── static/
    ├── style.css           # Hospital-style design
    └── app.js              # Browser interactions
```

## Run in VS Code

1. Install Python 3.10+.
2. Open this folder in VS Code.
3. Open Terminal > New Terminal.
4. Run:

Windows:
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

5. Open the local address printed by Flask, normally:
`http://127.0.0.1:5000`

## Testing the workflow

1. Open the Doctor tab and create a doctor account.
2. Open the Patient tab and create a patient account.
3. Log in as the doctor.
4. Select the patient and create a prescription.
5. Log out.
6. Log in as the patient.
7. The prescription should now appear in the patient dashboard.

## How the backend works

Browser form -> Flask route -> validation -> SQLite -> response/page

`app.py` creates two database tables:

- `users`: doctor/patient accounts
- `prescriptions`: doctor, patient, medicine, dosage, frequency, duration, instructions

When a user signs up, `generate_password_hash()` turns the password into a
one-way hash. During login, `check_password_hash()` verifies the submitted
password against the stored hash.

Parameterized SQL (`?`) is used for database values to reduce SQL injection risk.

The session stores the logged-in user's ID, role, and display name. The
`login_required()` decorator prevents users from opening protected pages
without authentication and prevents patients from accessing the doctor-only
prescription endpoint.

## Important medical/security note

This is a school/learning prototype, NOT a production medical-record system.
Do not use it with real patient information. A production system should add,
at minimum:

- HTTPS/TLS
- secure environment-based secrets
- CSRF protection
- stronger password policy and MFA
- account verification and password reset
- granular authorization
- audit logs
- encrypted data and backups
- input validation and security headers
- session cookie security
- rate limiting
- professional clinical workflow and medication checks
- privacy/security compliance applicable to the deployment
