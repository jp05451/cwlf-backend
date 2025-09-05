from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class EventInfo(db.Model):
    __tablename__ = 'd_event_info'

    event_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    event_name = db.Column(db.String(64), nullable=False)
    event_category = db.Column(db.String(24), nullable=False)  # 保持原規格拼字
    event_description = db.Column(db.Text, nullable=True)
    
    prior_event_id = db.Column(UUID(as_uuid=True), nullable=True) # FK需先參加過哪一類活動
    station_id = db.Column(UUID(as_uuid=True), nullable=False)  # FK主辦單位
    register_necessary = db.Column(db.Boolean, nullable=False)  # 是否需註冊
    event_start_date = db.Column(db.DateTime, nullable=False)
    event_end_date = db.Column(db.DateTime, nullable=False)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, event_name, event_category, station_id, register_necessary, event_start_date, event_end_date, event_description=None, prior_event_id=None):
        self.event_name = event_name
        self.event_category = event_category
        self.event_description = event_description
        self.prior_event_id = prior_event_id
        self.station_id = station_id
        self.register_necessary = register_necessary
        self.event_start_date = event_start_date
        self.event_end_date = event_end_date

    def __repr__(self):
        return f'<EventInfo event_id={self.event_id}, name={self.event_name}, category={self.event_category}>'

    def to_dict(self):
        return {
            'event_id': str(self.event_id),
            'event_name': self.event_name,
            'event_category': self.event_category,
            'event_description': self.event_description,
            'prior_event_id': str(self.prior_event_id) if self.prior_event_id else None,
            'station_id': str(self.station_id),
            'register_necessary': self.register_necessary,
            'event_start_date': self.event_start_date.isoformat() if self.event_start_date else None,
            'event_end_date': self.event_end_date.isoformat() if self.event_end_date else None,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'update_date': self.update_date.isoformat() if self.update_date else None
        }


class EnvUsage(db.Model):
    __tablename__ = 'd_env_usage'

    env_usage_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    member_id = db.Column(UUID(as_uuid=True), nullable=False)  # FK成員ID
    enter_time = db.Column(db.DateTime, nullable=False)
    leave_time = db.Column(db.DateTime, nullable=False)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, member_id, enter_time, leave_time):
        self.member_id = member_id
        self.enter_time = enter_time
        self.leave_time = leave_time

    def __repr__(self):
        return f'<EnvUsage env_usage_id={self.env_usage_id}, member_id={self.member_id}>'

    @property
    def duration_minutes(self):
        """計算使用時長（分鐘）"""
        if self.enter_time and self.leave_time:
            return int((self.leave_time - self.enter_time).total_seconds() / 60)
        return 0

    def to_dict(self):
        return {
            'env_usage_id': str(self.env_usage_id),
            'member_id': str(self.member_id),
            'enter_time': self.enter_time.isoformat() if self.enter_time else None,
            'leave_time': self.leave_time.isoformat() if self.leave_time else None,
            'duration_minutes': self.duration_minutes,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'update_date': self.update_date.isoformat() if self.update_date else None
        }


class EventParticipate(db.Model):
    __tablename__ = 'd_event_participate'

    env_participate_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    event_id = db.Column(UUID(as_uuid=True), nullable=False)  # FK活動ID
    event_register_date = db.Column(db.Date, nullable=False)
    participate = db.Column(db.Boolean, nullable=False)  # 是否報到
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, event_id, event_register_date, participate):
        self.event_id = event_id
        self.event_register_date = event_register_date
        self.participate = participate

    def __repr__(self):
        return f'<EventParticipate env_participate_id={self.env_participate_id}, event_id={self.event_id}, participate={self.participate}>'

    def to_dict(self):
        return {
            'env_participate_id': str(self.env_participate_id),
            'event_id': str(self.event_id),
            'event_register_date': self.event_register_date.isoformat() if self.event_register_date else None,
            'participate': self.participate,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'update_date': self.update_date.isoformat() if self.update_date else None
        }