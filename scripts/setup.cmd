@echo off
set SETUP_PATH=C:\users\WDAGUtilityAccount\Desktop\scripts\setups
echo [*] Copying setup files...
copy /B /Y /V %SETUP_PATH%\* %TEMP%\

msiexec /i "%TEMP%\7z2409-x64.msi" /qn /norestart
echo [*] Installing Visual Studio Code...
"%TEMP%\vscodesetup-x64.exe" /verysilent /suppressmsgboxes /MERGETASKS="!runcode,addtopath"

echo [*] Installing Sysinternals...
"%PROGRAMFILES%\7-Zip\7z.exe" x -aoa "%TEMP%\sysinternalssuite.zip" -o"%USERPROFILE%\Desktop\Tools\sysinternals"

echo [*] Installing Python 3...
"%TEMP%\python-3.12.4-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
set "PATH=%PATH%;C:\Program Files\Python312\Scripts\"
set "PATH=%PATH%;C:\Program Files\Python312\"

echo [*] Installing Python 2...
msiexec /i "%TEMP%\python-2.7.18.amd64.msi" /qn /norestart

echo [*] Installing JPEGView...
if not exist "C:\Program Files\JPEGView64" mkdir "C:\Program Files\JPEGView64"
"%PROGRAMFILES%\7-Zip\7z.exe" x -aoa "%TEMP%\jpegview_1.3.46.7z" -o"C:\Program Files" JPEGView64\*
assoc .jpg=JPEGView.Image
assoc .png=JPEGView.Image
ftype JPEGView.Image="C:\Program Files\JPEGView64\JPEGView64.exe" "%%1"

echo [*] Installing Git...
"%TEMP%\git-2.50.0-64-bit.exe" /VERYSILENT /NORESTART /NOCANCEL /SP-
set "PATH=%PATH%;C:\Program Files\Git\cmd"

echo [*] Installing Oletools...
pip install -U oletools[full]
echo "[*] oletools installed successfully."

echo [*] Enabling PowerShell ScriptBlockLogging...
powershell.exe -Command "New-Item -Path HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging -Force"
powershell.exe -Command "Set-ItemProperty -Path HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging -Name EnableScriptBlockLogging -Value 1 -Force"

echo [*] All tasks completed.
pause