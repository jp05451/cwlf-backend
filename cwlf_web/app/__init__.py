from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
import pytz

db = SQLAlchemy()
migrate = Migrate()

# 設定台北時區
TAIPEI_TZ = pytz.timezone('Asia/Taipei')

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # 設定環境變數時區
    os.environ['TZ'] = 'Asia/Taipei'
    
    # 初始化 logging
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'log.txt')
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    
    # 自訂 formatter 使用台北時區
    class TaipeiFormatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            dt = datetime.fromtimestamp(record.created, tz=TAIPEI_TZ)
            if datefmt:
                return dt.strftime(datefmt)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
    
    formatter = TaipeiFormatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    logger = logging.getLogger('cwlf')
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        logger.addHandler(handler)
    # 也將 flask 的 logger 指向同一個 handler
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    db.init_app(app)
    migrate.init_app(app, db)
    from routes import db_init , new_data
    app.register_blueprint(new_data.bp)
    app.register_blueprint(db_init.bp)
    return app