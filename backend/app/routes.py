from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import User, HelpRequest, GuidanceRecord, StepCard, StepCardStep, PracticeRecord, PracticeStepFeedback, DeviceProfile, StepCardDeviceTip

help_bp = Blueprint('help', __name__)
stepcard_bp = Blueprint('stepcard', __name__)
stats_bp = Blueprint('stats', __name__)
user_bp = Blueprint('user', __name__)
practice_bp = Blueprint('practice', __name__)
device_bp = Blueprint('device', __name__)

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
        'device_profile_id': h.device_profile_id,
        'device_profile': serialize_device_profile(h.device_profile) if h.device_profile else None,
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
        'steps': [serialize_step(st) for st in s.steps],
        'device_tips': [serialize_device_tip(dt) for dt in s.device_tips]
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

def serialize_device_profile(dp):
    return {
        'id': dp.id, 'user_id': dp.user_id,
        'device_brand': dp.device_brand, 'system_version': dp.system_version,
        'font_size_preference': dp.font_size_preference,
        'simple_mode_enabled': dp.simple_mode_enabled,
        'common_apps': dp.common_apps,
        'network_environment': dp.network_environment,
        'difficulty_tags': dp.difficulty_tags,
        'updated_at': dp.updated_at.isoformat() if dp.updated_at else None,
        'user': serialize_user(dp.user) if dp.user else None
    }

def serialize_device_tip(dt):
    return {
        'id': dt.id, 'step_card_id': dt.step_card_id,
        'step_number': dt.step_number, 'device_brand': dt.device_brand,
        'system_version': dt.system_version,
        'adaptation_tip': dt.adaptation_tip,
        'entry_name': dt.entry_name
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
        requester_id=data.get('requester_id', 1),
        device_profile_id=data.get('device_profile_id')
    )
    existing = StepCard.query.filter_by(problem_type=h.problem_type)
    if h.device_brand:
        brand_cards = existing.filter(
            db.or_(StepCard.device_brand == h.device_brand, StepCard.device_brand == None)
        ).all()
        if brand_cards:
            existing = StepCard.query.filter_by(problem_type=h.problem_type).filter(
                db.or_(StepCard.device_brand == h.device_brand, StepCard.device_brand == None)
            )
        else:
            existing = StepCard.query.filter_by(problem_type=h.problem_type)
    first = existing.first()
    if first:
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
    device_brand = request.args.get('device_brand')
    query = StepCard.query.order_by(StepCard.usage_count.desc())
    if problem_type:
        query = query.filter_by(problem_type=problem_type)
    if device_brand:
        query = query.filter(
            db.or_(StepCard.device_brand == device_brand, StepCard.device_brand == None)
        )
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

@device_bp.route('/profiles', methods=['GET'])
def list_device_profiles():
    profiles = DeviceProfile.query.all()
    return jsonify([serialize_device_profile(p) for p in profiles])

@device_bp.route('/profiles/<int:id>', methods=['GET'])
def get_device_profile(id):
    p = DeviceProfile.query.get_or_404(id)
    return jsonify(serialize_device_profile(p))

