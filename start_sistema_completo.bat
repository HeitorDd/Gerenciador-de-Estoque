@echo off
REM Arquivo: start_sistema_completo.bat (Versão com UI do Monitor)
REM Inicia todos os 3 componentes do sistema.

echo Iniciando Sistema de Inventario...

REM 1. Inicia a API (Backend) em uma nova janela
echo [1/3] Iniciando API (Flask)...
start "API - Servidor" python api.py

REM 2. Inicia o Monitor (AGORA COM UI) em uma nova janela
echo [2/3] Iniciando Monitor (UI)...
start "Monitor de Inventario (UI)" python monitor_ui.py

REM 3. Inicia o Frontend (Cadastro)
echo [3/3] Iniciando Interface (Tkinter)...
echo.
echo Aguarde o login no Monitor e na Interface.

REM Pausa por 2 segundos para dar tempo da API iniciar
timeout /t 2 /nobreak > nul

REM Roda o cadastro nesta janela
python cadastro.py

echo.
echo ----------------------------------------------------
echo A interface (cadastro.py) foi fechada.
echo A API e o Monitor (UI) continuam rodando nas outras janelas.
echo ----------------------------------------------------
pause