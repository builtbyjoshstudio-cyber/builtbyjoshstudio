@echo off
REM Double-click this file to open inkpress.
REM You can also drag a manuscript onto it to open that manuscript straight away.
setlocal
set "APP=%~dp0inkpress_app.py"

REM pythonw and pyw open the window with no console behind it.
where pythonw >nul 2>&1
if %ERRORLEVEL%==0 (
  start "" pythonw "%APP%" %*
  exit /b
)

where pyw >nul 2>&1
if %ERRORLEVEL%==0 (
  start "" pyw "%APP%" %*
  exit /b
)

REM Fall back to a console launch so any startup error stays readable.
where py >nul 2>&1
if %ERRORLEVEL%==0 (
  py "%APP%" %*
  if errorlevel 1 pause
  exit /b
)

python "%APP%" %*
if errorlevel 1 pause
