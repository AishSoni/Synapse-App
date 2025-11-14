@echo off
REM Package Chrome Extension for distribution

echo Packaging Synapse Chrome Extension...

REM Create dist directory
if not exist "dist" mkdir dist

REM Copy all necessary files
copy manifest.json dist\ >nul
copy background.js dist\ >nul
copy content.js dist\ >nul
if exist icon16.png copy icon16.png dist\ >nul
if exist icon48.png copy icon48.png dist\ >nul
if exist icon128.png copy icon128.png dist\ >nul

REM Create ZIP package using PowerShell
powershell -command "Compress-Archive -Path dist\* -DestinationPath synapse-extension.zip -Force"

echo.
echo Extension packaged to: synapse-extension.zip
echo.
echo To install in Chrome:
echo 1. Open chrome://extensions/
echo 2. Enable 'Developer mode'
echo 3. Extract synapse-extension.zip to a folder
echo 4. Click 'Load unpacked' and select the extracted folder
echo.
echo Or upload synapse-extension.zip to Chrome Web Store for publishing
echo.
pause
