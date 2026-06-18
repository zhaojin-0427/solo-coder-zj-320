from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import User, HelpRequest, GuidanceRecord, StepCard, StepCardStep

help_bp = Blueprint('help', __name__)
stepcard_bp = Blueprint('stepcard', __name__)
stats_bp = Blueprint('stats', __name__)
user_bp = Blueprint('user', __name__)

def serialize_user(u):
    return {'id': u.id, 'name': u.name, 'role': u.role, 'avatar': u.avatar, 'phone': u.phone}

def serialize_help(h):
    return {
        'id': h.id, 'title': h.title, 'problem_type': h.problem_type,
        'description': h.description, 'image_url': h.image_url, 'audio_url': h.audio_url,
        'device_brand': h.device_brand, 'system_version': h.system_version,
        'status': h.status, 'requester_id': h.requester_id,
        'requester': serialize_user(h.requester) if h.requester else None,
        'helper': serialize_user(h.helper) if h.helper else None,
        'helper_id': h.helper_id, 'step_card_id': h.step_card_id,
        'created_at': h.created_at.isoformat() if h.created_at else None,
        'resolved_at': h.resolved_at.isoformat() if h.resolved_at else None,
        'resolution_duration': h.resolution_duration,
        'is_independent': h.is_independent, 'is_repeat': h.is_repeat,
        'guidance_records': [serialize_guidance(g) for g in h.guidance_records]
    }

def serialize_guidance(g):
    return {
        'id': g.id, 'help_request_id': g.help_request_id,
        'step_number': g.step_number, 'content': g.content,
        'tip': g.tip, 'image_url': g.image_url,
        'created_at': g.created_at.isoformat() if g.created_at else None
    }

def serialize_stepcard(s):
    return {
        'id': s.id, 'title': s.title, 'problem_type': s.problem_type,
        'difficulty': s.difficulty, 'device_brand': s.device_brand,
        'system_version': s.system_version, 'description': s.description,
        'usage_count': s.usage_count, 'created_by': s.created_by,
        'created_at': s.created_at.isoformat() if s.created_at else None,
        'updated_at': s.updated_at.isoformat() if s.updated_at else None,
        'steps': [serialize_step(st) for st in s.steps]
    }

def serialize_step(st):
    return {
        'id': st.id, 'step_card_id': st.step_card_id,
        'step_number': st.step_number, 'content': st.content,
        'tip': st.tip, 'image_url': st.image_url
    }

