@echo off
if not exist "%~dp0.env" copy "%~dp0.env.example" "%~dp0.env" >nul
notepad "%~dp0.env"
