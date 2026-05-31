@echo off
chcp 65001 > nul

rem ――― 設定項目 ―――
set EXE_NAME="SequenceEditor"
set ICON_FILE="damiyan2.ico"
set ENTRY_POINT="main.py"
rem ――――――――――――――

echo ===================================================
echo  PyInstallerによるビルドを開始します...
echo ===================================================

pyinstaller --clean -y -F -w -i %ICON_FILE% -n %EXE_NAME% %ENTRY_POINT%

echo ===================================================
echo  ビルドが完了しました。
echo ===================================================
pause