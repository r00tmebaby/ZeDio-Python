@echo Silent install msi version

REM Uninstall any previous version of VLC

if exist "%PROGRAMFILES%\VideoLAN\VLC\uninstall.exe" "%PROGRAMFILES%\VideoLAN\VLC\uninstall.exe" /S
if exist "%PROGRAMFILES(x86)%\VideoLAN\VLC\uninstall.exe" "%PROGRAMFILES% (x86)\VideoLAN\VLC\uninstall.exe" /S

@Echo VLC silent install msi

start /wait msiexec /i "%~dp0vlc.msi" /qn