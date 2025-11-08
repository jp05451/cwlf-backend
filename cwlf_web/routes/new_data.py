from app import db
import os
from sqlalchemy.dialects.postgresql import UUID
from models.kids import Kids
from models.parent import Parent
from models.station import Station
from models.log import LogEntry
from models.family import Family
from models.event import EventInfo, EnvUsage, EventParticipate
from config import Config
from datetime import datetime, date
from flask import Blueprint, request, jsonify,render_template
import re
import logging
import csv
import uuid
from werkzeug.utils import secure_filename
import requests


bp = Blueprint('new_data', __name__,template_folder=os.path.join(os.path.dirname(__file__), '../templates'))

# logger
logger = logging.getLogger('cwlf')


# import config
config = Config()

# 確保上傳目錄存在
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

# 檢查檔案類型的輔助函式
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def parse_time(timestamp_str):
    """解析簽到時間戳記"""
    temp = timestamp_str
    if not timestamp_str:
        return None

    try:
        s = timestamp_str.strip()

        # 處理中文上午/下午標記，僅調整時間部分的 hour
        if ('下午' in s) or ('上午' in s):
            is_pm = '下午' in s
            # 移除中文標記後但保留日期與時間
            s = s.replace('上午', '').replace('下午', '').strip()

            # 找到時間片段 (H:MM:SS 或 H:MM)
            m = re.search(r"(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?", s)
            if m:
                hour = int(m.group(1))
                minute = int(m.group(2))
                second = int(m.group(3)) if m.group(3) else 0
                # 調整上午/下午邏輯
                if is_pm and hour < 12:
                    hour += 12
                if (not is_pm) and hour == 12:
                    hour = 0
                new_time = f"{hour:02d}:{minute:02d}:{second:02d}"
                # 只替換匹配的時間段，避免改到其他包含 '4:' 的位置
                s = s[:m.start()] + new_time + s[m.end():]

        # 嘗試常見格式
        fmts = [
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M',
            '%Y/%m/%d',
            '%m/%d',
        ]
        for fmt in fmts:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue

        # 如果都失敗，回傳今天的日期（保留原始輸入供除錯）
        logger.warning(f"無法解析時間戳記: {temp} -> 經過預處理: {s}")
        return date.today()
    except Exception as e:
        logger.exception(f"無法解析時間戳記: {temp} -> {e}")
        return date.today()
def process_birthdate(birth_str):
    try:
        birth_date = datetime.strptime(birth_str, '%Y/%m/%d').date()
        return birth_date
    except ValueError:
        return None
def get_family_by_parent(parent_name, phone):
    """根據家長資訊取得"""
    # 先查詢是否已存在此家長
    clean_phone = ''.join(filter(str.isdigit, phone))

    existing_parent = Parent.query.filter_by(
        parent_name=parent_name,
        phone_num=clean_phone
    ).first()
    
    if existing_parent:
        logger.info(f"找到現有家庭: {existing_parent.family_id}")
        return existing_parent.family_id
    else:

        return None

def process_single_signin_record(row):
    timestamp = parse_time(row[0])
    station_name = row[1]
    parents_name = []
    parents_phone = []
    kids_name=[]
    kids_birth=[]
    for i in range(2,10,2):
        if(i==6):
            i+=1
        parent_name = row[i]
        parent_phone = row[i+1]
        if parent_name.strip() != '' and parent_phone.strip() != '':
            parents_name.append(parent_name)
            parents_phone.append(parent_phone)
    for i in range(11,28,3):
        kid_name = row[i]
        kid_birth = process_birthdate(row[i+1])
        if kid_name.strip() != '':
            kids_name.append(kid_name)
            kids_birth.append(kid_birth)
    family_id = get_family_by_parent(parents_name[0], parents_phone[0])
    logger.info(f"Timestamp: {timestamp}")
    logger.info(f"Station Name: {station_name}")
    logger.info(f"Parents: {list(zip(parents_name, parents_phone))}")
    logger.info(f"Kids: {list(zip(kids_name, kids_birth))}")
    if not family_id:
        logger.warning("找不到對應的家庭，跳過此筆資料")
        return
    #確保不要重複簽到
    if EnvUsage.query.filter_by(family_id=family_id, enter_time=timestamp).first():
        logger.info("此家庭已存在相同簽到時間，跳過此筆資料")
        return
    env_usage=EnvUsage(family_id=family_id, station_name=station_name, enter_time=timestamp)
    visit_log=LogEntry(visit_time=timestamp, station_name=station_name, parent_names=parents_name, phone_nums=parents_phone, kid_names=kids_name, kid_birthdays=kids_birth)
    db.session.add(env_usage)
    db.session.add(visit_log)
    db.session.commit()
    return

