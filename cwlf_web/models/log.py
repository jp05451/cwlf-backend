from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class LogEntry(db.Model):
    __tablename__ = 'ods_user_visit_log'
    
    user_visit_log_id = db.Column(db.String(64), primary_key=True, default=uuid.uuid4, nullable=False)
    ods_user_visit_log = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    station_name = db.Column(db.String(24), nullable=False)
    #家長1~4姓名
    parent_name_1 = db.Column(db.String(24), nullable=False)
    parent_name_2 = db.Column(db.String(24), nullable=False)
    parent_name_3 = db.Column(db.String(24), nullable=False)
    parent_name_4 = db.Column(db.String(24), nullable=False)
    #家長1~4聯絡電話
    phone_num_1 = db.Column(db.String(24), nullable=False)
    phone_num_2 = db.Column(db.String(24), nullable=False)
    phone_num_3 = db.Column(db.String(24), nullable=False)
    phone_num_4 = db.Column(db.String(24), nullable=False)
    #兒童1~6姓名
    kid_name_1 = db.Column(db.String(24), nullable=False)
    kid_name_2 = db.Column(db.String(24), nullable=False)
    kid_name_3 = db.Column(db.String(24), nullable=False)
    kid_name_4 = db.Column(db.String(24), nullable=False)
    kid_name_5 = db.Column(db.String(24), nullable=False)
    kid_name_6 = db.Column(db.String(24), nullable=False)
    #兒童1~6生日
    kid_birthday_1 = db.Column(db.DateTime, nullable=True)
    kid_birthday_2 = db.Column(db.DateTime, nullable=True)
    kid_birthday_3 = db.Column(db.DateTime, nullable=True)
    kid_birthday_4 = db.Column(db.DateTime, nullable=True)
    kid_birthday_5 = db.Column(db.DateTime, nullable=True)
    kid_birthday_6 = db.Column(db.DateTime, nullable=True)

    def __init__(self, visit_time, station_name, parent_names, phone_nums, kid_names, kid_birthdays):
        self.ods_user_visit_log = visit_time
        self.station_name = station_name
        self.parent_name_1 = parent_names[0] if len(parent_names) > 0 else ''
        self.parent_name_2 = parent_names[1] if len(parent_names) > 1 else ''
        self.parent_name_3 = parent_names[2] if len(parent_names) > 2 else ''
        self.parent_name_4 = parent_names[3] if len(parent_names) > 3 else ''
        self.phone_num_1 = phone_nums[0] if len(phone_nums) > 0 else ''
        self.phone_num_2 = phone_nums[1] if len(phone_nums) > 1 else ''
        self.phone_num_3 = phone_nums[2] if len(phone_nums) > 2 else ''
        self.phone_num_4 = phone_nums[3] if len(phone_nums) > 3 else ''
        self.kid_name_1 = kid_names[0] if len(kid_names) > 0 else ''
        self.kid_name_2 = kid_names[1] if len(kid_names) > 1 else ''
        self.kid_name_3 = kid_names[2] if len(kid_names) > 2 else ''
        self.kid_name_4 = kid_names[3] if len(kid_names) > 3 else ''
        self.kid_name_5 = kid_names[4] if len(kid_names) > 4 else ''
        self.kid_name_6 = kid_names[5] if len(kid_names) > 5 else ''
        self.kid_birthday_1 = kid_birthdays[0] if len(kid_birthdays) > 0 else None
        self.kid_birthday_2 = kid_birthdays[1] if len(kid_birthdays) > 1 else None
        self.kid_birthday_3 = kid_birthdays[2] if len(kid_birthdays) > 2 else None
        self.kid_birthday_4 = kid_birthdays[3] if len(kid_birthdays) > 3 else None
        self.kid_birthday_5 = kid_birthdays[4] if len(kid_birthdays) > 4 else None
        self.kid_birthday_6 = kid_birthdays[5] if len(kid_birthdays) > 5 else None
        
    def __repr__(self):
        return f'<LogEntry user_visit_log_id={self.user_visit_log_id}, station={self.station_name}, visit_time={self.ods_user_visit_log}>'
    def to_dict(self):
        return {
            'user_visit_log_id': str(self.user_visit_log_id),
            'visit_time': self.ods_user_visit_log.isoformat() if self.ods_user_visit_log else None,
            'station_name': self.station_name,
            'parent_name_1': self.parent_name_1,
            'parent_name_2': self.parent_name_2,
            'parent_name_3': self.parent_name_3,
            'parent_name_4': self.parent_name_4,
            'phone_num_1': self.phone_num_1,
            'phone_num_2': self.phone_num_2,
            'phone_num_3': self.phone_num_3,
            'phone_num_4': self.phone_num_4,
            'kid_name_1': self.kid_name_1,
            'kid_name_2': self.kid_name_2,
            'kid_name_3': self.kid_name_3,
            'kid_name_4': self.kid_name_4,
            'kid_name_5': self.kid_name_5,
            'kid_name_6': self.kid_name_6,
            'kid_birthday_1': self.kid_birthday_1.isoformat() if self.kid_birthday_1 else None,
            'kid_birthday_2': self.kid_birthday_2.isoformat() if self.kid_birthday_2 else None,
            'kid_birthday_3': self.kid_birthday_3.isoformat() if self.kid_birthday_3 else None,
            'kid_birthday_4': self.kid_birthday_4.isoformat() if self.kid_birthday_4 else None,
            'kid_birthday_5': self.kid_birthday_5.isoformat() if self.kid_birthday_5 else None,
            'kid_birthday_6': self.kid_birthday_6.isoformat() if self.kid_birthday_6 else None
        }