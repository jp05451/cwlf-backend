from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class Parent(db.Model):
    __tablename__ = 'd_parent'

    member_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    family_id = db.Column(UUID(as_uuid=True), nullable=False)
    parent_name = db.Column(db.String(24), nullable=False)
    phone_num = db.Column(db.String(24), nullable=False)
    gender = db.Column(db.String(24), nullable=True)  # male, female, other, unknow
    register_station = db.Column(db.String(64), nullable=True)
    addr = db.Column(db.Text, nullable=True)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    in_same_region = db.Column(db.Boolean, nullable=True)

    def __init__(self, family_id, parent_name, phone_num, gender=None, addr=None, register_station=None):
        self.family_id = family_id
        self.parent_name = parent_name
        self.phone_num = phone_num
        self.gender = gender
        self.addr = addr
        self.register_station = register_station
        self.in_same_region = self.is_same_region(register_station, addr) if register_station and addr else None

    def is_same_region(self, register_station, addr):
        # Implement your logic to determine if the parent is in the same region
        region = register_station[:2]
        #如果地址包含地區代碼，則視為同區域
        if region in addr:
            return True
        return False
    
    def __repr__(self):
        return f'<Parent member_id={self.member_id}, name={self.parent_name}, phone={self.phone_num}>'

    def to_dict(self):
        return {
            'member_id': str(self.member_id),
            'family_id': str(self.family_id),
            'parent_name': self.parent_name,
            'phone_num': self.phone_num,
            'gender': self.gender,
            'addr': self.addr,
            'register_station': self.register_station,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'update_date': self.update_date.isoformat() if self.update_date else None,
            'in_same_region': self.in_same_region
        }