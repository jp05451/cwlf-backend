from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
import os
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    # 初始化 logging
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'log.txt')
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
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