# 步驟1：選擇一個基礎便當盒。我們選用官方的 Node.js 18 版。
FROM node:18-alpine

# 步驟2：在便當盒裡建立一個工作區，叫做 /usr/src/app
WORKDIR /usr/src/app

# 步驟3：將「身分證」(package.json) 複製進工作區
# 我們先複製這個檔案，是為了利用 Docker 的快取機制，加速之後的建置
COPY package*.json ./

# 步驟4：安裝「外部零件」(執行 npm install)
RUN npm install

# 步驟5：將我們寫的所有程式碼複製進工作區
COPY . .

# 步驟6：告訴外界，這個便當盒的 3000 號窗口是對外服務的
EXPOSE 5000

# 步驟7：設定便當盒的「啟動指令」。當容器啟動時，會自動執行 npm start
CMD [ "npm", "start" ]
