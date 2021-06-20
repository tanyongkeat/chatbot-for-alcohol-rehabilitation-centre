from app import db
from datetime import datetime

MAX_USER_INPUT_LEN = 150

class Captured(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utterence = db.Column(db.String(512), unique=False, nullable=False)

class HistoryFull(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, nullable=False)
    utterance_original = db.Column(db.String(MAX_USER_INPUT_LEN))
    utterance = db.Column(db.String(MAX_USER_INPUT_LEN))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    positive = db.Column(db.Boolean, default=False)
    negative = db.Column(db.Boolean, default=False)
    trained = db.Column(db.Boolean, default=False)
    predicted_intent_id_top = db.Column(db.Integer, nullable=False)
    predicted_intent_id = db.Column(db.String(10), nullable=False)
    __table_args__ = {'extend_existing': True}

class Intent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    intent_name = db.Column(db.String(50), nullable=False, unique=True)
    reply_message_en = db.Column(db.String(500), nullable=False)
    reply_message_my = db.Column(db.String(500), nullable=False)
    small_talk = db.Column(db.Boolean, default=False)
    deployed = db.Column(db.Boolean, default=True)
    training_data = db.relationship('TrainingData', backref='intent', cascade='all,delete')

class TrainingData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.String(MAX_USER_INPUT_LEN), nullable=False)
    intent_id = db.Column(db.Integer, db.ForeignKey('intent.id'), nullable=False)
