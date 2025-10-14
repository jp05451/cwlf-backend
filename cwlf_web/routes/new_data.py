from app import db
import os
from sqlalchemy.dialects.postgresql import UUID
from models.kids import Kids
from models.parent import Parent
from models.station import Station
from models.family import Family
from models.event import EventInfo, EnvUsage, EventParticipate
from config import Config
from datetime import datetime, date
from flask import Blueprint, request, jsonify,render_template
import csv
import uuid
from werkzeug.utils import secure_filename

bp = Blueprint('new_data', __name__,template_folder=os.path.join(os.path.dirname(__file__), '../templates'))

# import config
config = Config()





# 確保上傳目錄存在
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

# 檢查檔案類型的輔助函式
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload_file():
    # 檢查請求中是否有檔案
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # 檢查是否有選擇檔案
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # 檢查檔案類型（可選）
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename
        }), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400