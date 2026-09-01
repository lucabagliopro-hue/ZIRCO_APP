@echo off
title ZIRCO - Arret Systeme
color 0C

echo ===================================================
echo      ZIRCO - PROTOCOLE D'ARRET
echo ===================================================
echo.

echo Fermeture des processus Python (FastAPI et Streamlit)...
taskkill /F /IM python.exe /T > nul 2>&1

echo Systeme ZIRCO deconnecte.
timeout /t 2 /nobreak > nul
exit