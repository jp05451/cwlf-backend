from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class Station(db.Model):
    __tablename__ = 'd_station'

    station_id = db.Column(db.String(64), primary_key=True, default=uuid.uuid4, nullable=False)
    station_name = db.Column(db.String(24), nullable=False)
    addr = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(24), nullable=False)  # 總部、育兒+、...
    enable = db.Column(db.Boolean, nullable=False, default=True)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self,station_name, category, addr=None, enable=True):
        self.station_name = station_name
        self.category = category
        self.addr = addr
        self.enable = enable

    def __repr__(self):
        return f'<Station station_id={self.station_id}, name={self.station_name}, category={self.category}>'

    def to_dict(self):
        return {
            'station_id': str(self.station_id),
            'station_name': self.station_name,
            'addr': self.addr,
            'category': self.category,
            'enable': self.enable,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'update_date': self.update_date.isoformat() if self.update_date else None
        }