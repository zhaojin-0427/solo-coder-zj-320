from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import User, HelpRequest, GuidanceRecord, StepCard, StepCardStep, PracticeRecord, PracticeStepFeedback

help_bp = Blueprint('help', __name__)
stepcard_bp = Blueprint('stepcard', __name__)
stats_bp = Blueprint('stats', __name__)
user_bp = Blueprint('user', __name__)
practice_bp = Blueprint('practice', __name__)

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

def serialize_practice_step_feedback(psf):
    return {
        'id': psf.id,
        'practice_record_id': psf.practice_record_id,
        'step_card_step_id': psf.step_card_step_id,
        'step_number': psf.step_number,
        'status': psf.status,
        'feedback': psf.feedback,
        'step_content': psf.step_card_step.content if psf.step_card_step else None,
        'created_at': psf.created_at.isoformat() if psf.created_at else None
    }

def serialize_practice_record(pr):
    return {
        'id': pr.id,
        'step_card_id': pr.step_card_id,
        'practitioner_id': pr.practitioner_id,
        'practitioner': serialize_user(pr.practitioner) if pr.practitioner else None,
        'source': pr.source,
        'status': pr.status,
        'is_independent': pr.is_independent,
        'stuck_step_number': pr.stuck_step_number,
        'feedback': pr.feedback,
        'converted_to_help': pr.converted_to_help,
        'help_request_id': pr.help_request_id,
        'step_card': serialize_stepcard(pr.step_card) if pr.step_card else None,
        'step_feedbacks': [serialize_practice_step_feedback(f) for f in pr.step_feedbacks],
        'created_at': pr.created_at.isoformat() if pr.created_at else None,
        'completed_at': pr.completed_at.isoformat() if pr.completed_at else None
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

@stats_bp.route('/practice', methods=['GET'])
def stats_practice():
    from sqlalchemy import func, desc

    total_practices = PracticeRecord.query.count()
    completed_practices = PracticeRecord.query.filter_by(status='completed').count()
    completion_rate = (completed_practices / total_practices * 100) if total_practices else 0

    converted_count = PracticeRecord.query.filter_by(converted_to_help=True).count()

    step_stuck_counts = db.session.query(
        PracticeStepFeedback.step_number,
        StepCard.title,
        func.count(PracticeStepFeedback.id).label('stuck_count')
    ).join(
        PracticeRecord, PracticeStepFeedback.practice_record_id == PracticeRecord.id
    ).join(
        StepCard, PracticeRecord.step_card_id == StepCard.id
    ).filter(
        PracticeStepFeedback.status.in_(['cannot_understand', 'cannot_find'])
    ).group_by(
        PracticeStepFeedback.step_number, StepCard.title
    ).order_by(desc('stuck_count')).limit(5).all()

    stuck_steps = [
        {
            'step_number': s,
            'card_title': t,
            'stuck_count': c
        } for s, t, c in step_stuck_counts
    ]

    card_practice_counts = db.session.query(
        StepCard.id,
        StepCard.title,
        func.count(PracticeRecord.id).label('practice_count')
    ).join(
        PracticeRecord, StepCard.id == PracticeRecord.step_card_id
    ).group_by(StepCard.id, StepCard.title).order_by(desc('practice_count')).limit(5).all()

    top_practiced_cards = [
        {'id': cid, 'title': t, 'practice_count': pc}
        for cid, t, pc in card_practice_counts
    ]

    return jsonify({
        'total_practices': total_practices,
        'completed_practices': completed_practices,
        'completion_rate_percent': round(completion_rate, 1),
        'converted_to_help_count': converted_count,
        'top_stuck_steps': stuck_steps,
        'top_practiced_cards': top_practiced_cards
    })

@practice_bp.route('/', methods=['GET'])
def list_practices():
    step_card_id = request.args.get('step_card_id', type=int)
    practitioner_id = request.args.get('practitioner_id', type=int)
    status = request.args.get('status')

    query = PracticeRecord.query.order_by(PracticeRecord.created_at.desc())
    if step_card_id:
        query = query.filter_by(step_card_id=step_card_id)
    if practitioner_id:
        query = query.filter_by(practitioner_id=practitioner_id)
    if status:
        query = query.filter_by(status=status)

    practices = query.all()
    return jsonify([serialize_practice_record(p) for p in practices])

@practice_bp.route('/<int:id>', methods=['GET'])
def get_practice(id):
    p = PracticeRecord.query.get_or_404(id)
    return jsonify(serialize_practice_record(p))

@practice_bp.route('/', methods=['POST'])
def create_practice():
    data = request.json
    p = PracticeRecord(
        step_card_id=data['step_card_id'],
        practitioner_id=data.get('practitioner_id', 1),
        source=data.get('source', 'library'),
        status='in_progress'
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(serialize_practice_record(p)), 201

@practice_bp.route('/<int:id>/step_feedback', methods=['POST'])
def add_step_feedback(id):
    data = request.json
    p = PracticeRecord.query.get_or_404(id)

    existing = PracticeStepFeedback.query.filter_by(
        practice_record_id=id,
        step_card_step_id=data['step_card_step_id']
    ).first()

    if existing:
        existing.status = data['status']
        existing.feedback = data.get('feedback')
        psf = existing
    else:
        psf = PracticeStepFeedback(
            practice_record_id=id,
            step_card_step_id=data['step_card_step_id'],
            step_number=data['step_number'],
            status=data['status'],
            feedback=data.get('feedback')
        )
        db.session.add(psf)

    if data['status'] in ['cannot_understand', 'cannot_find']:
        p.stuck_step_number = data['step_number']

    db.session.commit()
    return jsonify(serialize_practice_step_feedback(psf)), 201

@practice_bp.route('/<int:id>/complete', methods=['POST'])
def complete_practice(id):
    data = request.json
    p = PracticeRecord.query.get_or_404(id)
    p.status = 'completed'
    p.completed_at = datetime.utcnow()
    p.feedback = data.get('feedback')
    p.is_independent = data.get('is_independent', True)
    p.stuck_step_number = data.get('stuck_step_number')
    db.session.commit()
    return jsonify(serialize_practice_record(p))

@practice_bp.route('/<int:id>/convert_to_help', methods=['POST'])
def convert_to_help(id):
    data = request.json
    p = PracticeRecord.query.get_or_404(id)

    h = HelpRequest(
        title=f'练习卡住：{p.step_card.title}' if p.step_card else '练习卡住求助',
        problem_type=p.step_card.problem_type if p.step_card else '其他问题',
        description=data.get('description') or p.feedback or '练习时遇到困难，需要帮助',
        device_brand=p.step_card.device_brand if p.step_card else None,
        system_version=p.step_card.system_version if p.step_card else None,
        requester_id=p.practitioner_id,
        is_repeat=True
    )
    db.session.add(h)
    db.session.flush()

    p.converted_to_help = True
    p.help_request_id = h.id
    p.status = 'converted'
    db.session.commit()

    return jsonify(serialize_practice_record(p))

@practice_bp.route('/card_stats/<int:card_id>', methods=['GET'])
def get_card_practice_stats(card_id):
    from sqlalchemy import func, desc

    practices = PracticeRecord.query.filter_by(step_card_id=card_id).all()
    total = len(practices)
    completed = len([p for p in practices if p.status == 'completed'])
    completion_rate = (completed / total * 100) if total else 0

    step_stuck_counts = db.session.query(
        PracticeStepFeedback.step_number,
        func.count(PracticeStepFeedback.id).label('stuck_count')
    ).join(
        PracticeRecord, PracticeStepFeedback.practice_record_id == PracticeRecord.id
    ).filter(
        PracticeRecord.step_card_id == card_id,
        PracticeStepFeedback.status.in_(['cannot_understand', 'cannot_find'])
    ).group_by(
        PracticeStepFeedback.step_number
    ).order_by(desc('stuck_count')).all()

    stuck_steps = [{'step_number': s, 'stuck_count': c} for s, c in step_stuck_counts]
    most_stuck_step = stuck_steps[0] if stuck_steps else None

    needs_optimization = total >= 3 and (
        completion_rate < 60 or
        (most_stuck_step and most_stuck_step['stuck_count'] >= total * 0.5)
    )

    recent_practices = PracticeRecord.query.filter_by(
        step_card_id=card_id
    ).order_by(PracticeRecord.created_at.desc()).limit(10).all()

    return jsonify({
        'step_card_id': card_id,
        'total_practice_count': total,
        'recent_practice_count': len(recent_practices),
        'completion_count': completed,
        'completion_rate_percent': round(completion_rate, 1),
        'most_stuck_step': most_stuck_step,
        'stuck_steps_detail': stuck_steps,
        'needs_optimization': needs_optimization,
        'independent_count': len([p for p in practices if p.is_independent]),
        'converted_to_help_count': len([p for p in practices if p.converted_to_help])
    })

@stepcard_bp.route('/<int:id>/add_tip', methods=['POST'])
def add_step_tip(id):
    data = request.json
    step = StepCardStep.query.filter_by(
        step_card_id=id,
        step_number=data['step_number']
    ).first()

    if not step:
        return jsonify({'error': 'Step not found'}), 404

    existing_tip = step.tip or ''
    new_tip = data.get('tip', '').strip()
    if existing_tip and new_tip:
        step.tip = f"{existing_tip}\n\n用户反馈补充：{new_tip}"
    else:
        step.tip = new_tip

    db.session.commit()
    return jsonify(serialize_step(step))
