#!/bin/bash

# 設定變數
CONTAINER_NAME="mysql_db"
# 載入環境變數
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi

DB_USER=${MYSQL_ROOT_USER:-root}
DB_PASSWORD=${MYSQL_ROOT_PASSWORD}
DB_NAME="cwlf_db"
BACKUP_DIR="./backups"

# 檢查是否提供備份檔案參數
if [ -z "$1" ]; then
  echo "使用方式: $0 <備份檔案名稱>"
  echo ""
  echo "可用的備份檔案:"
  ls -1 ${BACKUP_DIR}/mysql_backup_*.sql* 2>/dev/null | xargs -n 1 basename || echo "  沒有找到備份檔案"
  exit 1
fi

# 處理輸入參數，如果是完整路徑則提取檔案名稱
BACKUP_FILE=$(basename "$1")
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILE}"

# 檢查備份檔案是否存在
if [ ! -f "${BACKUP_PATH}" ]; then
  echo "錯誤: 備份檔案 ${BACKUP_FILE} 不存在於 ${BACKUP_DIR}"
  exit 1
fi

# 檢查容器是否運行
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "錯誤: 容器 ${CONTAINER_NAME} 未運行"
  exit 1
fi

# 確認還原操作
echo "警告: 此操作將覆蓋現有資料庫 ${DB_NAME}！"
echo "備份檔案: ${BACKUP_FILE}"
echo "目標容器: ${CONTAINER_NAME}"
echo "目標資料庫: ${DB_NAME}"
read -p "確定要繼續嗎? (yes/no): " confirmation

if [ "$confirmation" != "yes" ]; then
  echo "已取消還原操作"
  exit 0
fi

# 準備還原
echo "正在還原資料庫..."

# 檢查檔案是否為壓縮檔
TEMP_FILE="${BACKUP_PATH}"
if [[ "${BACKUP_FILE}" == *.gz ]]; then
  echo "偵測到壓縮檔案，正在解壓縮..."
  TEMP_FILE="${BACKUP_DIR}/temp_restore.sql"
  gunzip -c ${BACKUP_PATH} > ${TEMP_FILE}
  if [ $? -ne 0 ]; then
    echo "解壓縮失敗"
    exit 1
  fi
fi

# 還原資料庫
# 方法 1: 使用 docker exec 直接導入
if [[ "${BACKUP_FILE}" == *.gz ]]; then
  gunzip -c ${BACKUP_PATH} | docker exec -i ${CONTAINER_NAME} mysql -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME}
else
  docker exec -i ${CONTAINER_NAME} mysql -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME} < ${BACKUP_PATH}
fi

# 檢查還原是否成功
if [ $? -eq 0 ]; then
  echo "還原成功: ${BACKUP_FILE} -> ${DB_NAME}"
  echo ""
  echo "資料庫已成功還原。建議執行以下操作:"
  echo "1. 檢查資料庫內容:"
  echo "   docker exec -it ${CONTAINER_NAME} mysql -u${DB_USER} -p${DB_PASSWORD} -e 'USE ${DB_NAME}; SHOW TABLES;'"
  echo ""
  echo "2. 若需要，重啟相關應用容器:"
  echo "   docker-compose restart cwlf_web"
  
  # 清理臨時檔案
  if [[ "${BACKUP_FILE}" == *.gz ]] && [ -f "${TEMP_FILE}" ]; then
    rm -f ${TEMP_FILE}
    echo ""
    echo "已清理臨時解壓檔案"
  fi
else
  echo "還原失敗"
  # 清理臨時檔案
  if [[ "${BACKUP_FILE}" == *.gz ]] && [ -f "${TEMP_FILE}" ]; then
    rm -f ${TEMP_FILE}
  fi
  exit 1
fi
