from flask import Flask, render_template, request, jsonify, send_file, Response, make_response
from config import Config
from database.models import db, Contact, ChatLog, AnalysisResult
from utils.ai import get_ai_analysis, parse_ai_response, stream_ai_analysis
from utils.exporter import (
    export_chat_logs_to_csv, export_chat_logs_to_excel, export_chat_logs_to_multiple_formats,
    export_analysis_to_excel, export_analysis_to_json, export_analysis_to_pdf, export_analysis_to_multiple_formats,
    generate_summary_report
)
import json
from datetime import datetime, timedelta
import os
from collections import defaultdict

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.template_filter('activity_level_text')
def _activity_level_text(level):
    level_map = {
        'high': '高活跃',
        'medium': '中活跃',
        'low': '低活跃',
        'very_high': '极高活跃',
        'very_low': '极低活跃'
    }
    return level_map.get(level, '低活跃')

@app.context_processor
def inject_activity_level_text():
    def activity_level_text(level):
        level_map = {
            'high': '高活跃',
            'medium': '中活跃',
            'low': '低活跃',
            'very_high': '极高活跃',
            'very_low': '极低活跃'
        }
        return level_map.get(level, '低活跃')
    return dict(activity_level_text=activity_level_text)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/contacts')
def contacts_page():
    contacts = Contact.query.order_by(Contact.updated_at.desc()).all()
    return render_template('index.html', contacts=[c.to_dict() for c in contacts])

@app.route('/set_username', methods=['POST'])
def set_username():
    username = request.form.get('username', '').strip()
    if not username:
        return render_template('landing.html', error='请输入你的名字')
    response = make_response(render_template('redirect.html', username=username))
    response.set_cookie('username', username, max_age=60*60*24*30)
    return response

@app.route('/home')
def home_page():
    username = request.cookies.get('username') or '朋友'
    now = datetime.now()
    
    total_contacts = Contact.query.count()
    total_messages = ChatLog.query.count()
    total_analyses = AnalysisResult.query.count()
    
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_this_month = Contact.query.filter(Contact.created_at >= month_start).count()
    
    thirty_days_ago = now - timedelta(days=30)
    active_relationships = Contact.query.filter(
        Contact.updated_at >= thirty_days_ago
    ).count()
    
    analysis_rate = int(total_analyses / total_contacts * 100) if total_contacts > 0 else 0
    
    stats = {
        'total_contacts': total_contacts,
        'total_messages': total_messages,
        'total_analyses': total_analyses,
        'new_this_month': new_this_month,
        'active_relationships': active_relationships,
        'analysis_rate': analysis_rate
    }
    
    recent_contacts = Contact.query.order_by(Contact.updated_at.desc()).limit(5).all()
    
    need_attention = []
    for contact in recent_contacts:
        chat_count = ChatLog.query.filter_by(contact_id=contact.id).count()
        if chat_count > 0 and not contact.analysis:
            need_attention.append({
                'id': contact.id,
                'name': contact.name,
                'reason': '有待分析的聊天记录'
            })
    
    for contact in recent_contacts[:2]:
        chat_count = ChatLog.query.filter_by(contact_id=contact.id).count()
        if chat_count > 30 and not contact.analysis:
            need_attention.append({
                'id': contact.id,
                'name': contact.name,
                'reason': '积累了大量聊天记录'
            })
    
    activity_data = []
    for i in range(30):
        date = (now - timedelta(days=29 - i)).date()
        count = ChatLog.query.filter(
            ChatLog.chat_date == date
        ).count()
        activity_data.append({
            'date': str(date),
            'count': count
        })
    
    insights = None
    if total_contacts > 0:
        avg_messages = total_messages / total_contacts if total_contacts > 0 else 0
        most_active = db.session.query(
            Contact, db.func.count(ChatLog.id).label('chat_count')
        ).join(ChatLog).group_by(Contact.id).order_by(
            db.desc('chat_count')
        ).first()
        
        insights = {
            'avg_messages_per_contact': f'{avg_messages:.1f}',
            'most_active_contact': most_active[0].name if most_active else '-',
            'analysis_coverage': analysis_rate
        }
    
    greeting = now.strftime('%H:%M')
    if now.hour < 6:
        greeting = "夜猫子"
    elif now.hour < 12:
        greeting = "早上好"
    elif now.hour < 14:
        greeting = "中午好"
    elif now.hour < 18:
        greeting = "下午好"
    else:
        greeting = "晚上好"
    
    return render_template(
        'home.html',
        greeting=greeting,
        username=username,
        stats=stats,
        recent_contacts=[c.to_dict() for c in recent_contacts],
        need_attention=need_attention[:3],
        activity_data=activity_data,
        insights=insights
    )

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    contacts = Contact.query.order_by(Contact.updated_at.desc()).all()
    return jsonify({'contacts': [c.to_dict() for c in contacts]})

