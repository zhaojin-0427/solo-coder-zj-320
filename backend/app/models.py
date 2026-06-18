from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    avatar = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HelpRequest(db.Model):
    __tablename__ = 'help_requests'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    problem_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    audio_url = db.Column(db.String(500))
    device_brand = db.Column(db.String(50))
    system_version = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    helper_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolution_duration = db.Column(db.Integer)
    is_independent = db.Column(db.Boolean, default=False)
    is_repeat = db.Column(db.Boolean, default=False)
    
    requester = db.relationship('User', foreign_keys=[requester_id])
    helper = db.relationship('User', foreign_keys=[helper_id])
    guidance_records = db.relationship('GuidanceRecord', backref='help_request', cascade='all, delete-orphan')
    step_card_id = db.Column(db.Integer, db.ForeignKey('step_cards.id'))

class GuidanceRecord(db.Model):
    __tablename__ = 'guidance_records'
    id = db.Column(db.Integer, primary_key=True)
    help_request_id = db.Column(db.Integer, db.ForeignKey('help_requests.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    tip = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StepCard(db.Model):
    __tablename__ = 'step_cards'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    problem_type = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), default='normal')
    device_brand = db.Column(db.String(50))
    system_version = db.Column(db.String(50))
    description = db.Column(db.Text)
    usage_count = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    steps = db.relationship('StepCardStep', backref='step_card', cascade='all, delete-orphan')
    help_requests = db.relationship('HelpRequest', backref='step_card')

class StepCardStep(db.Model):
    __tablename__ = 'step_card_steps'
    id = db.Column(db.Integer, primary_key=True)
    step_card_id = db.Column(db.Integer, db.ForeignKey('step_cards.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    tip = db.Column(db.Text)
    image_url = db.Column(db.String(500))
