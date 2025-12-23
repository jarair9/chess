@echo off
title Autoshorts Server
echo Starting Autoshorts...
echo Ensure you have Node.js and Python installed.
echo.

call npm start

if %errorlevel% neq 0 (
    echo.
    echo Server crashed or stopped with an error!
    pause
)