@app.route('/api/contacts', methods=['POST'])
def create_contact():
    data = request.get_json()
    contact = Contact(
        name=data.get('name'),
        avatar=data.get('avatar', ''),
        notes=data.get('notes', ''),
        tags=data.get('tags', '')
    )
    db.session.add(contact)
    db.session.commit()
    return jsonify({'contact': contact.to_dict()}), 201

@app.route('/api/contacts/<int:id>', methods=['GET'])
def get_contact(id):
    contact = Contact.query.get_or_404(id)
    return jsonify({'contact': contact.to_dict()})

@app.route('/api/contacts/<int:id>', methods=['PUT'])
def update_contact(id):
    contact = Contact.query.get_or_404(id)
    data = request.get_json()
    contact.name = data.get('name', contact.name)
    contact.avatar = data.get('avatar', contact.avatar)
    contact.notes = data.get('notes', contact.notes)
    contact.tags = data.get('tags', contact.tags)
    db.session.commit()
    return jsonify({'contact': contact.to_dict()})

@app.route('/api/contacts/<int:id>', methods=['DELETE'])
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'message': '删除成功'})

@app.route('/labeling/<int:contact_id>')
def labeling_page(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    return render_template('labeling.html', contact=contact)

@app.route('/api/contacts/<int:contact_id>/chat-logs', methods=['GET'])
def get_chat_logs(contact_id):
    chat_logs = ChatLog.query.filter_by(contact_id=contact_id).order_by(ChatLog.chat_date, ChatLog.created_at).all()
    return jsonify({'chat_logs': [log.to_dict() for log in chat_logs]})

@app.route('/api/contacts/<int:contact_id>/chat-logs', methods=['POST'])
def add_chat_logs(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    data = request.get_json()
    
    lines = data.get('lines', [])
    chat_date = datetime.strptime(data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
    
    for line_data in lines:
        chat_log = ChatLog(
            contact_id=contact_id,
            speaker=line_data.get('speaker', '对方'),
            content=line_data.get('content', ''),
            chat_date=chat_date
        )
        db.session.add(chat_log)
    
    contact.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': '保存成功', 'count': len(lines)})

@app.route('/profile/<int:contact_id>')
def profile_page(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    chat_logs = ChatLog.query.filter_by(contact_id=contact_id).order_by(ChatLog.chat_date, ChatLog.created_at).all()
    analysis = AnalysisResult.query.filter_by(contact_id=contact_id).first()
    
    return render_template('profile.html', contact=contact, chat_logs=chat_logs, analysis=analysis)

@app.route('/api/contacts/<int:contact_id>/analyze', methods=['POST'])
def analyze_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    chat_logs = ChatLog.query.filter_by(contact_id=contact_id).order_by(ChatLog.chat_date).all()
    
    if not chat_logs:
        return jsonify({'error': '没有聊天记录可分析'}), 400
    
    chat_content = '\n'.join([
        f"[{log.chat_date}]【我】{log.content}" if log.speaker == '我' else f"[{log.chat_date}]【对方】{log.content}"
        for log in chat_logs
    ])
    
    api_key = request.json.get('api_key') if request.json else None
    analysis_result = get_ai_analysis(chat_content, api_key)
    
    if 'error' in analysis_result:
        return jsonify(analysis_result), 500
    
    parsed_result = parse_ai_response(analysis_result)
    
    existing_analysis = AnalysisResult.query.filter_by(contact_id=contact_id).first()
    
    if existing_analysis:
        existing_analysis.core_traits = json.dumps(parsed_result.get('core_traits', {}), ensure_ascii=False)
        existing_analysis.behavior_preferences = json.dumps(parsed_result.get('behavior_preferences', {}), ensure_ascii=False)
        existing_analysis.social_interaction = json.dumps(parsed_result.get('social_interaction', {}), ensure_ascii=False)
        existing_analysis.cognitive_thinking = json.dumps(parsed_result.get('cognitive_thinking', {}), ensure_ascii=False)
        existing_analysis.summary = parsed_result.get('summary', '')
        existing_analysis.interests = json.dumps(parsed_result.get('interests', []), ensure_ascii=False)
        existing_analysis.dos_and_donts = json.dumps(parsed_result.get('dos_and_donts', {}), ensure_ascii=False)
        existing_analysis.topic_suggestions = json.dumps(parsed_result.get('topic_suggestions', []), ensure_ascii=False)
        existing_analysis.gift_suggestions = json.dumps(parsed_result.get('gift_suggestions', []), ensure_ascii=False)
        existing_analysis.raw_response = json.dumps(analysis_result, ensure_ascii=False)
        existing_analysis.updated_at = datetime.utcnow()
        analysis = existing_analysis
    else:
        analysis = AnalysisResult(
            contact_id=contact_id,
            core_traits=json.dumps(parsed_result.get('core_traits', {}), ensure_ascii=False),
            behavior_preferences=json.dumps(parsed_result.get('behavior_preferences', {}), ensure_ascii=False),
            social_interaction=json.dumps(parsed_result.get('social_interaction', {}), ensure_ascii=False),
            cognitive_thinking=json.dumps(parsed_result.get('cognitive_thinking', {}), ensure_ascii=False),
            summary=parsed_result.get('summary', ''),
            interests=json.dumps(parsed_result.get('interests', []), ensure_ascii=False),
            dos_and_donts=json.dumps(parsed_result.get('dos_and_donts', {}), ensure_ascii=False),
            topic_suggestions=json.dumps(parsed_result.get('topic_suggestions', []), ensure_ascii=False),
            gift_suggestions=json.dumps(parsed_result.get('gift_suggestions', []), ensure_ascii=False),
            raw_response=json.dumps(analysis_result, ensure_ascii=False)
        )
        db.session.add(analysis)
    
    contact.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'analysis': analysis.to_dict()})

@app.route('/api/contacts/<int:contact_id>/analyze/stream', methods=['POST'])
def analyze_contact_stream(contact_id):
    print(f"[Stream Debug] API called: contact_id={contact_id}")
    data = request.get_json()
    
    def generate(data):
        print(f"[Stream Debug] generate() called for contact_id={contact_id}")
        with app.app_context():
            contact = Contact.query.get_or_404(contact_id)
            
            chat_logs = ChatLog.query.filter_by(contact_id=contact_id).order_by(ChatLog.chat_date).all()
            
            print(f"[Stream Debug] Found {len(chat_logs)} chat logs")
            
            if not chat_logs:
                yield json.dumps({'type': 'error', 'message': '没有聊天记录可分析'})
                return
            
            chat_content = '\n'.join([
                f"[{log.chat_date}]【我】{log.content}" if log.speaker == '我' else f"[{log.chat_date}]【对方】{log.content}"
                for log in chat_logs
            ])
            
            print(f"[Stream Debug] Chat content length: {len(chat_content)}")
            
            api_key = data.get('api_key')
            
            result = None
            accumulated_content = ""
            chunk_count = 0
            for item in stream_ai_analysis(chat_content, api_key):
                chunk_count += 1
                print(f"[Stream Debug] Chunk {chunk_count}: {item}")
                
                if 'error' in item:
                    yield json.dumps({'type': 'error', 'message': item['error']})
                    return
                elif item.get('type') == 'content_update':
                    accumulated_content += item.get('content', '')
                    content_length = len(accumulated_content)
                    yield json.dumps({
                        'type': 'content_update',
                        'content_length': content_length,
                        'total_tokens': item.get('total_tokens', 0),
                        'completion_tokens': item.get('completion_tokens', 0)
                    }) + '\n'
                elif item.get('type') == 'token_update':
                    yield json.dumps({
                        'type': 'token_update',
                        'total_tokens': item.get('total_tokens', 0),
                        'completion_tokens': item.get('completion_tokens', 0)
                    }) + '\n'
                elif 'result' in item or 'raw_response' in item:
                    result = item
            
            if result is None:
                yield json.dumps({'type': 'error', 'message': '未能获取分析结果'})
                return
            
            if 'result' in result:
                parsed_result = result['result']
            else:
                parsed_result = parse_ai_response(result)
            
            existing_analysis = AnalysisResult.query.filter_by(contact_id=contact_id).first()
            
            if existing_analysis:
                existing_analysis.core_traits = json.dumps(parsed_result.get('core_traits', {}), ensure_ascii=False)
                existing_analysis.behavior_preferences = json.dumps(parsed_result.get('behavior_preferences', {}), ensure_ascii=False)
                existing_analysis.social_interaction = json.dumps(parsed_result.get('social_interaction', {}), ensure_ascii=False)
                existing_analysis.cognitive_thinking = json.dumps(parsed_result.get('cognitive_thinking', {}), ensure_ascii=False)
                existing_analysis.summary = parsed_result.get('summary', '')
                existing_analysis.interests = json.dumps(parsed_result.get('interests', []), ensure_ascii=False)
                existing_analysis.dos_and_donts = json.dumps(parsed_result.get('dos_and_donts', {}), ensure_ascii=False)
                existing_analysis.topic_suggestions = json.dumps(parsed_result.get('topic_suggestions', []), ensure_ascii=False)
                existing_analysis.gift_suggestions = json.dumps(parsed_result.get('gift_suggestions', []), ensure_ascii=False)
                existing_analysis.raw_response = json.dumps(result, ensure_ascii=False)
                existing_analysis.updated_at = datetime.utcnow()
                analysis = existing_analysis
            else:
                analysis = AnalysisResult(
                    contact_id=contact_id,
                    core_traits=json.dumps(parsed_result.get('core_traits', {}), ensure_ascii=False),
                    behavior_preferences=json.dumps(parsed_result.get('behavior_preferences', {}), ensure_ascii=False),
                    social_interaction= json.dumps(parsed_result.get('social_interaction', {}), ensure_ascii=False),
                    cognitive_thinking=json.dumps(parsed_result.get('cognitive_thinking', {}), ensure_ascii=False),
                    summary=parsed_result.get('summary', ''),
                    interests=json.dumps(parsed_result.get('interests', []), ensure_ascii=False),
                    dos_and_donts=json.dumps(parsed_result.get('dos_and_donts', {}), ensure_ascii=False),
                    topic_suggestions=json.dumps(parsed_result.get('topic_suggestions', []), ensure_ascii=False),
                    gift_suggestions=json.dumps(parsed_result.get('gift_suggestions', []), ensure_ascii=False),
                    raw_response=json.dumps(result, ensure_ascii=False)
                )
                db.session.add(analysis)
            
            contact.updated_at = datetime.utcnow()
            db.session.commit()
            
            yield json.dumps({
                'type': 'complete',
                'analysis': analysis.to_dict(),
                'message_count': len(chat_logs),
                'total_tokens': result.get('total_tokens', 0),
                'completion_tokens': result.get('completion_tokens', 0)
            }) + '\n'
            print(f"[Stream Debug] Sent complete event with tokens: total={result.get('total_tokens', 0)}, completion={result.get('completion_tokens', 0)}")
    
    return Response(generate(data), mimetype='text/event-stream')

@app.route('/api/contacts/<int:contact_id>/analysis', methods=['GET'])
def get_analysis(contact_id):
    analysis = AnalysisResult.query.filter_by(contact_id=contact_id).first()
    if not analysis:
        return jsonify({'error': '没有分析结果'}), 404
    return jsonify({'analysis': analysis.to_dict()})

@app.route('/api/contacts/<int:contact_id>/analyze-selected', methods=['POST'])
def analyze_selected_messages(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    data = request.get_json()
    
    selected_ids = data.get('message_ids', [])
    if not selected_ids:
        return jsonify({'error': '请选择要分析的聊天记录'}), 400
    
    chat_logs = ChatLog.query.filter(
        ChatLog.contact_id == contact_id,
        ChatLog.id.in_(selected_ids)
    ).order_by(ChatLog.chat_date).all()
    
    if not chat_logs:
        return jsonify({'error': '没有找到选中的聊天记录'}), 400
    
    chat_content = '\n'.join([
        f"[{log.chat_date}]【我】{log.content}" if log.speaker == '我' else f"[{log.chat_date}]【对方】{log.content}"
        for log in chat_logs
    ])
    
    if len(chat_content) < 50:
        return jsonify({'error': '聊天记录内容太少，无法进行有效分析'}), 400
    
    api_key = data.get('api_key')
    analysis_result = get_ai_analysis(chat_content, api_key)
    
    if 'error' in analysis_result:
        return jsonify(analysis_result), 500
    
    parsed_result = parse_ai_response(analysis_result)
    
    existing_analysis = AnalysisResult.query.filter_by(contact_id=contact_id).first()
    
    if existing_analysis:
        existing_analysis.core_traits = json.dumps(parsed_result.get('core_traits', {}), ensure_ascii=False)
        existing_analysis.behavior_preferences = json.dumps(parsed_result.get('behavior_preferences', {}), ensure_ascii=False)
        existing_analysis.social_interaction = json.dumps(parsed_result.get('social_interaction', {}), ensure_ascii=False)
        existing_analysis.cognitive_thinking = json.dumps(parsed_result.get('cognitive_thinking', {}), ensure_ascii=False)
        existing_analysis.summary = parsed_result.get('summary', '')
        existing_analysis.interests = json.dumps(parsed_result.get('interests', []), ensure_ascii=False)
        existing_analysis.dos_and_donts = json.dumps(parsed_result.get('dos_and_donts', {}), ensure_ascii=False)
        existing_analysis.topic_suggestions = json.dumps(parsed_result.get('topic_suggestions', []), ensure_ascii=False)
        existing_analysis.gift_suggestions = json.dumps(parsed_result.get('gift_suggestions', []), ensure_ascii=False)
        existing_analysis.raw_response = json.dumps(analysis_result, ensure_ascii=False)
        existing_analysis.updated_at = datetime.utcnow()
        analysis = existing_analysis
    else:
        analysis = AnalysisResult(
            contact_id=contact_id,
            core_traits=json.dumps(parsed_result.get('core_traits', {}), ensure_ascii=False),
            behavior_preferences=json.dumps(parsed_result.get('behavior_preferences', {}), ensure_ascii=False),
            social_interaction= json.dumps(parsed_result.get('social_interaction', {}), ensure_ascii=False),
            cognitive_thinking=json.dumps(parsed_result.get('cognitive_thinking', {}), ensure_ascii=False),
            summary=parsed_result.get('summary', ''),
            interests=json.dumps(parsed_result.get('interests', []), ensure_ascii=False),
            dos_and_donts=json.dumps(parsed_result.get('dos_and_donts', {}), ensure_ascii=False),
            topic_suggestions=json.dumps(parsed_result.get('topic_suggestions', []), ensure_ascii=False),
            gift_suggestions=json.dumps(parsed_result.get('gift_suggestions', []), ensure_ascii=False),
            raw_response=json.dumps(analysis_result, ensure_ascii=False)
        )
        db.session.add(analysis)
    
    contact.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'analysis': analysis.to_dict(), 'message_count': len(chat_logs)})

@app.route('/api/contacts/<int:contact_id>/analyze-selected/stream', methods=['POST'])
def analyze_selected_messages_stream(contact_id):
    print(f"[Stream Debug] analyze-selected/stream called: contact_id={contact_id}")
    data = request.get_json()
    print(f"[Stream Debug] Request data: {data}")
    
    def generate(data):
        print(f"[Stream Debug] generate() started")
        with app.app_context():
            contact = Contact.query.get_or_404(contact_id)
            
            selected_ids = data.get('message_ids', [])
            if not selected_ids:
                yield json.dumps({'type': 'error', 'message': '请选择要分析的聊天记录'})
                return
            
            chat_logs = ChatLog.query.filter(
                ChatLog.contact_id == contact_id,
                ChatLog.id.in_(selected_ids)
            ).order_by(ChatLog.chat_date).all()
            
            if not chat_logs:
                yield json.dumps({'type': 'error', 'message': '没有找到选中的聊天记录'})
                return
            
            chat_content = '\n'.join([
                f"[{log.chat_date}]【我】{log.content}" if log.speaker == '我' else f"[{log.chat_date}]【对方】{log.content}"
                for log in chat_logs
            ])
            
            if len(chat_content) < 50:
                yield json.dumps({'type': 'error', 'message': '聊天记录内容太少，无法进行有效分析'})
                return
            
            api_key = data.get('api_key')
            
            result = None
            accumulated_content = ""
            for item in stream_ai_analysis(chat_content, api_key):
                if 'error' in item:
                    yield json.dumps({'type': 'error', 'message': item['error']})
                    return
                elif item.get('type') == 'content_update':
                    accumulated_content += item.get('content', '')
                    content_length = len(accumulated_content)
                    yield json.dumps({
                        'type': 'content_update',
                        'content_length': content_length,
                        'total_tokens': item.get('total_tokens', 0),
                        'completion_tokens': item.get('completion_tokens', 0)
                    }) + '\n'
                elif item.get('type') == 'token_update':
                    yield json.dumps({
                        'type': 'token_update',
                        'total_tokens': item.get('total_tokens', 0),
                        'completion_tokens': item.get('completion_tokens', 0)
                    }) + '\n'
                elif 'result' in item or 'raw_response' in item:
                    result = item
            
            if result is None:
                yield json.dumps({'type': 'error', 'message': '未能获取分析结果'})
                return
            
            if 'result' in result:
                parsed_result = result['result']
            else:
                parsed_result = parse_ai_response(result)
            
            existing_analysis = AnalysisResult.query.filter_by(contact_id=contact_id).first()
            
            if existing_analysis:
                existing_analysis.core_traits = json.dumps(parsed_result.get('core_traits', {}), ensure_ascii=False)
                existing_analysis.behavior_preferences = json.dumps(parsed_result.get('behavior_preferences', {}), ensure_ascii=False)
                existing_analysis.social_interaction = json.dumps(parsed_result.get('social_interaction', {}), ensure_ascii=False)
                existing_analysis.cognitive_thinking = json.dumps(parsed_result.get('cognitive_thinking', {}), ensure_ascii=False)
                existing_analysis.summary = parsed_result.get('summary', '')
                existing_analysis.interests = json.dumps(parsed_result.get('interests', []), ensure_ascii=False)
                existing_analysis.dos_and_donts = json.dumps(parsed_result.get('dos_and_donts', {}), ensure_ascii=False)
                existing_analysis.topic_suggestions = json.dumps(parsed_result.get('topic_suggestions', []), ensure_ascii=False)
                existing_analysis.gift_suggestions = json.dumps(parsed_result.get('gift_suggestions', []), ensure_ascii=False)
                existing_analysis.raw_response = json.dumps(result, ensure_ascii=False)
                existing_analysis.updated_at = datetime.utcnow()
                analysis = existing_analysis
            else:
                analysis = AnalysisResult(
                    contact_id=contact_id,
                    core_traits=json.dumps(parsed_result.get('core_traits', {}), ensure_ascii=False),
                    behavior_preferences=json.dumps(parsed_result.get('behavior_preferences', {}), ensure_ascii=False),
                    social_interaction= json.dumps(parsed_result.get('social_interaction', {}), ensure_ascii=False),
                    cognitive_thinking=json.dumps(parsed_result.get('cognitive_thinking', {}), ensure_ascii=False),
                    summary=parsed_result.get('summary', ''),
                    interests=json.dumps(parsed_result.get('interests', []), ensure_ascii=False),
                    dos_and_donts=json.dumps(parsed_result.get('dos_and_donts', {}), ensure_ascii=False),
                    topic_suggestions=json.dumps(parsed_result.get('topic_suggestions', []), ensure_ascii=False),
                    gift_suggestions=json.dumps(parsed_result.get('gift_suggestions', []), ensure_ascii=False),
                    raw_response=json.dumps(result, ensure_ascii=False)
                )
                db.session.add(analysis)
            
            contact.updated_at = datetime.utcnow()
            db.session.commit()
            
            yield json.dumps({
                'type': 'complete',
                'analysis': analysis.to_dict(),
                'message_count': len(chat_logs),
                'total_tokens': result.get('total_tokens', 0),
                'completion_tokens': result.get('completion_tokens', 0)
            }) + '\n'
            print(f"[Stream Debug] Sent complete event with tokens: total={result.get('total_tokens', 0)}, completion={result.get('completion_tokens', 0)}")
    
    return Response(generate(data), mimetype='text/event-stream')

@app.route('/export/<int:contact_id>')
def export_page(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    return render_template('export.html', contact=contact)

@app.route('/api/contacts/<int:contact_id>/export/chat-logs')
def export_chat_logs(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    
    formats = request.args.get('formats', 'xlsx').split(',')
    include_analysis = request.args.get('include_analysis', 'false').lower() == 'true'
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = ChatLog.query.filter_by(contact_id=contact_id)
    
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(ChatLog.chat_date >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(ChatLog.chat_date <= end)
        except ValueError:
            pass
    
    chat_logs = query.order_by(ChatLog.chat_date).all()
    
    if not chat_logs:
        return jsonify({'error': '没有聊天记录可导出'}), 400
    
    if len(formats) > 1 or 'csv' in formats:
        if 'csv' in formats and 'xlsx' in formats:
            filepath, filename = export_chat_logs_to_multiple_formats(chat_logs, contact.name, formats, include_analysis)
            mimetype = 'application/zip'
        elif 'csv' in formats:
            filepath, filename = export_chat_logs_to_csv(chat_logs, contact.name)
            mimetype = 'text/csv'
        else:
            filepath, filename = export_chat_logs_to_excel(chat_logs, contact.name, include_analysis)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        filepath, filename = export_chat_logs_to_excel(chat_logs, contact.name, include_analysis)
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype=mimetype
    )

@app.route('/api/contacts/<int:contact_id>/export/analysis')
def export_analysis(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    analysis = AnalysisResult.query.filter_by(contact_id=contact_id).first()
    
    if not analysis:
        return jsonify({'error': '没有分析结果可导出'}), 400
    
    formats = request.args.get('formats', 'xlsx').split(',')
    include_personality = request.args.get('include_personality', 'true').lower() == 'true'
    include_interests = request.args.get('include_interests', 'true').lower() == 'true'
    include_guide = request.args.get('include_guide', 'true').lower() == 'true'
    
    if len(formats) > 1:
        filepath, filename = export_analysis_to_multiple_formats(
            analysis, contact.name, formats,
            include_personality=include_personality,
            include_interests=include_interests,
            include_guide=include_guide
        )
        mimetype = 'application/zip'
    elif formats[0] == 'json':
        filepath, filename = export_analysis_to_json(analysis, contact.name)
        mimetype = 'application/json'
    elif formats[0] == 'pdf':
        filepath, filename = export_analysis_to_pdf(analysis, contact.name)
        mimetype = 'application/pdf'
    else:
        filepath, filename = export_analysis_to_excel(
            analysis, contact.name,
            include_personality=include_personality,
            include_interests=include_interests,
            include_guide=include_guide
        )
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype=mimetype
    )

if __name__ == '__main__':
    os.makedirs('exports', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
