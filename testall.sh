rm -rf venv
set -e

python3 -m venv venv
./venv/bin/python -m pip install --upgrade pip
./venv/bin/python -m pip install -r requirements.txt
./venv/bin/python -m pip install pytest
./venv/bin/python -m pip install flake8

echo "Run all tests..."
./venv/bin/python -m pytest ivviewer/tests -v

echo "Check flake8..."
./venv/bin/python -m flake8 ivviewer
echo "Done"