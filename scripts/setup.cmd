@echo off
set SETUP_PATH=C:\users\WDAGUtilityAccount\Desktop\scripts\setups
echo [*] Copying setup files...
copy /B /Y /V %SETUP_PATH%\* %TEMP%\

msiexec /i "%TEMP%\7z2409-x64.msi" /qn /norestart
echo [*] Installing Visual Studio Code...
"%TEMP%\vscodesetup-x64.exe" /verysilent /suppressmsgboxes /MERGETASKS="!runcode,addtopath"

echo [*] Installing Python 3...
"%TEMP%\python-3.12.4-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
set "PATH=%PATH%;C:\Program Files\Python312\Scripts\"
set "PATH=%PATH%;C:\Program Files\Python312\"

echo [*] Installing Oletools...
pip install -U oletools[full]
echo "[*] oletools installed successfully."

echo [*] Enabling PowerShell ScriptBlockLogging...
powershell.exe -Command "New-Item -Path HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging -Force"
powershell.exe -Command "Set-ItemProperty -Path HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging -Name EnableScriptBlockLogging -Value 1 -Force"

echo [*] All tasks completed.
pause