#!/bin/bash
cd "$(dirname "$0")"
python3 -m pip install --user -q -r requirements.txt
exec python3 VEIL.py
