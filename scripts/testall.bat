cd ..
setlocal EnableDelayedExpansion
set PYTHON=c:\python\python312\python
if exist venv rd /s/q venv

%PYTHON% -m venv venv
venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\python -m pip install -r requirements.txt
venv\Scripts\python -m pip install flake8 pytest

echo --- Run all tests ---
venv\Scripts\python -m pytest ivviewer\tests -v

echo --- Check flake8 ---
venv\Scripts\python -m flake8 .

echo --- Done ---
pause