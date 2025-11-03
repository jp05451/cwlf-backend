from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class Family(db.Model):
    __tablename__ = 'd_family'

    family_pair_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    family_id = db.Column(UUID(as_uuid=True), nullable=False)  # FK for family grouping
    member_id = db.Column(UUID(as_uuid=True), nullable=False)  # FK to d_parent or d_kids
    member_role = db.Column(db.String(24), nullable=False)  # parent, kids, relative, other
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, family_id, member_id, member_role):
        self.family_id = family_id
        self.member_id = member_id
        self.member_role = member_role

    def __repr__(self):
        return f'<Family pair_id={self.family_pair_id}, family_id={self.family_id}, member_role={self.member_role}>'

    def to_dict(self):
        return {
            'family_pair_id': str(self.family_pair_id),
            'family_id': str(self.family_id),
            'member_id': str(self.member_id),
            'member_role': self.member_role,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'update_date': self.update_date.isoformat() if self.update_date else None
        }