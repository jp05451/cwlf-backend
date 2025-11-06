@echo off
chcp 65001 >nul
REM MySQL 備份排程解除安裝腳本

echo ========================================
echo   MySQL 備份排程任務解除安裝程式
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

REM 列出可能的任務名稱
set TASKS=MySQL_Daily_Backup MySQL_Weekly_Backup MySQL_Hourly_Backup MySQL_Custom_Backup

echo 搜尋已安裝的備份排程任務...
echo.

set FOUND=0

for %%T in (%TASKS%) do (
    schtasks /Query /TN "%%T" >nul 2>&1
    if !errorlevel! equ 0 (
        set FOUND=1
        echo 找到任務: %%T

        REM 顯示任務詳細資訊
        echo.
        echo 任務詳細資訊:
        schtasks /Query /TN "%%T" /V /FO LIST | findstr /C:"工作名稱" /C:"下次執行時間" /C:"上次執行時間" /C:"Task To Run"
        echo.

        set /p CONFIRM="確定要刪除此任務嗎? (Y/N): "
        if /i "!CONFIRM!"=="Y" (
            schtasks /Delete /TN "%%T" /F
            if !errorlevel! equ 0 (
                echo ✓ 任務 %%T 已成功刪除
            ) else (
                echo ✗ 刪除任務 %%T 失敗
            )
        ) else (
            echo 已取消刪除任務 %%T
        )
        echo.
        echo ----------------------------------------
        echo.
    )
)

if %FOUND%==0 (
    echo 沒有找到任何 MySQL 備份排程任務
    echo.
    echo 如果你使用自訂名稱，請手動刪除:
    echo schtasks /Delete /TN "你的任務名稱" /F
    echo.
    echo 或使用工作排程器 (Task Scheduler) 手動管理
)

echo.
echo 解除安裝程式執行完畢
pause
