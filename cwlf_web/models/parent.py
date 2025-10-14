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
    addr = db.Column(db.Text, nullable=True)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, family_id, parent_name, phone_num, gender=None, addr=None):
        self.family_id = family_id
        self.parent_name = parent_name
        self.phone_num = phone_num
        self.gender = gender
        self.addr = addr

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
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'update_date': self.update_date.isoformat() if self.update_date else None
        }