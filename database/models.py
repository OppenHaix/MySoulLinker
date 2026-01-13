from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(255), default='https://ui-avatars.com/api/?name=?&background=random&color=fff&size=128')
    notes = db.Column(db.Text, default='')
    tags = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chat_logs = db.relationship('ChatLog', backref='contact', lazy='dynamic', cascade='all, delete-orphan')
    analysis = db.relationship('AnalysisResult', backref='contact', uselist=False, cascade='all, delete-orphan')
    
    @property
    def sessions(self):
        logs = self.chat_logs.all()
        if not logs:
            return 0
        dates = set()
        for log in logs:
            dates.add(log.chat_date)
        return len(dates)
    
    @property
    def active_days(self):
        logs = self.chat_logs.all()
        if not logs:
            return 0
        dates = set()
        for log in logs:
            dates.add(log.chat_date)
        return len(dates)
    
    @property
    def analysis_count(self):
        return AnalysisResult.query.filter_by(contact_id=self.id).count()
    
    @property
    def avg_response_time(self):
        return None
    
    @property
    def longest_streak(self):
        return 0
    
    @property
    def last_active(self):
        latest_log = self.chat_logs.order_by(ChatLog.chat_date.desc()).first()
        if latest_log:
            return latest_log.chat_date.strftime('%Y-%m-%d')
        return None
    
    @property
    def relationship_trend(self):
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'avatar': self.avatar,
            'notes': self.notes,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'chat_count': self.chat_logs.count(),
            'sessions': self.sessions,
            'active_days': self.active_days,
            'analysis_count': self.analysis_count,
            'has_analysis': self.analysis is not None
        }

class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    speaker = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    chat_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'contact_id': self.contact_id,
            'speaker': self.speaker,
            'content': self.content,
            'chat_date': self.chat_date.isoformat() if self.chat_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AnalysisResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False, unique=True)
    
    core_traits = db.Column(db.Text, nullable=True)
    behavior_preferences = db.Column(db.Text, nullable=True)
    social_interaction = db.Column(db.Text, nullable=True)
    cognitive_thinking = db.Column(db.Text, nullable=True)
    
    summary = db.Column(db.Text, default='')
    interests = db.Column(db.Text, default='')
    dos_and_donts = db.Column(db.Text, default='')
    topic_suggestions = db.Column(db.Text, default='')
    gift_suggestions = db.Column(db.Text, default='')
    
    raw_response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_parsed_data(self):
        import json
        result = {}
        for field in ['core_traits', 'behavior_preferences', 'social_interaction', 'cognitive_thinking']:
            value = getattr(self, field)
            if value:
                try:
                    result[field] = json.loads(value)
                except json.JSONDecodeError:
                    result[field] = value
        
        if self.interests:
            try:
                result['interests'] = json.loads(self.interests)
            except json.JSONDecodeError:
                result['interests'] = self.interests
        
        if self.dos_and_donts:
            try:
                result['dos_and_donts'] = json.loads(self.dos_and_donts)
            except json.JSONDecodeError:
                result['dos_and_donts'] = self.dos_and_donts
        
        if self.topic_suggestions:
            try:
                result['topic_suggestions'] = json.loads(self.topic_suggestions)
            except json.JSONDecodeError:
                result['topic_suggestions'] = self.topic_suggestions
        
        if self.gift_suggestions:
            try:
                result['gift_suggestions'] = json.loads(self.gift_suggestions)
            except json.JSONDecodeError:
                result['gift_suggestions'] = self.gift_suggestions
        
        result['summary'] = self.summary
        return result
    
    def to_dict(self):
        return {
            'id': self.id,
            'contact_id': self.contact_id,
            'core_traits': self.core_traits,
            'behavior_preferences': self.behavior_preferences,
            'social_interaction': self.social_interaction,
            'cognitive_thinking': self.cognitive_thinking,
            'summary': self.summary,
            'interests': self.interests,
            'dos_and_donts': self.dos_and_donts,
            'topic_suggestions': self.topic_suggestions,
            'gift_suggestions': self.gift_suggestions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
