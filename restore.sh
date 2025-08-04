#!/bin/bash

# 腳本需要一個參數：要還原的備份檔案路徑
BACKUP_FILE=$1
# UAT 環境的 MySQL 容器名稱
CONTAINER_NAME="mysql-uat"

# 檢查是否提供了備份檔案
if [ -z "$BACKUP_FILE" ]; then
    echo "❌ 錯誤：請提供要還原的備份檔案路徑！"
    echo "用法: ./restore.sh /path/to/your/backup.sql"
    exit 1
fi

# 檢查備份檔案是否存在
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ 錯誤：找不到備份檔案 '${BACKUP_FILE}'"
    exit 1
fi

echo "⚠️ 警告：這將會覆寫容器 '${CONTAINER_NAME}' 中的現有資料！"
read -p "你確定要繼續嗎？ (y/n) " -n 1 -r
echo "" # 換行
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "操作已取消。"
    exit 0
fi

echo "正在從檔案 '${BACKUP_FILE}' 還原資料庫至容器 '${CONTAINER_NAME}'..."

# 使用 cat 將備份檔案內容通過管道 pipe 傳給 docker exec
# docker exec -i 讓 mysql 客戶端可以接收標準輸入
cat "${BACKUP_FILE}" | docker exec -i "${CONTAINER_NAME}" mysql -u root -p'asdfasdf'

if [ $? -eq 0 ]; then
  echo "✅ 資料庫還原成功！"
else
  echo "❌ 資料庫還原失敗！"
  exit 1
fi