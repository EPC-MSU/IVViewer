@echo off
setlocal EnableDelayedExpansion
if exist venv rd /S /Q venv
python -m venv venv
venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\python -m pip install -r requirements.txt
venv\Scripts\python -m pip install flake8 pytest

echo --- Run all tests ---
venv\Scripts\python -m pytest ivviewer\tests -v

echo --- Check flake8 ---
venv\Scripts\python -m flake8 .

echo --- Done ---
pause