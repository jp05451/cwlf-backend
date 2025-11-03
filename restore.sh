#!/bin/bash

# 設定變數
CONTAINER_NAME="cwlf-backend"
DB_PATH="/app/instance/site.db"
BACKUP_DIR="/home/jp05451/cwlf-backend/backups"

# 檢查是否提供備份檔案參數
if [ -z "$1" ]; then
  echo "使用方式: $0 <備份檔案名稱>"
  echo ""
  echo "可用的備份檔案:"
  ls -1 ${BACKUP_DIR}/db_backup_*.db 2>/dev/null | xargs -n 1 basename || echo "  沒有找到備份檔案"
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
echo "警告: 此操作將覆蓋現有資料庫！"
echo "備份檔案: ${BACKUP_FILE}"
echo "目標容器: ${CONTAINER_NAME}"
read -p "確定要繼續嗎? (yes/no): " confirmation

if [ "$confirmation" != "yes" ]; then
  echo "已取消還原操作"
  exit 0
fi

# 停止應用程式服務 (可選,取決於你的應用程式)
echo "正在還原資料庫..."

# 複製備份檔案到容器
docker cp ${BACKUP_PATH} ${CONTAINER_NAME}:${DB_PATH}

# 檢查還原是否成功
if [ $? -eq 0 ]; then
  echo "還原成功: ${BACKUP_FILE} -> ${DB_PATH}"
  echo "建議重啟容器以確保變更生效:"
  echo "  docker restart ${CONTAINER_NAME}"
else
  echo "還原失敗"
  exit 1
fi
