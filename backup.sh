#!/bin/bash

# --- 可設定的變數 ---
# 你的 Docker 容器名稱
CONTAINER_NAME="mysql-compose"
# 備份檔案要存放的目錄 (在專案根目錄下建立一個 backups 資料夾)
BACKUP_DIR="$(pwd)/backups"
# --- ---

# 建立一個以日期和時間命名的備份檔案，例如：backup-20240803-153000.sql
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
FILENAME="${BACKUP_DIR}/backup-${TIMESTAMP}.sql"

# 確保備份目錄存在，如果不存在就建立它
mkdir -p "${BACKUP_DIR}"

echo "正在備份資料庫從容器 ${CONTAINER_NAME}..."
echo "備份檔案將儲存至: ${FILENAME}"

# 執行我們熟悉的 mysqldump 指令
# 使用 docker exec 在指定的容器內執行備份指令
# 並將結果導向到我們剛剛定義的檔案中
docker exec "${CONTAINER_NAME}" mysqldump -u root -p'asdfasdf' --all-databases > "${FILENAME}"

# 檢查上一個指令是否成功
if [ $? -eq 0 ]; then
  echo "✅ 資料庫備份成功！"
else
  echo "❌ 資料庫備份失敗！"
  exit 1
fi