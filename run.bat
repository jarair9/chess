@echo off
title Autoshorts Server
echo Starting Autoshorts (Streamlit)...
echo Ensure you have Python installed and dependencies from src/lib/python/requirements.txt.
echo.

call streamlit run app.py

if %errorlevel% neq 0 (
    echo.
    echo Server crashed or stopped with an error!
    pause
)
