#!/bin/bash

# 設定變數
CONTAINER_NAME="cwlf-backend"
DB_PATH="/app/instance/site.db"  # 根據實際路徑調整
BACKUP_DIR="/home/jp05451/cwlf-backend/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="db_backup_${TIMESTAMP}.db"

# 建立備份目錄
mkdir -p ${BACKUP_DIR}

# 檢查容器是否運行
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "錯誤: 容器 ${CONTAINER_NAME} 未運行"
  exit 1
fi

# 從容器複製資料庫檔案
echo "開始備份資料庫..."
docker cp ${CONTAINER_NAME}:${DB_PATH} ${BACKUP_DIR}/${BACKUP_FILE}

# 檢查備份是否成功
if [ $? -eq 0 ]; then
  echo "備份成功: ${BACKUP_DIR}/${BACKUP_FILE}"
  
  # 刪除 7 天前的備份
  find ${BACKUP_DIR} -name "db_backup_*.db" -mtime +7 -delete
  echo "已清理 7 天前的舊備份"
else
  echo "備份失敗"
  exit 1
fi