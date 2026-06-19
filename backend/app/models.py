from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    avatar = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    expertise = db.Column(db.String(200))
    is_online = db.Column(db.Boolean, default=False)
    is_on_duty = db.Column(db.Boolean, default=False)
    last_online_at = db.Column(db.DateTime)
    expected_response_minutes = db.Column(db.Integer, default=5)
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
    status = db.Column(db.String(30), default='pending')
    processing_status = db.Column(db.String(30))
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    helper_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_at = db.Column(db.DateTime)
    responded_at = db.Column(db.DateTime)
    response_duration = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolution_duration = db.Column(db.Integer)
    is_independent = db.Column(db.Boolean, default=False)
    is_repeat = db.Column(db.Boolean, default=False)
    transfer_count = db.Column(db.Integer, default=0)
    is_timeout = db.Column(db.Boolean, default=False)
    is_risk = db.Column(db.Boolean, default=False)
    risk_level = db.Column(db.String(20))
    processing_note = db.Column(db.Text)
    device_profile_id = db.Column(db.Integer, db.ForeignKey('device_profiles.id'))
    create_source = db.Column(db.String(20), default='direct')

    requester = db.relationship('User', foreign_keys=[requester_id])
    helper = db.relationship('User', foreign_keys=[helper_id])
    guidance_records = db.relationship('GuidanceRecord', backref='help_request', cascade='all, delete-orphan')
    step_card_id = db.Column(db.Integer, db.ForeignKey('step_cards.id'))
    device_profile = db.relationship('DeviceProfile', backref='help_requests')
    status_logs = db.relationship('HelpStatusLog', backref='help_request', cascade='all, delete-orphan')
    assignments = db.relationship('HelpAssignment', backref='help_request', cascade='all, delete-orphan')
    risk_info = db.relationship('FraudRiskInfo', backref='help_request', uselist=False, cascade='all, delete-orphan')
    risk_disposals = db.relationship('RiskDisposal', backref='help_request', cascade='all, delete-orphan')

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
    responsible_family_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_source = db.Column(db.String(20), default='manual')
    source_help_request_id = db.Column(db.Integer, db.ForeignKey('help_requests.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    steps = db.relationship('StepCardStep', backref='step_card', cascade='all, delete-orphan')
    help_requests = db.relationship('HelpRequest', foreign_keys=[HelpRequest.step_card_id], backref='step_card')
    created_by_user = db.relationship('User', foreign_keys=[created_by])
    responsible_family = db.relationship('User', foreign_keys=[responsible_family_id])

class StepCardStep(db.Model):
    __tablename__ = 'step_card_steps'
    id = db.Column(db.Integer, primary_key=True)
    step_card_id = db.Column(db.Integer, db.ForeignKey('step_cards.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    tip = db.Column(db.Text)
    image_url = db.Column(db.String(500))

class PracticeRecord(db.Model):
    __tablename__ = 'practice_records'
    id = db.Column(db.Integer, primary_key=True)
    step_card_id = db.Column(db.Integer, db.ForeignKey('step_cards.id'), nullable=False)
    practitioner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='in_progress')
    is_independent = db.Column(db.Boolean, default=False)
    stuck_step_number = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    converted_to_help = db.Column(db.Boolean, default=False)
    help_request_id = db.Column(db.Integer, db.ForeignKey('help_requests.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    step_card = db.relationship('StepCard', backref='practice_records')
    practitioner = db.relationship('User', foreign_keys=[practitioner_id])
    help_request = db.relationship('HelpRequest', foreign_keys=[help_request_id])
    step_feedbacks = db.relationship('PracticeStepFeedback', backref='practice_record', cascade='all, delete-orphan')

class StepCardDeviceTip(db.Model):
    __tablename__ = 'step_card_device_tips'
    id = db.Column(db.Integer, primary_key=True)
    step_card_id = db.Column(db.Integer, db.ForeignKey('step_cards.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    device_brand = db.Column(db.String(50), nullable=False)
    system_version = db.Column(db.String(50))
    adaptation_tip = db.Column(db.Text, nullable=False)
    entry_name = db.Column(db.String(100))

    step_card = db.relationship('StepCard', backref='device_tips')

class DeviceProfile(db.Model):
    __tablename__ = 'device_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    device_brand = db.Column(db.String(50))
    system_version = db.Column(db.String(50))
    font_size_preference = db.Column(db.String(20))
    simple_mode_enabled = db.Column(db.Boolean, default=False)
    common_apps = db.Column(db.Text)
    network_environment = db.Column(db.String(50))
    difficulty_tags = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='device_profile')

class PracticeStepFeedback(db.Model):
    __tablename__ = 'practice_step_feedbacks'
    id = db.Column(db.Integer, primary_key=True)
    practice_record_id = db.Column(db.Integer, db.ForeignKey('practice_records.id'), nullable=False)
    step_card_step_id = db.Column(db.Integer, db.ForeignKey('step_card_steps.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    step_card_step = db.relationship('StepCardStep')

class HelpStatusLog(db.Model):
    __tablename__ = 'help_status_logs'
    id = db.Column(db.Integer, primary_key=True)
    help_request_id = db.Column(db.Integer, db.ForeignKey('help_requests.id'), nullable=False)
    old_status = db.Column(db.String(30))
    new_status = db.Column(db.String(30))
    old_processing_status = db.Column(db.String(30))
    new_processing_status = db.Column(db.String(30))
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    operator = db.relationship('User', foreign_keys=[operator_id])

class HelpAssignment(db.Model):
    __tablename__ = 'help_assignments'
    id = db.Column(db.Integer, primary_key=True)
    help_request_id = db.Column(db.Integer, db.ForeignKey('help_requests.id'), nullable=False)
    from_helper_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    to_helper_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignment_type = db.Column(db.String(20), default='auto')
    reason = db.Column(db.Text)
    match_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    from_helper = db.relationship('User', foreign_keys=[from_helper_id])
    to_helper = db.relationship('User', foreign_keys=[to_helper_id])

class FraudRiskInfo(db.Model):
    __tablename__ = 'fraud_risk_infos'
    id = db.Column(db.Integer, primary_key=True)
    help_request_id = db.Column(db.Integer, db.ForeignKey('help_requests.id'), nullable=False, unique=True)
    scam_type = db.Column(db.String(50), nullable=False)
    suspicious_source = db.Column(db.String(200))
    involved_amount = db.Column(db.Float, default=0)
    leaked_verification_code = db.Column(db.Boolean, default=False)
    leaked_payment_password = db.Column(db.Boolean, default=False)
    clicked_link = db.Column(db.Boolean, default=False)
    risk_keywords = db.Column(db.Text)
    custom_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RiskDisposal(db.Model):
    __tablename__ = 'risk_disposals'
    id = db.Column(db.Integer, primary_key=True)
    help_request_id = db.Column(db.Integer, db.ForeignKey('help_requests.id'), nullable=False)
    disposal_type = db.Column(db.String(30), nullable=False)
    note = db.Column(db.Text)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    operator = db.relationship('User', foreign_keys=[operator_id])
