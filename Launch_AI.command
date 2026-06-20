#!/bin/bash
cd "$(dirname "$0")/Desktop" 2>/dev/null || cd "$HOME/Desktop"
python3 -m streamlit run app.py
