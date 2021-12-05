from app import db, login_manager
from datetime import datetime
from dataclasses import dataclass
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash



@login_manager.user_loader
def load_user(id):
    return Admin.query.get(int(id))



MAX_USER_INPUT_LEN = 150
MAX_REPLY_LEN = 500
MAX_EMAIL_LEN = 320
MAX_INTENT_NAME_LEN = 50
MAX_LANG_CODE_LEN = 10

# @dataclass
class Captured(db.Model):
    # id: int
    # utterance: str

    id = db.Column(db.Integer, primary_key=True)
    utterence = db.Column(db.String(512), unique=False, nullable=False)

@dataclass
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@dataclass
class HistoryFull(db.Model):
    # __table_args__ = {'extend_existing': True}
    id:int = db.Column(db.Integer, primary_key=True)
    chat_id:int = db.Column(db.Integer, db.ForeignKey('chat_history.id'), nullable=False)
    utterance_original:str = db.Column(db.String(MAX_USER_INPUT_LEN))
    utterance:str = db.Column(db.String(MAX_USER_INPUT_LEN))
    predicted_intent_id_top:int = db.Column(db.Integer, nullable=False)
    predicted_intent_id:str = db.Column(db.String(50), nullable=False)
    timestamp:datetime = db.Column(db.DateTime, default=datetime.utcnow)
    positive:bool = db.Column(db.Boolean, default=False)
    negative:bool = db.Column(db.Boolean, default=False)
    trained:bool = db.Column(db.Boolean, default=False)
    is_selection:bool = db.Column(db.Boolean, nullable=False, default=False)

@dataclass
class ChatHistory(db.Model):
    id:int = db.Column(db.Integer, primary_key=True)
    user_email:str = db.Column(db.String(MAX_EMAIL_LEN)) # max email address character number is 320, setting nullable first to prevent stakeholder from changing their mind to suddenly respect the 'privacy' of the users
    user_name:str = db.Column(db.String(MAX_USER_INPUT_LEN))
    history_full:HistoryFull = db.relationship('HistoryFull', backref='chat_history', cascade='all,delete')

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
class Response(db.Model):
    id: int
    intent_id: int
    lang: str
    text: str
    selection: str

    id = db.Column(db.Integer, primary_key=True)
    intent_id = db.Column(db.Integer, db.ForeignKey('intent.id'), nullable=False)
    lang = db.Column(db.String(MAX_LANG_CODE_LEN), nullable=False)
    text = db.Column(db.String(MAX_REPLY_LEN), nullable=False)
    selection = db.Column(db.String(MAX_USER_INPUT_LEN), nullable=False)
    selection_encoding:str = db.Column(db.JSON, nullable=False)

@dataclass
class Intent(db.Model):
    id:int = db.Column(db.Integer, primary_key=True)
    intent_name:str = db.Column(db.String(MAX_INTENT_NAME_LEN), nullable=False, unique=True)
    reply_message_en:str = db.Column(db.String(MAX_REPLY_LEN), nullable=False)
    reply_message_my:str = db.Column(db.String(MAX_REPLY_LEN), nullable=False)
    training_data:TrainingData = db.relationship('TrainingData', backref='intent', cascade='all,delete')
    response:Response = db.relationship('Response', backref='intent', cascade='all,delete')
    small_talk:bool = db.Column(db.Boolean, default=False)
    deployed:bool = db.Column(db.Boolean, default=True)
    system:bool = db.Column(db.Boolean, default=False)
    children:str = db.Column(db.JSON)

@dataclass
class Setting(db.Model):
    id:int = db.Column(db.Integer, primary_key=True)
    primary_lang:str = db.Column(db.String(MAX_LANG_CODE_LEN))
    selected_lang:str = db.Column(db.JSON, nullable=False)
