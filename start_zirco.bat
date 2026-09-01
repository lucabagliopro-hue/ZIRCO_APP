@echo off
title ZIRCO - Initialisation Systeme
color 0B

echo ===================================================
echo      ZIRCO - PROTOCOLE DE DEMARRAGE SYSTEME
echo ===================================================
echo.

echo [1/3] Demarrage du noyau serveur (FastAPI)...
start /b python server.py > nul 2>&1

echo [2/3] Demarrage du tableau de bord (Streamlit)...
:: Utilisation de "python -m streamlit" pour contourner le problème de PATH Windows
start /b python -m streamlit run app.py > nul 2>&1

echo [3/3] Synchronisation des modules (Attente 5s)...
timeout /t 5 /nobreak > nul

echo Lancement de l'interface de commandement...
start msedge --app=http://localhost:8501

exit