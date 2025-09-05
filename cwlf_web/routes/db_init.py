from app import db
from sqlalchemy.dialects.postgresql import UUID
from models.kids import Kids
from models.parent import Parent
from models.station import Station
from models.family import Family
from models.event import EventInfo, EnvUsage, EventParticipate
from config import Config
from datetime import datetime, date
from flask import Blueprint, request, jsonify
import hashlib
import csv
import uuid

bp = Blueprint('db_init', __name__)

def parse_event_info_data():
    """解析 event_info.csv 並導入 d_event_info 資料庫"""
    default_data_path = 'test/'
    event_info_data = f'{default_data_path}event_info.csv'
    
    print(f"正在讀取檔案: {event_info_data}")
    processed_rows = 0
    
    with open(event_info_data, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row_index, row in enumerate(reader):
            print(f"處理第 {row_index + 1} 行")
            
            # 跳過說明行和空行
            if (not row.get('活動名稱') or 
                row['活動名稱'] in ['活動名稱', '說明'] or
                row.get('欄位') == '欄位' or
                row['活動名稱'].strip() == ''):
                print(f"跳過第 {row_index + 1} 行")
                continue
            
            # 使用單筆活動資料處理函數
            success = process_single_event_record(row)
            if success:
                processed_rows += 1
    
    print(f"成功處理 {processed_rows} 行資料，event_info.csv 資料導入完成")

def process_single_event_record(row_data):
    """處理單筆活動記錄"""
    try:
        # 解析基本資料
        event_name = str(row_data.get('活動名稱', '')).strip()
        event_category = str(row_data.get('活動分類', '')).strip()
        event_description = str(row_data.get('活動敘述', '')).strip()
        prior_event_name = str(row_data.get('需事先參與過的活動名稱', '')).strip()
        register_necessary_str = str(row_data.get('是否需事先報名', '')).strip()
        event_start_time_str = str(row_data.get('活動起始時間', '')).strip()
        event_end_time_str = str(row_data.get('活動結束時間', '')).strip()
        
        print(f"處理活動資料: {event_name}, 分類: {event_category}")
        if not event_name or not event_category:
            print(f"缺少必要資料，跳過此記錄")
            return False
        
        # 處理是否需要報名
        register_necessary = register_necessary_str == '是'
        # 處理前置活動需求
        prior_event_id = get_prior_event_id(prior_event_name)
        
        # 取得預設站點ID (假設有一個預設站點)
        station_id = get_default_station_id()
        # 解析活動時間
        event_start_date = parse_event_datetime(event_start_time_str)
        event_end_date = parse_event_datetime(event_end_time_str, is_end_time=True)
        
        # 如果沒有結束時間，設定為開始時間加1.5小時
        if event_start_date and not event_end_date:
            from datetime import timedelta
            event_end_date = event_start_date + timedelta(hours=1, minutes=30)
        
        # 建立 EventInfo 記錄
        event_info = EventInfo(
            event_name=event_name,
            event_category=event_category,
            event_description=event_description if event_description else None,
            prior_event_id=prior_event_id,
            station_id=station_id,
            register_necessary=register_necessary,
            event_start_date=event_start_date,
            event_end_date=event_end_date
        )
        
        db.session.add(event_info)
        db.session.commit()
        
        print(f"新增活動: {event_name}")
        return True
        
    except Exception as e:
        print(f"處理活動記錄時發生錯誤: {e}")
        db.session.rollback()
        return False

def get_prior_event_id(prior_event_name):
    """取得前置活動ID"""
    if not prior_event_name or prior_event_name == '無':
        # 如果沒有前置活動，返回一個特殊的UUID (可以是null或預設值)
        return None
    
    # 根據活動分類來查找前置活動
    category_mapping = {
        '回應式照顧家長團體-初階': None,
        '回應式照顧家長團體-中階': '回應式照顧家長團體-初階',
        '回應式照顧家長團體-進階': '回應式照顧家長團體-中階'
    }
    
    if prior_event_name in category_mapping:
        if category_mapping[prior_event_name] is None:
            return None
        else:
            # 查找對應分類的任一活動ID
            prior_event = EventInfo.query.filter_by(
                event_category=category_mapping[prior_event_name]
            ).first()
            if prior_event:
                return prior_event.event_id
    
    return None

def get_default_station_id():
    """取得預設站點ID"""
    # 先查看是否有站點存在
    station = Station.query.first()
    if station:
        return station.station_id
    else:
        # 如果沒有站點，建立一個預設站點
        default_station = Station(
            station_name='萬華親子館',
            category='育兒+',
            addr='台北市萬華區',
            enable=True
        )
        db.session.add(default_station)
        db.session.flush()
        return default_station.station_id

def parse_event_datetime(datetime_str, is_end_time=False):
    """解析活動時間"""
    if not datetime_str or datetime_str.strip() == '':
        return None
    
    try:
        # 處理各種日期時間格式
        datetime_str = str(datetime_str.strip())
        # 如果只有日期沒有時間
        if len(datetime_str) == 10 and '-' in datetime_str:
            # YYYY-MM-DD 格式
            date_part = datetime.strptime(datetime_str, '%Y-%m-%d').date()
            if is_end_time:
                # 結束時間設為當天 17:00
                return datetime.combine(date_part, datetime.min.time().replace(hour=17))
            else:
                # 開始時間設為當天 10:00
                return datetime.combine(date_part, datetime.min.time().replace(hour=10))
        
        # 嘗試不同的日期時間格式
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M',
            '%Y-%m-%d',
            '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                parsed_datetime = datetime.strptime(datetime_str, fmt)
                # 如果只解析到日期，補充時間
                if fmt in ['%Y-%m-%d', '%Y/%m/%d']:
                    if is_end_time:
                        parsed_datetime = parsed_datetime.replace(hour=17, minute=0)
                    else:
                        parsed_datetime = parsed_datetime.replace(hour=10, minute=0)
                return parsed_datetime
            except ValueError:
                continue
        
        print(f"無法解析時間格式: {datetime_str}")
        return None
        
    except Exception as e:
        print(f"解析時間時發生錯誤: {datetime_str} -> {e}")
        return None

def parse_event_join_data():
    """解析 event_join.csv 並導入資料庫"""
    default_data_path = 'test/'
    event_join_data = f'{default_data_path}event_join.csv'
    
    print(f"正在讀取檔案: {event_join_data}")
    processed_rows = 0
    
    with open(event_join_data, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row_index, row in enumerate(reader):
            print(f"處理第 {row_index + 1} 行")
            
            # 跳過說明行和空行
            if (not row.get('活動名稱') or 
                row['活動名稱'] in ['活動名稱', '說明'] or
                row.get('欄位') == '欄位'):
                print(f"跳過第 {row_index + 1} 行")
                continue
            
            # 使用單筆資料處理函數
            success = process_single_record(row)
            if success:
                processed_rows += 1
    
    print(f"成功處理 {processed_rows} 行資料，event_join.csv 資料導入完成")

def process_single_record(row_data):
    """處理單筆記錄"""
    try:
        # 解析基本資料
        event_name = row_data.get('活動名稱', '').strip()
        timestamp = row_data.get('時間戳記(報名時間)', '').strip()
        parent1_name = row_data.get('家長1-姓名', '').strip()
        parent2_name = row_data.get('家長2-姓名', '').strip()
        phone = row_data.get('聯絡電話', '').strip()
        addr = row_data.get('居住地', '').strip()
        
        print(f"處理資料: event={event_name}, parent1={parent1_name}, phone={phone}")
        
        if not parent1_name or not phone or not event_name:
            print(f"缺少必要資料，跳過此記錄")
            return False
        
        # 清理電話號碼
        phone = phone.replace('-', '').replace(' ', '')
        
        # 取得或建立 family_id
        family_id = get_or_create_family_by_parent(parent1_name, phone)
        
        # 處理家長1
        parent1_id = get_or_create_parent(family_id, parent1_name, phone, addr)
        print(f"處理家長1: {parent1_name} -> {parent1_id}")
        
        # 處理家長2（如果存在）
        if parent2_name and parent2_name.strip():
            parent2_id = get_or_create_parent(family_id, parent2_name, phone, addr)
            print(f"處理家長2: {parent2_name} -> {parent2_id}")
        
        # 處理兒童（最多4個）
        for i in range(1, 5):
            child_name = row_data.get(f'兒童{i}-姓名', '').strip()
            child_gender = row_data.get(f'兒童{i}-性別', '').strip()
            child_birth = row_data.get(f'兒童{i}-出生年月日', '').strip()
            
            if child_name and child_birth:
                child_id = get_or_create_child(family_id, child_name, child_gender, child_birth)
                print(f"處理兒童{i}: {child_name} -> {child_id}")
        
        # 提交這筆記錄的變更
        db.session.commit()
        return True
        
    except Exception as e:
        print(f"處理記錄時發生錯誤: {e}")
        db.session.rollback()
        return False

def get_or_create_family_by_parent(parent_name, phone):
    """根據家長資訊取得或建立家庭"""
    # 先查詢是否已存在此家長
    clean_phone = ''.join(filter(str.isdigit, phone))
    phone_int = int(clean_phone) if clean_phone else 0
    
    existing_parent = Parent.query.filter_by(
        parent_name=parent_name,
        phone_num=phone_int
    ).first()
    
    if existing_parent:
        print(f"找到現有家庭: {existing_parent.family_id}")
        return existing_parent.family_id
    else:
        # 建立新的家庭ID
        new_family_id = uuid.uuid4()
        print(f"建立新家庭: {new_family_id}")
        return new_family_id

def get_or_create_parent(family_id, parent_name, phone, addr):
    """取得或建立家長記錄"""
    clean_phone = ''.join(filter(str.isdigit, phone))
    
    # 檢查是否已存在
    existing_parent = Parent.query.filter_by(
        parent_name=parent_name,
        phone_num=clean_phone
    ).first()
    
    if existing_parent:
        print(f"家長已存在: {parent_name}")
        return existing_parent.member_id
    
    try:
        # 產生身分證後四碼（模擬）
        id_last4 = abs(hash(parent_name + phone)) % 10000
        
        # 建立 Parent 記錄
        parent = Parent(
            family_id=family_id,
            parent_name=parent_name,
            phone_num=clean_phone,
            id_last4=None,
            addr=addr
        )
        
        db.session.add(parent)
        db.session.flush()  # 取得 member_id
        
        # 建立 Family 關聯記錄
        family_relation = Family(
            family_id=family_id,
            member_id=parent.member_id,
            member_role='parent'
        )
        db.session.add(family_relation)
        
        print(f"新增家長: {parent_name}")
        return parent.member_id
        
    except Exception as e:
        print(f"建立家長記錄時發生錯誤: {e}")
        raise e

def get_or_create_child(family_id, child_name, gender, birth_str):
    """取得或建立兒童記錄"""
    if not birth_str or not child_name:
        return None
    
    try:
        # 解析生日
        birth_date = parse_birth_date(birth_str)
        if not birth_date:
            print(f"無法解析生日: {birth_str}")
            return None
        
        # 檢查是否已存在相同姓名、生日和家庭的兒童
        existing_child = Kids.query.filter_by(
            family_id=family_id,
            kids_name=child_name,
            BRD=birth_date
        ).first()
        
        if existing_child:
            print(f"兒童已存在: {child_name} ({birth_date}) in family {family_id}")
            return existing_child.member_id
        
        # 標準化性別
        gender_map = {'男': 'male', '女': 'female'}
        gender = gender_map.get(gender, 'unknow')
        
        # 建立 Kids 記錄
        kid = Kids(
            family_id=family_id,
            gender=gender,
            kids_name=child_name,
            BRD=birth_date
        )
        
        db.session.add(kid)
        db.session.flush()  # 取得 member_id
        
        # 建立 Family 關聯記錄
        family_relation = Family(
            family_id=family_id,
            member_id=kid.member_id,
            member_role='kids'
        )
        db.session.add(family_relation)
        
        print(f"新增兒童: {child_name} ({birth_date})")
        return kid.member_id
        
    except Exception as e:
        print(f"處理兒童資料時發生錯誤: {e}")
        raise e

def parse_birth_date(birth_str):
    """解析生日"""
    if not birth_str:
        return None
    
    try:
        # 嘗試不同的日期格式
        for fmt in ['%Y/%m/%d', '%Y-%m-%d']:
            try:
                return datetime.strptime(birth_str, fmt).date()
            except ValueError:
                continue
        return None
    except:
        return None

def parse_sign_in_data():
    """解析 sign_in.csv 並導入資料庫"""
    default_data_path = 'test/'
    sign_in_data = f'{default_data_path}sign_in.csv'
    
    print(f"正在讀取檔案: {sign_in_data}")
    processed_rows = 0
    
    with open(sign_in_data, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        
        for row_index, row in enumerate(csv_reader):
            print(f"處理第 {row_index + 1} 行")
            
            # 跳過空行或無效行
            if not row or len(row) < 18:
                print(f"跳過第 {row_index + 1} 行 - 資料不完整")
                continue
            
            # 使用單筆簽到記錄處理函數
            success = process_single_signin_record(row)
            if success:
                processed_rows += 1
    
    print(f"成功處理 {processed_rows} 行資料，sign_in.csv 資料導入完成")

def process_single_signin_record(row_data):
    """處理單筆簽到記錄"""
    try:
        # 從CSV行中解析資料
        if len(row_data) < 18:
            return False
            
        timestamp = row_data[1].strip() if len(row_data) > 1 else ''
        guardian_name = row_data[2].strip() if len(row_data) > 2 else ''
        guardian_gender = row_data[3].strip() if len(row_data) > 3 else ''
        guardian_relation = row_data[4].strip() if len(row_data) > 4 else ''
        guardian2_name = row_data[5].strip() if len(row_data) > 5 else ''
        guardian2_gender = row_data[6].strip() if len(row_data) > 6 else ''
        guardian2_relation = row_data[7].strip() if len(row_data) > 7 else ''
        phone = row_data[8].strip() if len(row_data) > 8 else ''
        is_member = row_data[9].strip() if len(row_data) > 9 else ''
        addr = row_data[10].strip() if len(row_data) > 10 else ''
        
        # 兒童資料從第11欄開始，每3欄一組 (姓名、性別、年齡/生日)
        children_data = []
        for i in range(11, min(len(row_data), 20), 3):
            child_name = row_data[i].strip() if i < len(row_data) else ''
            child_gender = row_data[i+1].strip() if i+1 < len(row_data) else ''
            child_age_birth = row_data[i+2].strip() if i+2 < len(row_data) else ''
            
            if child_name and child_age_birth:
                children_data.append({
                    'name': child_name,
                    'gender': child_gender,
                    'age_birth': child_age_birth
                })
        
        print(f"處理簽到資料: {guardian_name}, 手機: {phone}, 兒童數: {len(children_data)}")
        
        # 驗證必要資料
        if not guardian_name or not phone:
            print(f"缺少必要資料，跳過此記錄")
            return False
        
        # 清理電話號碼
        phone = phone.replace('-', '').replace(' ', '')
        if not phone:
            print(f"無效的電話號碼，跳過此記錄")
            return False
        
        # 取得簽到日期，用於計算生日
        signin_date = parse_signin_date(timestamp)
        
        # 取得或建立 family_id
        family_id = get_or_create_family_by_guardian(guardian_name, phone)
        
        # 處理主要監護人
        guardian_id = get_or_create_parent(family_id, guardian_name, phone, addr)
        print(f"處理監護人: {guardian_name} -> {guardian_id}")
        
        # 處理第二監護人（如果存在）
        if guardian2_name and guardian2_name.strip():
            guardian2_id = get_or_create_parent(family_id, guardian2_name, phone, addr)
            print(f"處理第二監護人: {guardian2_name} -> {guardian2_id}")
        
        # 處理兒童資料
        for idx, child_data in enumerate(children_data):
            child_birth = convert_age_to_birth_date(child_data['age_birth'], signin_date)
            if child_birth:
                child_id = get_or_create_child_from_signin(
                    family_id, 
                    child_data['name'],
                    child_data['gender'], 
                    child_birth
                )
                print(f"處理兒童{idx+1}: {child_data['name']} -> {child_id}")
        
        # 提交這筆記錄的變更
        db.session.commit()
        return True
        
    except Exception as e:
        print(f"處理簽到記錄時發生錯誤: {e}")
        db.session.rollback()
        return False

def parse_signin_date(timestamp_str):
    """解析簽到時間戳記"""
    if not timestamp_str:
        return None
    
    try:
        # 嘗試不同的日期格式
        for fmt in ['%Y/%m/%d 上午 %H:%M:%S', '%Y/%m/%d 下午 %H:%M:%S', 
                   '%Y/%m/%d', '%m/%d', '%Y/%m/%d 上午', '%Y/%m/%d 下午']:
            try:
                if '下午' in timestamp_str and '12:' not in timestamp_str:
                    # 處理下午時間，需要加12小時
                    timestamp_str = timestamp_str.replace('下午', '').strip()
                    if ':' in timestamp_str:
                        time_part = timestamp_str.split()[-1]
                        if ':' in time_part:
                            hour = int(time_part.split(':')[0])
                            if hour < 12:
                                timestamp_str = timestamp_str.replace(f'{hour}:', f'{hour+12}:')
                
                timestamp_str = timestamp_str.replace('上午', '').replace('下午', '').strip()
                return datetime.strptime(timestamp_str, fmt.replace(' 上午', '').replace(' 下午', '')).date()
            except ValueError:
                continue
        
        # 如果都失敗，回傳今天的日期
        return date.today()
    except:
        return date.today()

def convert_age_to_birth_date(age_str, signin_date):
    """將年齡字串轉換為出生日期"""
    if not age_str or not signin_date:
        return None
    
    try:
        # 如果已經是日期格式 (YYYY/MM/DD)
        if '/' in age_str and len(age_str.split('/')) == 3:
            return parse_birth_date(age_str)
        
        # 解析年齡格式
        age_str = age_str.replace('歲', 'y').replace('個月', 'm').replace('月', 'm').strip()
        
        years = 0
        months = 0
        
        # 處理各種年齡格式
        if 'y' in age_str.lower():
            # 例如 "2y6m", "1y", "3y 4m" "8m"
            parts = age_str.lower().split('y')
            if len(parts) >= 1 and parts[0].strip().isdigit():
                years = int(parts[0].strip())
            if len(parts) == 2 and 'm' in parts[1]:
                months_part = parts[1].split('m')[0].strip()
                if months_part.isdigit():
                    months = int(months_part)
        else:
            # 提取數字
            import re
            numbers = re.findall(r'\d+', age_str)
            if len(numbers) >= 2:
                years = int(numbers[0])
                months = int(numbers[1])
            elif len(numbers) == 1:
                # 如果只有一個數字，判斷是年還是月
                if '月' in age_str or 'm' in age_str.lower():
                    months = int(numbers[0])
                    if(months > 12):
                        years += months // 12
                        months = months % 12
                else:
                    years = int(numbers[0])
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        
        # 計算出生日期：簽到日期減去年齡
        birth_date = signin_date - relativedelta(years=years, months=months)
        
        print(f"年齡轉換: {age_str} -> {years}年{months}月 -> 出生日期: {birth_date}")
        
        return birth_date
        
    except Exception as e:
        print(f"轉換年齡時發生錯誤: {age_str} -> {e}")
        # 如果出錯，嘗試簡單計算
        try:
            import re
            numbers = re.findall(r'\d+', age_str)
            if numbers:
                years = int(numbers[0])
                estimated_birth_year = signin_date.year - years
                return signin_date.replace(year=estimated_birth_year)
        except:
            pass
        return None
    
def get_or_create_family_by_guardian(guardian_name, phone):
    """根據監護人資訊取得或建立家庭"""
    clean_phone = ''.join(filter(str.isdigit, phone))
    
    existing_parent = Parent.query.filter_by(
        parent_name=guardian_name,
        phone_num=phone
    ).first()
    
    if existing_parent:
        print(f"找到現有家庭: {existing_parent.family_id}")
        return existing_parent.family_id
    else:
        new_family_id = uuid.uuid4()
        print(f"建立新家庭: {new_family_id}")
        return new_family_id

def get_or_create_child_from_signin(family_id, child_name, gender, birth_date):
    """從簽到資料取得或建立兒童記錄"""
    if not birth_date or not child_name:
        return None
    
    try:
        # 檢查是否已存在相同姓名、生日和家庭的兒童
        existing_child = Kids.query.filter_by(
            family_id=family_id,
            kids_name=child_name,
            BRD=birth_date
        ).first()
        
        if existing_child:
            print(f"兒童已存在: {child_name} ({birth_date}) in family {family_id}")
            return existing_child.member_id
        
        # 標準化性別
        gender_map = {'男': 'male', '女': 'female'}
        gender = gender_map.get(gender, 'unknown')
        
        # 建立 Kids 記錄
        kid = Kids(
            family_id=family_id,
            gender=gender,
            kids_name=child_name,
            BRD=birth_date
        )
        
        db.session.add(kid)
        db.session.flush()  # 取得 member_id
        
        # 建立 Family 關聯記錄
        family_relation = Family(
            family_id=family_id,
            member_id=kid.member_id,
            member_role='kids'
        )
        db.session.add(family_relation)
        
        print(f"新增兒童: {child_name} ({birth_date})")
        return kid.member_id
        
    except Exception as e:
        print(f"處理兒童資料時發生錯誤: {e}")
        raise e

# 新增路由
@bp.route('/import_signin_data', methods=['GET'])
def import_signin_data():
    """導入簽到資料"""
    parse_sign_in_data()
    return "Sign-in data imported successfully"

@bp.route('/add_single_signin_record', methods=['POST'])
def add_single_signin_record():
    """新增單筆簽到記錄的 API"""
    try:
        data = request.get_json()
        
        # 驗證必要欄位
        required_fields = ['時間戳記(報名時間)', '監護人姓名', '聯絡電話']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必要欄位: {field}'}), 400
        
        success = process_single_signin_record(data)
        
        if success:
            return jsonify({'message': '簽到記錄新增成功'}), 200
        else:
            return jsonify({'error': '簽到記錄新增失敗'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# 路由定義
@bp.route('/default_db', methods=['GET'])
def default_db():
    """重置資料庫並導入所有資料"""
    db.drop_all()
    db.create_all()
    parse_event_join_data()
    parse_sign_in_data()
    parse_event_info_data()
    return "Default database initialized successfully"

@bp.route('/import_event_join_data', methods=['GET'])
def import_event_join_data():
    """僅導入新資料，不重置資料庫"""
    parse_event_join_data()
    return "New data imported successfully"

@bp.route('/add_single_record', methods=['POST'])
def add_single_record():
    """新增單筆記錄的 API"""
    try:
        data = request.get_json()
        
        # 驗證必要欄位
        required_fields = ['活動名稱', '家長1-姓名', '聯絡電話']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必要欄位: {field}'}), 400
        
        success = process_single_record(data)
        
        if success:
            return jsonify({'message': '記錄新增成功'}), 200
        else:
            return jsonify({'error': '記錄新增失敗'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/show_db', methods=['GET'])
def show_db():
    tables = db.metadata.tables
    result = {}
    for table_name, table in tables.items():
        columns = [column.name for column in table.columns]
        result[table_name] = columns
    return result

@bp.route('/show_family', methods=['GET'])
def show_family():
    families = Family.query.all()
    return [family.to_dict() for family in families]

@bp.route('/show_parent', methods=['GET'])
def show_parent():
    parents = Parent.query.all()
    return [parent.to_dict() for parent in parents]

@bp.route('/show_kids', methods=['GET'])
def show_kids():
    kids = Kids.query.all()
    return [kid.to_dict() for kid in kids]

@bp.route('/family_summary', methods=['GET'])
def family_summary():
    """顯示家庭統計摘要"""
    total_families = db.session.query(Parent.family_id).distinct().count()
    total_parents = Parent.query.count()
    total_kids = Kids.query.count()
    
    return {
        'total_families': total_families,
        'total_parents': total_parents,
        'total_kids': total_kids
    }

@bp.route('/import_event_info', methods=['GET'])
def import_event_info():
    """導入活動資訊資料"""
    parse_event_info_data()
    return "Event info data imported successfully"

@bp.route('/add_single_event', methods=['POST'])
def add_single_event():
    """新增單筆活動記錄的 API"""
    try:
        data = request.get_json()
        
        # 驗證必要欄位
        required_fields = ['活動名稱', '活動分類']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必要欄位: {field}'}), 400
        
        success = process_single_event_record(data)
        
        if success:
            return jsonify({'message': '活動記錄新增成功'}), 200
        else:
            return jsonify({'error': '活動記錄新增失敗'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/show_events', methods=['GET'])
def show_events():
    """顯示所有活動"""
    events = EventInfo.query.all()
    return [event.to_dict() for event in events]

@bp.route('/reset_db', methods=['GET'])
def reset_db():
    """重置資料庫"""
    db.drop_all()
    db.create_all()
    return "Database reset successfully"