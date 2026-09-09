@echo off
REM Create a virtual environment and install dependencies.
python -m venv .venv
call .venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