@user_bp.route('/', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([serialize_user(u) for u in users])

@help_bp.route('/', methods=['GET'])
def list_help():
    status = request.args.get('status')
    query = HelpRequest.query.order_by(HelpRequest.created_at.desc())
    if status:
        query = query.filter_by(status=status)
    helps = query.all()
    return jsonify([serialize_help(h) for h in helps])

@help_bp.route('/<int:id>', methods=['GET'])
def get_help(id):
    h = HelpRequest.query.get_or_404(id)
    return jsonify(serialize_help(h))

@help_bp.route('/', methods=['POST'])
def create_help():
    data = request.json
    h = HelpRequest(
        title=data['title'],
        problem_type=data['problem_type'],
        description=data.get('description'),
        image_url=data.get('image_url'),
        audio_url=data.get('audio_url'),
        device_brand=data.get('device_brand'),
        system_version=data.get('system_version'),
        requester_id=data.get('requester_id', 1)
    )
    existing = StepCard.query.filter_by(problem_type=h.problem_type).first()
    if existing:
        h.is_repeat = True
    db.session.add(h)
    db.session.commit()
    return jsonify(serialize_help(h)), 201

@help_bp.route('/<int:id>/guidance', methods=['POST'])
def add_guidance(id):
    data = request.json
    h = HelpRequest.query.get_or_404(id)
    g = GuidanceRecord(
        help_request_id=id,
        step_number=data['step_number'],
        content=data['content'],
        tip=data.get('tip'),
        image_url=data.get('image_url')
    )
    db.session.add(g)
    db.session.commit()
    return jsonify(serialize_guidance(g)), 201

@help_bp.route('/<int:id>/resolve', methods=['POST'])
def resolve_help(id):
    data = request.json
    h = HelpRequest.query.get_or_404(id)
    h.status = 'resolved'
    h.helper_id = data.get('helper_id', 2)
    h.resolved_at = datetime.utcnow()
    if h.created_at:
        delta = h.resolved_at - h.created_at
        h.resolution_duration = int(delta.total_seconds() // 60)
    h.is_independent = data.get('is_independent', False)
    db.session.commit()
    return jsonify(serialize_help(h))

@stepcard_bp.route('/', methods=['GET'])
def list_stepcards():
    problem_type = request.args.get('problem_type')
    query = StepCard.query.order_by(StepCard.usage_count.desc())
    if problem_type:
        query = query.filter_by(problem_type=problem_type)
    cards = query.all()
    return jsonify([serialize_stepcard(s) for s in cards])

@stepcard_bp.route('/<int:id>', methods=['GET'])
def get_stepcard(id):
    s = StepCard.query.get_or_404(id)
    return jsonify(serialize_stepcard(s))

@stepcard_bp.route('/', methods=['POST'])
def create_stepcard():
    data = request.json
    s = StepCard(
        title=data['title'],
        problem_type=data['problem_type'],
        difficulty=data.get('difficulty', 'normal'),
        device_brand=data.get('device_brand'),
        system_version=data.get('system_version'),
        description=data.get('description'),
        created_by=data.get('created_by', 2)
    )
    db.session.add(s)
    db.session.flush()
    for step_data in data.get('steps', []):
        st = StepCardStep(
            step_card_id=s.id,
            step_number=step_data['step_number'],
            content=step_data['content'],
            tip=step_data.get('tip'),
            image_url=step_data.get('image_url')
        )
        db.session.add(st)
    db.session.commit()
    return jsonify(serialize_stepcard(s)), 201

@stepcard_bp.route('/from_help/<int:help_id>', methods=['POST'])
def create_from_help(help_id):
    h = HelpRequest.query.get_or_404(help_id)
    data = request.json
    s = StepCard(
        title=data.get('title', h.title),
        problem_type=h.problem_type,
        difficulty=data.get('difficulty', 'normal'),
        device_brand=h.device_brand,
        system_version=h.system_version,
        description=data.get('description', h.description),
        created_by=data.get('created_by', 2)
    )
    db.session.add(s)
    db.session.flush()
    for g in sorted(h.guidance_records, key=lambda x: x.step_number):
        st = StepCardStep(
            step_card_id=s.id,
            step_number=g.step_number,
            content=g.content,
            tip=g.tip,
            image_url=g.image_url
        )
        db.session.add(st)
    h.step_card_id = s.id
    db.session.commit()
    return jsonify(serialize_stepcard(s)), 201

@stepcard_bp.route('/<int:id>/use', methods=['POST'])
def use_stepcard(id):
    s = StepCard.query.get_or_404(id)
    s.usage_count += 1
    db.session.commit()
    return jsonify(serialize_stepcard(s))

@stats_bp.route('/overview', methods=['GET'])
def stats_overview():
    total = HelpRequest.query.count()
    resolved = HelpRequest.query.filter_by(status='resolved').count()
    pending = HelpRequest.query.filter_by(status='pending').count()
    total_stepcards = StepCard.query.count()

    type_counts = db.session.query(
        HelpRequest.problem_type,
        db.func.count(HelpRequest.id)
    ).group_by(HelpRequest.problem_type).all()
    problem_types = [{'type': t, 'count': c} for t, c in type_counts]

    resolved_helps = HelpRequest.query.filter_by(status='resolved').all()
    durations = [h.resolution_duration for h in resolved_helps if h.resolution_duration]
    avg_duration = sum(durations) / len(durations) if durations else 0

    repeat_count = HelpRequest.query.filter_by(is_repeat=True).count()
    repeat_rate = (repeat_count / total * 100) if total else 0

    independent_count = HelpRequest.query.filter_by(is_independent=True).count()
    independent_rate = (independent_count / resolved * 100) if resolved else 0

    return jsonify({
        'total_requests': total,
        'resolved_count': resolved,
        'pending_count': pending,
        'total_stepcards': total_stepcards,
        'problem_types': problem_types,
        'average_duration_minutes': round(avg_duration, 1),
        'repeat_rate_percent': round(repeat_rate, 1),
        'independent_rate_percent': round(independent_rate, 1)
    })

@stats_bp.route('/timeline', methods=['GET'])
def stats_timeline():
    from sqlalchemy import func
    result = db.session.query(
        func.date(HelpRequest.created_at).label('date'),
        func.count(HelpRequest.id).label('count')
    ).group_by(func.date(HelpRequest.created_at)).order_by('date').all()
    return jsonify([{'date': str(d), 'count': c} for d, c in result])
