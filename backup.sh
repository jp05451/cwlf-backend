#!/bin/bash

# 設定變數
CONTAINER_NAME="mysql_db"
# 載入環境變數
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi
# echo "使用的 MySQL Root 使用者: ${MYSQL_ROOT_USER}"
# echo "使用的 MySQL Root 密碼: ${MYSQL_ROOT_PASSWORD}"

DB_USER=${MYSQL_ROOT_USER}
DB_PASSWORD=${MYSQL_ROOT_PASSWORD}  # 請替換為實際密碼
DB_NAME="cwlf_db"  # 請替換為實際資料庫名稱
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="mysql_backup_${TIMESTAMP}.sql"

# 建立備份目錄
mkdir -p ${BACKUP_DIR}

# 檢查容器是否運行
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "錯誤: 容器 ${CONTAINER_NAME} 未運行"
  exit 1
fi

# 備份 MySQL 資料庫
echo "開始備份 MySQL 資料庫..."
docker exec ${CONTAINER_NAME} mysqldump -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME} > ${BACKUP_DIR}/${BACKUP_FILE}

# 檢查備份是否成功
if [ $? -eq 0 ]; then
  echo "備份成功: ${BACKUP_DIR}/${BACKUP_FILE}"
  
  # 壓縮備份檔案
  gzip ${BACKUP_DIR}/${BACKUP_FILE}
  echo "已壓縮備份檔案"
  
  # 刪除 7 天前的備份
  find ${BACKUP_DIR} -name "mysql_backup_*.sql.gz" -mtime +7 -delete
  echo "已清理 7 天前的舊備份"
else
  echo "備份失敗"
  exit 1
fi