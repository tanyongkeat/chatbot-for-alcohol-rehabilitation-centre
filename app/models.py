from app import db
from datetime import datetime
from dataclasses import dataclass

MAX_USER_INPUT_LEN = 150

# @dataclass
class Captured(db.Model):
    # id: int
    # utterance: str

    id = db.Column(db.Integer, primary_key=True)
    utterence = db.Column(db.String(512), unique=False, nullable=False)

@dataclass
class HistoryFull(db.Model):
    # __table_args__ = {'extend_existing': True}
    id:int = db.Column(db.Integer, primary_key=True)
    chat_id:int = db.Column(db.Integer, nullable=False)
    utterance_original:str = db.Column(db.String(MAX_USER_INPUT_LEN))
    utterance:str = db.Column(db.String(MAX_USER_INPUT_LEN))
    predicted_intent_id_top:int = db.Column(db.Integer, nullable=False)
    predicted_intent_id:str = db.Column(db.String(10), nullable=False)
    timestamp:datetime = db.Column(db.DateTime, default=datetime.utcnow)
    positive:bool = db.Column(db.Boolean, default=False)
    negative:bool = db.Column(db.Boolean, default=False)
    trained:bool = db.Column(db.Boolean, default=False)

@dataclass
class TrainingData(db.Model):
    id: int
    user_message: str
    intent_id: int

    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.String(MAX_USER_INPUT_LEN), nullable=False, unique=True)
    intent_id = db.Column(db.Integer, db.ForeignKey('intent.id'), nullable=False)
    encoding:str = db.Column(db.JSON, nullable=False)

@dataclass
class Intent(db.Model):
    id:int = db.Column(db.Integer, primary_key=True)
    intent_name:str = db.Column(db.String(50), nullable=False, unique=True)
    reply_message_en:str = db.Column(db.String(500), nullable=False)
    reply_message_my:str = db.Column(db.String(500), nullable=False)
    training_data:TrainingData = db.relationship('TrainingData', backref='intent', cascade='all,delete')
    small_talk:bool = db.Column(db.Boolean, default=False)
    deployed:bool = db.Column(db.Boolean, default=True)