@device_bp.route('/profiles', methods=['POST'])
def create_device_profile():
    data = request.json
    existing = DeviceProfile.query.filter_by(user_id=data['user_id']).first()
    if existing:
        return jsonify({'error': '该用户已有设备档案，请使用 PUT 更新'}), 400
    p = DeviceProfile(
        user_id=data['user_id'],
        device_brand=data.get('device_brand'),
        system_version=data.get('system_version'),
        font_size_preference=data.get('font_size_preference'),
        simple_mode_enabled=data.get('simple_mode_enabled', False),
        common_apps=data.get('common_apps'),
        network_environment=data.get('network_environment'),
        difficulty_tags=data.get('difficulty_tags')
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(serialize_device_profile(p)), 201

@device_bp.route('/profiles/<int:id>', methods=['PUT'])
def update_device_profile(id):
    p = DeviceProfile.query.get_or_404(id)
    data = request.json
    if 'device_brand' in data:
        p.device_brand = data['device_brand']
    if 'system_version' in data:
        p.system_version = data['system_version']
    if 'font_size_preference' in data:
        p.font_size_preference = data['font_size_preference']
    if 'simple_mode_enabled' in data:
        p.simple_mode_enabled = data['simple_mode_enabled']
    if 'common_apps' in data:
        p.common_apps = data['common_apps']
    if 'network_environment' in data:
        p.network_environment = data['network_environment']
    if 'difficulty_tags' in data:
        p.difficulty_tags = data['difficulty_tags']
    p.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(serialize_device_profile(p))

@device_bp.route('/profiles/user/<int:user_id>', methods=['GET'])
def get_profile_by_user(user_id):
    p = DeviceProfile.query.filter_by(user_id=user_id).first()
    if not p:
        return jsonify(None)
    return jsonify(serialize_device_profile(p))

@device_bp.route('/profiles/<int:id>/supplement', methods=['POST'])
def supplement_device_profile(id):
    p = DeviceProfile.query.get_or_404(id)
    data = request.json
    if data.get('difficulty_tags'):
        existing_tags = set((p.difficulty_tags or '').split(',')) if p.difficulty_tags else set()
        new_tags = set(data['difficulty_tags'].split(','))
        p.difficulty_tags = ','.join(existing_tags | new_tags).strip(',')
    if data.get('common_apps'):
        existing_apps = set((p.common_apps or '').split(',')) if p.common_apps else set()
        new_apps = set(data['common_apps'].split(','))
        p.common_apps = ','.join(existing_apps | new_apps).strip(',')
    if data.get('device_brand'):
        p.device_brand = data['device_brand']
    if data.get('system_version'):
        p.system_version = data['system_version']
    if data.get('font_size_preference'):
        p.font_size_preference = data['font_size_preference']
    if 'simple_mode_enabled' in data:
        p.simple_mode_enabled = data['simple_mode_enabled']
    if data.get('network_environment'):
        p.network_environment = data['network_environment']
    p.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(serialize_device_profile(p))

@stepcard_bp.route('/<int:id>/device_tips', methods=['GET'])
def list_device_tips(id):
    s = StepCard.query.get_or_404(id)
    return jsonify([serialize_device_tip(dt) for dt in s.device_tips])

@stepcard_bp.route('/<int:id>/device_tips', methods=['POST'])
def add_device_tip(id):
    s = StepCard.query.get_or_404(id)
    data = request.json
    dt = StepCardDeviceTip(
        step_card_id=id,
        step_number=data['step_number'],
        device_brand=data['device_brand'],
        system_version=data.get('system_version'),
        adaptation_tip=data['adaptation_tip'],
        entry_name=data.get('entry_name')
    )
    db.session.add(dt)
    db.session.commit()
    return jsonify(serialize_device_tip(dt)), 201

@stepcard_bp.route('/<int:id>/device_tips/<int:tip_id>', methods=['PUT'])
def update_device_tip(id, tip_id):
    dt = StepCardDeviceTip.query.get_or_404(tip_id)
    if dt.step_card_id != id:
        return jsonify({'error': 'Tip does not belong to this step card'}), 400
    data = request.json
    if 'step_number' in data:
        dt.step_number = data['step_number']
    if 'device_brand' in data:
        dt.device_brand = data['device_brand']
    if 'system_version' in data:
        dt.system_version = data['system_version']
    if 'adaptation_tip' in data:
        dt.adaptation_tip = data['adaptation_tip']
    if 'entry_name' in data:
        dt.entry_name = data['entry_name']
    db.session.commit()
    return jsonify(serialize_device_tip(dt))

@stepcard_bp.route('/<int:id>/device_tips/<int:tip_id>', methods=['DELETE'])
def delete_device_tip(id, tip_id):
    dt = StepCardDeviceTip.query.get_or_404(tip_id)
    if dt.step_card_id != id:
        return jsonify({'error': 'Tip does not belong to this step card'}), 400
    db.session.delete(dt)
    db.session.commit()
    return jsonify({'success': True})

@stepcard_bp.route('/<int:id>/adaptation', methods=['GET'])
def get_step_adaptation(id):
    s = StepCard.query.get_or_404(id)
    device_brand = request.args.get('device_brand')
    system_version = request.args.get('system_version')
    tips = s.device_tips
    if device_brand:
        tips = [t for t in tips if t.device_brand == device_brand]
    if system_version:
        tips = [t for t in tips if t.system_version == system_version or t.system_version is None]
    steps_with_tips = []
    for step in sorted(s.steps, key=lambda x: x.step_number):
        step_tips = [t for t in tips if t.step_number == step.step_number]
        steps_with_tips.append({
            'step': serialize_step(step),
            'adaptation_tips': [serialize_device_tip(t) for t in step_tips]
        })
    return jsonify(steps_with_tips)

@stats_bp.route('/device', methods=['GET'])
def stats_device():
    from sqlalchemy import func, desc

    brand_stats = db.session.query(
        HelpRequest.device_brand,
        func.count(HelpRequest.id).label('count')
    ).filter(
        HelpRequest.device_brand != None
    ).group_by(HelpRequest.device_brand).all()

    system_stats = db.session.query(
        HelpRequest.system_version,
        func.count(HelpRequest.id).label('count')
    ).group_by(HelpRequest.system_version).all()

    brand_duration = db.session.query(
        HelpRequest.device_brand,
        func.avg(HelpRequest.resolution_duration).label('avg_duration')
    ).filter(
        HelpRequest.device_brand != None,
        HelpRequest.status == 'resolved',
        HelpRequest.resolution_duration != None
    ).group_by(HelpRequest.device_brand).all()

    brand_problem = db.session.query(
        HelpRequest.device_brand,
        HelpRequest.problem_type,
        func.count(HelpRequest.id).label('count')
    ).filter(
        HelpRequest.device_brand != None
    ).group_by(HelpRequest.device_brand, HelpRequest.problem_type).all()

    profiles = DeviceProfile.query.all()
    difficulty_tag_counts = {}
    for p in profiles:
        if p.difficulty_tags:
            tags = [t.strip() for t in p.difficulty_tags.split(',') if t.strip()]
            for tag in tags:
                difficulty_tag_counts[tag] = difficulty_tag_counts.get(tag, 0) + 1

    sorted_tags = sorted(difficulty_tag_counts.items(), key=lambda x: x[1], reverse=True)

    return jsonify({
        'brand_distribution': [{'brand': b or '未知', 'count': c} for b, c in brand_stats],
        'system_distribution': [{'system': s or '未知', 'count': c} for s, c in system_stats],
        'brand_avg_duration': [{'brand': b, 'avg_duration': round(d, 1)} for b, d in brand_duration],
        'brand_problem_distribution': [
            {'brand': b, 'problem_type': pt, 'count': c}
            for b, pt, c in brand_problem
        ],
        'top_difficulty_tags': [{'tag': t, 'count': c} for t, c in sorted_tags[:10]]
    })
