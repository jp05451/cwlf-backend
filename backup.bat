@echo off
chcp 65001 >nul
REM MySQL 備份腳本 (Windows 版本)

SET CONTAINER_NAME=mysql_db
SET DB_NAME=cwlf_db
SET BACKUP_DIR=.\backups

REM 讀取 .env 檔案中的環境變數
if exist .env (
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        set "line=%%a"
        if not "!line:~0,1!"=="#" (
            if "%%a"=="MYSQL_ROOT_USER" set "DB_USER=%%b"
            if "%%a"=="MYSQL_ROOT_PASSWORD" set "DB_PASSWORD=%%b"
        )
    )
) else (
    echo 錯誤: 找不到 .env 檔案
    exit /b 1
)

REM 檢查是否成功讀取環境變數
if not defined DB_USER (
    echo 錯誤: 無法從 .env 讀取 MYSQL_ROOT_USER
    exit /b 1
)
if not defined DB_PASSWORD (
    echo 錯誤: 無法從 .env 讀取 MYSQL_ROOT_PASSWORD
    exit /b 1
)

REM 產生時間戳記
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set TIMESTAMP=%dt:~0,8%_%dt:~8,6%
SET BACKUP_FILE=mysql_backup_%TIMESTAMP%.sql

REM 建立備份目錄
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM 檢查容器是否運行
docker ps --format "{{.Names}}" | findstr /x "%CONTAINER_NAME%" >nul
if errorlevel 1 (
    echo 錯誤: 容器 %CONTAINER_NAME% 未運行
    exit /b 1
)

REM 備份 MySQL 資料庫
echo 開始備份 MySQL 資料庫...
docker exec %CONTAINER_NAME% mysqldump -u%DB_USER% -p%DB_PASSWORD% %DB_NAME% > %BACKUP_DIR%\%BACKUP_FILE%

if %errorlevel% equ 0 (
    echo 備份成功: %BACKUP_DIR%\%BACKUP_FILE%

    REM 壓縮備份檔案 (使用 PowerShell)
    powershell -Command "Compress-Archive -Path '%BACKUP_DIR%\%BACKUP_FILE%' -DestinationPath '%BACKUP_DIR%\%BACKUP_FILE%.zip' -Force"
    if %errorlevel% equ 0 (
        del "%BACKUP_DIR%\%BACKUP_FILE%"
        echo 已壓縮備份檔案
    ) else (
        echo 警告: 壓縮失敗，保留原始 SQL 檔案
    )

    REM 刪除 7 天前的備份 (同時處理 .sql 和 .zip)
    forfiles /p "%BACKUP_DIR%" /m mysql_backup_*.sql /d -7 /c "cmd /c del @path" 2>nul
    forfiles /p "%BACKUP_DIR%" /m mysql_backup_*.zip /d -7 /c "cmd /c del @path" 2>nul
    echo 已清理 7 天前的舊備份
) else (
    echo 備份失敗
    exit /b 1
)

echo 備份完成！
pause