def process_single_register_record(row):
    timestamp = parse_time(row[0])
    station_name = row[1]
    address=row[41]
    gendermap = {
        '生理男': 'male',
        '生理女': 'female'
    }
    rolemap = {
        '父母親': 'parent',
        '(外)祖父母': 'grandparent',
    }
    parents_name = []
    parents_gender = []
    parents_role = []
    parents_phone = []
    kids_name=[]
    kids_birth=[]
    kids_gender=[]
    family_id = get_family_by_parent(row[2], row[5])
    if(family_id):
        logger.info(f"家庭已存在: {family_id}")
    else:
        family_id = uuid.uuid4()
    
    for i in range(2,18,4):
        if(i==10):
            i+=1
        parent_name = row[i]
        parent_gender= row[i+1]
        parent_role= row[i+2]
        parent_phone = row[i+3]
        if parent_name.strip() != '' and parent_phone.strip() != '' and parent_gender.strip() != '' and parent_role.strip() != '':
            parents_name.append(parent_name)
            parents_phone.append(parent_phone)
            parents_gender.append(gendermap.get(parent_gender.strip(), 'unknown'))
            parents_role.append(rolemap.get(parent_role.strip(), 'other'))
            existed_parent = Parent.query.filter_by(
            parent_name=parent_name,
            phone_num=''.join(filter(str.isdigit, parent_phone))
            ).first()
            if existed_parent:
                logger.info(f"家長已存在，跳過新增: {parent_name}, {parent_phone}")
                continue
            parent=Parent(family_id=family_id, parent_name=parent_name, 
                          register_station=station_name,
                          gender=gendermap.get(parent_gender.strip(), 'unknown'), 
                          addr=address,
                          phone_num=''.join(filter(str.isdigit, parent_phone)))
            db.session.add(parent)
            db.session.flush()
            family_relation=Family(family_id=family_id, member_id=parent.member_id,member_role=rolemap.get(parent_role.strip(), 'other'))
            db.session.add(family_relation)
    for i in range(19,39,3):
        #  如果開頭是是否還有其他...
        if row[i].startswith('是否還有其他'):
            i+=1
        kid_name = row[i]
        kid_birth = process_birthdate(row[i+1])
        kid_gender = gendermap.get(row[i+2].strip(), 'unknown')
        if kid_name.strip() != '' and kid_birth is not None and kid_gender is not None:
            kids_name.append(kid_name)
            kids_birth.append(kid_birth)
            kids_gender.append(kid_gender)
            existed_kid = Kids.query.filter_by(
                family_id=family_id,
                kids_name=kid_name,
                BRD=kid_birth
            ).first()
            if existed_kid:
                logger.info(f"小孩已存在，跳過新增: {kid_name}, {kid_birth}")
                continue
            kid=Kids(family_id=family_id, kids_name=kid_name, BRD=kid_birth, gender=kid_gender)
            db.session.add(kid)
            db.session.flush()
            family_relation=Family(family_id=family_id, member_id=kid.member_id,member_role='kid')
            db.session.add(family_relation)
    logger.info(f"Timestamp: {timestamp}")
    logger.info(f"Station Name: {station_name}")
    logger.info(f"Address: {address}")
    logger.info(f"Parents: {list(zip(parents_name, parents_gender, parents_role, parents_phone))}")
    logger.info(f"Kids: {list(zip(kids_name, kids_birth, kids_gender))}")
    db.session.commit()
    return

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if(len(row) == 47):
                if(row[0]=='時間戳記'):
                    continue
                process_single_register_record(row)
            elif(len(row) == 28):
                if(row[0]=='時間戳記'):
                    continue
                process_single_signin_record(row)
            else:
                logger.warning(f"未知的行格式:{row} {len(row)}")
    # remove file
    #os.remove(filepath)
    return

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload_file():
    # 檢查請求中是否有檔案
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # 檢查檔案類型（可選）
    try:

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(config.UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # 解析上傳的 CSV 檔案
                # parse_family_info_data(filepath)
            return jsonify({
                'message': 'File uploaded and processed successfully',
                'filename': filename
            }), 200
        else:
            return jsonify({'error': 'File type not allowed'}), 400

    except Exception as e:
        return jsonify({
            'error': f'File uploaded but processing failed: {str(e)}'
        }), 500

# 新增：處理上傳檔案的 route
@bp.route('/process_uploaded_file', methods=['POST'])
def process_uploaded_file():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({'success': False, 'error': 'No filename provided'}), 400
    filepath = os.path.join(config.UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'error': 'File not found'}), 404
    try:
        logger.info(f"正在處理檔案: {filepath}")
        process_file(filepath)
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.exception(f"處理檔案失敗: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/health', methods=['GET'])
def health_check():
    """檢查 cwlf-backend-monitor 服務的健康狀態"""
    try:
        # 向 cwlf-backend-monitor 服務發送請求
        response = requests.get('http://cwlf-backend-monitor:3000/health', timeout=5)

        if response.status_code == 200:
            return jsonify({
                'status': 'ok',
                'monitor_service': 'healthy'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'monitor_service': 'unhealthy',
                'status_code': response.status_code
            }), 503

    except requests.exceptions.Timeout:
        logger.error("Monitor service health check timeout")
        return jsonify({
            'status': 'error',
            'monitor_service': 'timeout'
        }), 503

    except requests.exceptions.ConnectionError:
        logger.error("Monitor service connection error")
        return jsonify({
            'status': 'error',
            'monitor_service': 'unreachable'
        }), 503

    except Exception as e:
        logger.exception(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'monitor_service': 'error',
            'message': str(e)
        }), 503
