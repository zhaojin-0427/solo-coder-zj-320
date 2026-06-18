from datetime import datetime, timedelta
from app import db
from app.models import User, HelpRequest, GuidanceRecord, StepCard, StepCardStep, PracticeRecord, PracticeStepFeedback, DeviceProfile, StepCardDeviceTip

def seed_data():
    if User.query.count() > 0:
        return

    u1 = User(name='张奶奶', role='elder', phone='13800138001')
    u2 = User(name='小明', role='family', phone='13900139002')
    u3 = User(name='李爷爷', role='elder', phone='13700137003')
    db.session.add_all([u1, u2, u3])
    db.session.flush()

    dp1 = DeviceProfile(
        user_id=u1.id, device_brand='华为', system_version='HarmonyOS 4',
        font_size_preference='大', simple_mode_enabled=True,
        common_apps='微信,抖音,电话,短信,相机',
        network_environment='WiFi',
        difficulty_tags='找不到入口,看不清字'
    )
    dp3 = DeviceProfile(
        user_id=u3.id, device_brand='小米', system_version='MIUI 14',
        font_size_preference='超大', simple_mode_enabled=True,
        common_apps='微信,电话,相册,支付宝',
        network_environment='4G',
        difficulty_tags='找不到入口,不会切换网络,误触广告'
    )
    db.session.add_all([dp1, dp3])
    db.session.flush()

    sc1 = StepCard(title='调大手机字体', problem_type='看不清字', difficulty='easy',
                   device_brand='华为', system_version='HarmonyOS 3',
                   description='字体太小看不清，需要把字体调大', created_by=u2.id, usage_count=5)
    sc2 = StepCard(title='关闭手机弹窗广告', problem_type='误触广告', difficulty='normal',
                   device_brand='苹果', system_version='iOS 16',
                   description='手机总是弹出广告，总是误点到', created_by=u2.id, usage_count=3)
    sc3 = StepCard(title='连接家里的WiFi', problem_type='不会切换网络', difficulty='easy',
                   description='不会切换WiFi网络', created_by=u2.id, usage_count=8)
    sc4 = StepCard(title='找到手机相册', problem_type='找不到入口', difficulty='easy',
                   device_brand='小米', system_version='MIUI 14',
                   description='找不到相册在哪里', created_by=u2.id, usage_count=4)
    sc5 = StepCard(title='设置免密支付', problem_type='支付设置', difficulty='hard',
                   description='不会设置支付方式', created_by=u2.id, usage_count=2)
    db.session.add_all([sc1, sc2, sc3, sc4, sc5])
    db.session.flush()

    steps_sc1 = [
        StepCardStep(step_card_id=sc1.id, step_number=1, content='点击手机桌面上的「设置」图标', tip='图标是一个齿轮的样子'),
        StepCardStep(step_card_id=sc1.id, step_number=2, content='往下滑动找到「显示和亮度」，点击进去'),
        StepCardStep(step_card_id=sc1.id, step_number=3, content='找到「字体与显示大小」，点击进入'),
        StepCardStep(step_card_id=sc1.id, step_number=4, content='拖动「字体大小」下面的滑块，往右滑动字体变大', tip='建议调到中间偏右的位置'),
        StepCardStep(step_card_id=sc1.id, step_number=5, content='调整完成后直接返回，设置会自动保存'),
    ]
    steps_sc3 = [
        StepCardStep(step_card_id=sc3.id, step_number=1, content='从手机屏幕顶部往下滑，打开快捷设置面板'),
        StepCardStep(step_card_id=sc3.id, step_number=2, content='长按「WLAN」图标，进入WiFi设置'),
        StepCardStep(step_card_id=sc3.id, step_number=3, content='在列表里找到家里的WiFi名称，点击它', tip='名字通常写在路由器背面'),
        StepCardStep(step_card_id=sc3.id, step_number=4, content='输入WiFi密码，点击「连接」', tip='密码注意区分大小写'),
    ]
    steps_sc4 = [
        StepCardStep(step_card_id=sc4.id, step_number=1, content='在手机桌面上找到「相册」图标', tip='图标一般是彩色花朵或照片的样子'),
        StepCardStep(step_card_id=sc4.id, step_number=2, content='点击图标就能打开看到所有照片了'),
        StepCardStep(step_card_id=sc4.id, step_number=3, content='如果桌面上找不到，可以从底部往上滑进入全部应用列表查找'),
    ]
    db.session.add_all(steps_sc1 + steps_sc3 + steps_sc4)

    device_tips_data = [
        StepCardDeviceTip(step_card_id=sc1.id, step_number=1, device_brand='华为',
                         system_version='HarmonyOS 4', adaptation_tip='华为手机「设置」在桌面或应用抽屉中，图标为齿轮',
                         entry_name='设置'),
        StepCardDeviceTip(step_card_id=sc1.id, step_number=1, device_brand='苹果',
                         system_version='iOS 16', adaptation_tip='iPhone「设置」图标是灰色齿轮，在第一屏',
                         entry_name='Settings'),
        StepCardDeviceTip(step_card_id=sc1.id, step_number=2, device_brand='华为',
                         system_version='HarmonyOS 4', adaptation_tip='华为手机叫「显示和亮度」，在设置列表中上部',
                         entry_name='显示和亮度'),
        StepCardDeviceTip(step_card_id=sc1.id, step_number=2, device_brand='苹果',
                         system_version='iOS 16', adaptation_tip='iPhone 叫「显示与亮度」，在设置列表中',
                         entry_name='Display & Brightness'),
        StepCardDeviceTip(step_card_id=sc1.id, step_number=2, device_brand='小米',
                         system_version='MIUI 14', adaptation_tip='小米手机叫「显示」，在设置中',
                         entry_name='显示'),
        StepCardDeviceTip(step_card_id=sc1.id, step_number=3, device_brand='华为',
                         system_version='HarmonyOS 4', adaptation_tip='华为叫「字体与显示大小」',
                         entry_name='字体与显示大小'),
        StepCardDeviceTip(step_card_id=sc1.id, step_number=3, device_brand='苹果',
                         system_version='iOS 16', adaptation_tip='iPhone 在「显示与亮度」里点击「文字大小」',
                         entry_name='文字大小'),
        StepCardDeviceTip(step_card_id=sc3.id, step_number=2, device_brand='华为',
                         system_version='HarmonyOS 4', adaptation_tip='华为快捷面板中叫「WLAN」，长按进入',
                         entry_name='WLAN'),
        StepCardDeviceTip(step_card_id=sc3.id, step_number=2, device_brand='苹果',
                         system_version='iOS 16', adaptation_tip='iPhone 在「设置」中找「无线局域网」',
                         entry_name='无线局域网'),
        StepCardDeviceTip(step_card_id=sc3.id, step_number=2, device_brand='小米',
                         system_version='MIUI 14', adaptation_tip='小米叫「WLAN」，在设置第一项',
                         entry_name='WLAN'),
        StepCardDeviceTip(step_card_id=sc4.id, step_number=1, device_brand='华为',
                         system_version='HarmonyOS 4', adaptation_tip='华为相册图标是彩色花朵，桌面上可找到',
                         entry_name='图库'),
        StepCardDeviceTip(step_card_id=sc4.id, step_number=1, device_brand='苹果',
                         system_version='iOS 16', adaptation_tip='iPhone 相册叫「照片」，图标是彩色风车',
                         entry_name='照片'),
        StepCardDeviceTip(step_card_id=sc4.id, step_number=1, device_brand='小米',
                         system_version='MIUI 14', adaptation_tip='小米相册图标是彩色花',
                         entry_name='相册'),
    ]
    db.session.add_all(device_tips_data)

    now = datetime.utcnow()
    helps = []
    problem_types = ['看不清字', '找不到入口', '误触广告', '不会切换网络', '支付设置', '看不清字', '找不到入口', '误触广告', '不会切换网络', '看不清字', '找不到入口']
    for i, pt in enumerate(problem_types):
        created = now - timedelta(days=i*2, hours=i%3)
        h = HelpRequest(
            title=f'{pt}问题求助', problem_type=pt,
            description=f'遇到了{pt}的问题，不知道怎么办',
            device_brand=['华为', '苹果', '小米', 'OPPO'][i % 4],
            system_version=['HarmonyOS 3', 'iOS 16', 'MIUI 14', 'ColorOS 13'][i % 4],
            device_profile_id=dp1.id if i % 2 == 0 else dp3.id,
            status='resolved' if i < 9 else 'pending',
            requester_id=[u1.id, u3.id][i % 2],
            helper_id=u2.id,
            created_at=created,
            resolved_at=created + timedelta(minutes=10 + i * 3) if i < 9 else None,
            resolution_duration=10 + i * 3 if i < 9 else None,
            is_independent=[True, False, False, True, False, True, False, True, False][i % 9] if i < 9 else False,
            is_repeat=i in [5, 6, 7, 8, 9, 10],
            audio_url='https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3' if i == 0 else None
        )
        helps.append(h)
    db.session.add_all(helps)
    db.session.flush()

    for i, h in enumerate(helps[:3]):
        for j in range(1, 4):
            g = GuidanceRecord(
                help_request_id=h.id, step_number=j,
                content=f'第{j}步指导内容示例',
                tip=f'第{j}步的小贴士'
            )
            db.session.add(g)

    practice_data = [
        (sc1.id, u1.id, 'library', 'completed', True, None, 1, 5, ['completed', 'completed', 'completed', 'completed', 'completed']),
        (sc1.id, u3.id, 'library', 'completed', True, None, 0, 4, ['completed', 'completed', 'completed', 'completed', 'completed']),
        (sc1.id, u1.id, 'help_success', 'completed', False, 4, 1, 3, ['completed', 'completed', 'completed', 'cannot_understand', 'completed']),
        (sc3.id, u1.id, 'library', 'completed', True, None, 0, 6, ['completed', 'completed', 'completed', 'completed']),
        (sc3.id, u3.id, 'library', 'completed', False, 3, 2, 5, ['completed', 'completed', 'cannot_find', 'completed']),
        (sc3.id, u1.id, 'help_success', 'converted', False, 2, 3, 2, ['completed', 'cannot_understand', 'cannot_find', 'cannot_find']),
        (sc4.id, u3.id, 'library', 'completed', True, None, 0, 7, ['completed', 'completed', 'completed']),
        (sc4.id, u1.id, 'library', 'completed', False, 3, 1, 8, ['completed', 'completed', 'cannot_find']),
        (sc1.id, u3.id, 'library', 'completed', True, None, 0, 9, ['completed', 'completed', 'completed', 'completed', 'completed']),
        (sc3.id, u3.id, 'library', 'completed', True, None, 0, 10, ['completed', 'completed', 'completed', 'completed']),
    ]

    for sc_id, prac_id, source, status, is_indep, stuck_step, converted_idx, days_ago, step_statuses in practice_data:
        created = now - timedelta(days=days_ago, hours=10)
        completed = created + timedelta(minutes=5 + days_ago) if status != 'converted' else None

        p = PracticeRecord(
            step_card_id=sc_id,
            practitioner_id=prac_id,
            source=source,
            status=status,
            is_independent=is_indep,
            stuck_step_number=stuck_step,
            feedback='步骤写得很清楚，就是第三步找了半天' if stuck_step and stuck_step == 3 else None,
            converted_to_help=(status == 'converted'),
            help_request_id=helps[converted_idx].id if status == 'converted' else None,
            created_at=created,
            completed_at=completed
        )
        db.session.add(p)
        db.session.flush()

        for idx, step_status in enumerate(step_statuses):
            step_num = idx + 1
            step = StepCardStep.query.filter_by(step_card_id=sc_id, step_number=step_num).first()
            if step:
                psf = PracticeStepFeedback(
                    practice_record_id=p.id,
                    step_card_step_id=step.id,
                    step_number=step_num,
                    status=step_status,
                    feedback='这里写得有点不清楚' if step_status == 'cannot_understand' else '找不到这个按钮在哪里' if step_status == 'cannot_find' else None,
                    created_at=created + timedelta(minutes=idx)
                )
                db.session.add(psf)

    db.session.commit()
