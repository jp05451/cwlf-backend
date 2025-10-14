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

bp = Blueprint('new_data', __name__,template_folder=os.path.join(os.path.dirname(__file__), '../templates'))

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

