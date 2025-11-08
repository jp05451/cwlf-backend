@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
REM MySQL 資料庫還原腳本 (Windows 版本)

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
    pause
    exit /b 1
)

REM 檢查是否成功讀取環境變數
if not defined DB_USER (
    echo 錯誤: 無法從 .env 讀取 MYSQL_ROOT_USER
    pause
    exit /b 1
)
if not defined DB_PASSWORD (
    echo 錯誤: 無法從 .env 讀取 MYSQL_ROOT_PASSWORD
    pause
    exit /b 1
)

REM 檢查是否提供備份檔案參數
if "%~1"=="" (
    echo 使用方式: %~nx0 ^<備份檔案名稱^>
    echo.
    echo 可用的備份檔案:
    if exist "%BACKUP_DIR%\mysql_backup_*.sql" (
        dir /b "%BACKUP_DIR%\mysql_backup_*.sql" 2>nul
    )
    if exist "%BACKUP_DIR%\mysql_backup_*.sql.gz" (
        dir /b "%BACKUP_DIR%\mysql_backup_*.sql.gz" 2>nul
    )
    if exist "%BACKUP_DIR%\mysql_backup_*.zip" (
        dir /b "%BACKUP_DIR%\mysql_backup_*.zip" 2>nul
    )
    if not exist "%BACKUP_DIR%\mysql_backup_*.*" (
        echo   沒有找到備份檔案
    )
    echo.
    pause
    exit /b 1
)

REM 處理輸入參數，取得檔案名稱
SET BACKUP_FILE=%~nx1
SET BACKUP_PATH=%BACKUP_DIR%\%BACKUP_FILE%

REM 檢查備份檔案是否存在
if not exist "%BACKUP_PATH%" (
    echo 錯誤: 備份檔案 %BACKUP_FILE% 不存在於 %BACKUP_DIR%
    pause
    exit /b 1
)

REM 檢查容器是否運行
docker ps --format "{{.Names}}" | findstr /x "%CONTAINER_NAME%" >nul
if errorlevel 1 (
    echo 錯誤: 容器 %CONTAINER_NAME% 未運行
    echo.
    echo 請先啟動服務: docker compose up -d
    pause
    exit /b 1
)

REM 確認還原操作
echo ========================================
echo   警告: 資料庫還原確認
echo ========================================
echo.
echo 此操作將覆蓋現有資料庫 %DB_NAME%！
echo.
echo 備份檔案: %BACKUP_FILE%
echo 目標容器: %CONTAINER_NAME%
echo 目標資料庫: %DB_NAME%
echo.
echo 此操作無法復原，請確認您已了解風險。
echo.
set /p CONFIRMATION="確定要繼續嗎? (請輸入 yes 確認): "

if /i not "%CONFIRMATION%"=="yes" (
    echo.
    echo 已取消還原操作
    pause
    exit /b 0
)

echo.
echo ========================================
echo   開始還原資料庫...
echo ========================================
echo.

REM 檢查檔案類型並處理
SET TEMP_FILE=%BACKUP_PATH%
SET IS_COMPRESSED=0

REM 檢查是否為 .zip 檔案
echo %BACKUP_FILE% | findstr /i "\.zip$" >nul
if not errorlevel 1 (
    echo 偵測到 ZIP 壓縮檔案，正在解壓縮...
    SET TEMP_FILE=%BACKUP_DIR%\temp_restore.sql

    REM 使用 PowerShell 解壓縮
    powershell -Command "Expand-Archive -Path '%BACKUP_PATH%' -DestinationPath '%BACKUP_DIR%\temp_extract' -Force"
    if errorlevel 1 (
        echo 解壓縮失敗
        pause
        exit /b 1
    )

    REM 找到解壓縮後的 .sql 檔案
    for %%f in ("%BACKUP_DIR%\temp_extract\*.sql") do (
        copy "%%f" "!TEMP_FILE!" >nul
    )

    if not exist "!TEMP_FILE!" (
        echo 錯誤: 在壓縮檔中找不到 .sql 檔案
        rd /s /q "%BACKUP_DIR%\temp_extract" 2>nul
        pause
        exit /b 1
    )

    SET IS_COMPRESSED=1
)

REM 檢查是否為 .gz 檔案
echo %BACKUP_FILE% | findstr /i "\.gz$" >nul
if not errorlevel 1 (
    echo 偵測到 GZIP 壓縮檔案，正在解壓縮...
    SET TEMP_FILE=%BACKUP_DIR%\temp_restore.sql

    REM 使用 PowerShell 解壓縮 gzip (需要 .NET 4.5+)
    powershell -Command "$input = [System.IO.File]::OpenRead('%BACKUP_PATH%'); $output = [System.IO.File]::Create('!TEMP_FILE!'); $gzipStream = New-Object System.IO.Compression.GzipStream $input, ([System.IO.Compression.CompressionMode]::Decompress); $gzipStream.CopyTo($output); $gzipStream.Close(); $output.Close(); $input.Close()"

    if errorlevel 1 (
        echo 解壓縮失敗，請確認檔案格式正確
        pause
        exit /b 1
    )

    SET IS_COMPRESSED=1
)

REM 還原資料庫
echo 正在將資料導入資料庫...
type "!TEMP_FILE!" | docker exec -i %CONTAINER_NAME% mysql -u%DB_USER% -p%DB_PASSWORD% %DB_NAME%

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   還原成功！
    echo ========================================
    echo.
    echo 資料庫已成功還原: %BACKUP_FILE% -^> %DB_NAME%
    echo.
    echo 建議執行以下操作:
    echo.
    echo 1. 檢查資料庫內容:
    echo    docker exec -it %CONTAINER_NAME% mysql -u%DB_USER% -p%DB_PASSWORD% -e "USE %DB_NAME%; SHOW TABLES;"
    echo.
    echo 2. 若需要，重啟相關應用容器:
    echo    docker compose restart cwlf-backend
    echo.

    REM 清理臨時檔案
    if %IS_COMPRESSED%==1 (
        if exist "!TEMP_FILE!" del /f /q "!TEMP_FILE!" >nul 2>&1
        if exist "%BACKUP_DIR%\temp_extract" rd /s /q "%BACKUP_DIR%\temp_extract" >nul 2>&1
        echo 已清理臨時解壓檔案
        echo.
    )

    echo 還原完成！
) else (
    echo.
    echo ========================================
    echo   還原失敗！
    echo ========================================
    echo.
    echo 請檢查:
    echo 1. 備份檔案是否完整且格式正確
    echo 2. 資料庫容器是否正常運行
    echo 3. 資料庫使用者權限是否正確
    echo.

    REM 清理臨時檔案
    if %IS_COMPRESSED%==1 (
        if exist "!TEMP_FILE!" del /f /q "!TEMP_FILE!" >nul 2>&1
        if exist "%BACKUP_DIR%\temp_extract" rd /s /q "%BACKUP_DIR%\temp_extract" >nul 2>&1
    )

    pause
    exit /b 1
)

pause
