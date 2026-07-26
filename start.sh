#!/bin/bash

echo "[ANSH] Checking Python installation..."
if ! command -v python3 &> /dev/null
then
    echo "[ANSH] Python3 is not installed!"
    echo "[ANSH] Please install it via your package manager (e.g., sudo apt install python3 python3-venv) and try again."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "[ANSH] Creating Virtual Environment for isolation..."
    python3 -m venv venv
fi

echo "[ANSH] Activating Environment..."
source venv/bin/activate

echo "[ANSH] Installing necessary packages..."
pip install -r requirements.txt --quiet

echo "[ANSH] Starting ANSH..."
python3 main.py
