from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, date

class Kids(db.Model):
    __tablename__ = 'd_kids'

    member_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    family_id = db.Column(UUID(as_uuid=True), nullable=False)
    gender = db.Column(db.String(24), nullable=False)  # male, female, other, unknow
    kids_name = db.Column(db.String(24), nullable=False)  # Required: Name of the kid
    #id_last4 = db.Column(db.Integer, nullable=True)
    BRD = db.Column(db.Date, nullable=False)  # Birthday
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, family_id, gender, kids_name, BRD):
        self.family_id = family_id
        self.gender = gender
        self.kids_name = kids_name
        #self.id_last4 = id_last4
        self.BRD = BRD

    def __repr__(self):
        return f'<Kids member_id={self.member_id}, family_id={self.family_id}, gender={self.gender}, kids_name={self.kids_name}>'

    def to_dict(self):
        return {
            'member_id': str(self.member_id),
            'family_id': str(self.family_id),
            'gender': self.gender,
            'kids_name': self.kids_name,
            'BRD': self.BRD.isoformat() if self.BRD else None,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'update_date': self.update_date.isoformat() if self.update_date else None
        }