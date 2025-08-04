// 引入我們需要的函式庫
const express = require('express');
const mysql = require('mysql2/promise');
const amqp = require('amqplib');

// 建立一個 Express 應用程式
const app = express();
const PORT = 3000; // 應用程式將在這個 port 運作

// --- 從「環境變數」讀取資料庫和 RabbitMQ 的連線資訊 ---
// 這是容器化應用程式的最佳實踐！我們不會把密碼寫死在程式碼裡。
// 這些變數將由 docker-compose.yml 檔案傳遞進來。
const dbConfig = {
    host: process.env.MYSQL_HOST,
    user: process.env.MYSQL_USER,
    password: process.env.MYSQL_ROOT_PASSWORD,
    database: process.env.MYSQL_DATABASE
};

const rabbitmqConfig = {
    hostname: process.env.RABBITMQ_HOST,
    username: process.env.RABBITMQ_DEFAULT_USER,
    password: process.env.RABBITMQ_DEFAULT_PASS
};

// 這是主路由，當我們訪問網站首頁時會觸發
app.get('/', async (req, res) => {
    let dbStatus = 'Disconnected';
    let rabbitStatus = 'Disconnected';

    // 測試 MySQL 連線
    try {
        const connection = await mysql.createConnection(dbConfig);
        await connection.ping(); // 嘗試 ping 一下資料庫
        dbStatus = 'Connected Successfully!';
        await connection.end();
    } catch (error) {
        dbStatus = `Failed to connect: ${error.message}`;
    }

    // 測試 RabbitMQ 連線
    try {
        const connection = await amqp.connect(rabbitmqConfig);
        rabbitStatus = 'Connected Successfully!';
        await connection.close();
    } catch (error) {
        rabbitStatus = `Failed to connect: ${error.message}`;
    }

    // 在網頁上顯示結果
    res.send(`
        <h1>CWLF Backend Status</h1>
        <p><strong>MySQL Database Status:</strong> ${dbStatus}</p>
        <p><strong>RabbitMQ Service Status:</strong> ${rabbitStatus}</p>
    `);
});

// 啟動我們的網頁伺服器
app.listen(PORT, () => {
    console.log(`CWLF backend app listening on port ${PORT}`);
    console.log('Connecting with the following config:');
    console.log('DB Host:', dbConfig.host);
    console.log('RabbitMQ Host:', rabbitmqConfig.hostname);
});
