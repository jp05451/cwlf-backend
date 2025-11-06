@echo off
chcp 65001 >nul
REM MySQL 備份排程安裝腳本

echo ========================================
echo   MySQL 備份排程任務安裝程式
echo ========================================
echo.

REM 檢查是否以系統管理員身份執行
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 錯誤: 此腳本需要系統管理員權限
    echo 請以系統管理員身份執行此批次檔
    echo.
    pause
    exit /b 1
)

REM 取得當前目錄的絕對路徑
set SCRIPT_DIR=%~dp0
set BACKUP_SCRIPT=%SCRIPT_DIR%backup.bat

REM 檢查 backup.bat 是否存在
if not exist "%BACKUP_SCRIPT%" (
    echo 錯誤: 找不到 backup.bat 檔案
    echo 預期位置: %BACKUP_SCRIPT%
    echo.
    pause
    exit /b 1
)

echo 備份腳本位置: %BACKUP_SCRIPT%
echo.

REM 詢問使用者設定排程時間
echo 請選擇備份排程頻率:
echo 1. 每天執行一次 (預設: 凌晨 2:00)
echo 2. 每週執行一次 (預設: 星期日 凌晨 2:00)
echo 3. 每 12 小時執行一次
echo 4. 自訂時間
echo.
set /p SCHEDULE_TYPE="請輸入選項 (1-4): "

if "%SCHEDULE_TYPE%"=="" set SCHEDULE_TYPE=1

if "%SCHEDULE_TYPE%"=="1" (
    set SCHEDULE_FREQ=DAILY
    set SCHEDULE_TIME=02:00
    set TASK_NAME=MySQL_Daily_Backup
    echo.
    echo 設定為: 每天凌晨 2:00 執行備份
) else if "%SCHEDULE_TYPE%"=="2" (
    set SCHEDULE_FREQ=WEEKLY
    set SCHEDULE_TIME=02:00
    set SCHEDULE_DAY=/D SUN
    set TASK_NAME=MySQL_Weekly_Backup
    echo.
    echo 設定為: 每週日凌晨 2:00 執行備份
) else if "%SCHEDULE_TYPE%"=="3" (
    set SCHEDULE_FREQ=DAILY
    set SCHEDULE_TIME=00:00
    set SCHEDULE_INTERVAL=/RI 720
    set TASK_NAME=MySQL_Hourly_Backup
    echo.
    echo 設定為: 每 12 小時執行一次備份
) else if "%SCHEDULE_TYPE%"=="4" (
    echo.
    set /p CUSTOM_TIME="請輸入執行時間 (格式: HH:MM，例如 14:30): "
    set SCHEDULE_FREQ=DAILY
    set SCHEDULE_TIME=%CUSTOM_TIME%
    set TASK_NAME=MySQL_Custom_Backup
    echo.
    echo 設定為: 每天 %CUSTOM_TIME% 執行備份
) else (
    echo 無效的選項，使用預設設定: 每天凌晨 2:00
    set SCHEDULE_FREQ=DAILY
    set SCHEDULE_TIME=02:00
    set TASK_NAME=MySQL_Daily_Backup
)

echo.
echo ========================================
echo   開始建立排程任務...
echo ========================================
echo.

REM 先刪除可能存在的舊任務
schtasks /Query /TN "%TASK_NAME%" >nul 2>&1
if %errorlevel% equ 0 (
    echo 偵測到現有的排程任務，正在刪除...
    schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1
    echo 已刪除舊的排程任務
    echo.
)

REM 建立新的排程任務
if "%SCHEDULE_TYPE%"=="2" (
    REM 每週任務
    schtasks /Create /TN "%TASK_NAME%" /TR "\"%BACKUP_SCRIPT%\"" /SC %SCHEDULE_FREQ% %SCHEDULE_DAY% /ST %SCHEDULE_TIME% /RU SYSTEM /RL HIGHEST /F
) else if "%SCHEDULE_TYPE%"=="3" (
    REM 每 12 小時任務
    schtasks /Create /TN "%TASK_NAME%" /TR "\"%BACKUP_SCRIPT%\"" /SC MINUTE /MO 720 /ST %SCHEDULE_TIME% /RU SYSTEM /RL HIGHEST /F
) else (
    REM 每天任務
    schtasks /Create /TN "%TASK_NAME%" /TR "\"%BACKUP_SCRIPT%\"" /SC %SCHEDULE_FREQ% /ST %SCHEDULE_TIME% /RU SYSTEM /RL HIGHEST /F
)

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   排程任務安裝成功！
    echo ========================================
    echo.
    echo 任務名稱: %TASK_NAME%
    echo 執行時間: %SCHEDULE_TIME%
    echo 備份腳本: %BACKUP_SCRIPT%
    echo.
    echo 你可以使用以下方式管理排程任務:
    echo 1. 開啟 "工作排程器" (Task Scheduler)
    echo 2. 使用指令: schtasks /Query /TN "%TASK_NAME%" /V /FO LIST
    echo 3. 刪除任務: schtasks /Delete /TN "%TASK_NAME%" /F
    echo.
    echo 如需立即測試備份，請執行 backup.bat
    echo.
) else (
    echo.
    echo ========================================
    echo   排程任務安裝失敗！
    echo ========================================
    echo.
    echo 請檢查:
    echo 1. 是否以系統管理員身份執行
    echo 2. backup.bat 檔案是否存在
    echo 3. 時間格式是否正確 (HH:MM)
    echo.
)

pause
