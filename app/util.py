from config import host, port, database, user, pw
import psycopg2
import pandas as pd
import json
import werkzeug
from app.models import Intent, TrainingData, Response, db, MAX_USER_INPUT_LEN, MAX_REPLY_LEN, MAX_EMAIL_LEN, MAX_INTENT_NAME_LEN
from app.intent import model
from sqlalchemy import func
import flask
from flask import flash
from functools import cmp_to_key


FIELD_EMPTY_MESSAGE = 'This field cannot be left empty'



#################
###           ###
###   UTILS   ###
###           ###
#################

def strip_tags(string):
    return flask.Markup(string).striptags()

def sanitize(string):
    return flask.escape(string)

def compare_response(item1, item2):
    primary_lang = get_primary_lang()
    if item1.lang == primary_lang:
        return -1
    if item2.lang == primary_lang:
        return 1
    
    if item1.lang < item2.lang:
        return -1
    elif item1.lang > item2.lang:
        return 1
    else:
        return 0


####################
###              ###
###   DB_UTILS   ###
###              ###
####################

def query_db(sql):
    conn = psycopg2.connect("host='{}' port={} dbname='{}' user={} password={}".format(host, port, database, user, pw))
    data = pd.read_sql_query(sql, conn)
    conn.close()
    return data


def get_primary_lang():
    return 'en'

def get_selected_lang():
    return ['en', 'ms', 'zh-cn', 'ta']

from googletrans import Translator
translator = Translator()

def get_langs():
    return ['zh-cn', 'ms', 'ta', 'en']

def translate(text, dest):
    return translator.translate(text, dest=dest).text
    
def detect_lang(text):
    return translator.detect(text).lang

lens = {
    'selection': MAX_USER_INPUT_LEN, 
    'text': MAX_REPLY_LEN
}


def create_intent(intent_name, reply_message_en, reply_message_my):
    if not intent_name:
        raise EmptyRequiredField('The intent name')
    intent_name = intent_name[:MAX_INTENT_NAME_LEN]
    
    # if not reply_message_en or not reply_message_my:
    #     raise EmptyRequiredField('The reply messages')
    # reply_message_en = reply_message_en[:MAX_REPLY_LEN]
    # reply_message_my = reply_message_my[:MAX_REPLY_LEN]

    same_sample = Intent.query.filter(func.lower(Intent.intent_name) == func.lower(intent_name)).first()
    if same_sample:
        raise CustomError('The intent name already exists')

    intent = Intent(intent_name=intent_name, reply_message_en=reply_message_en, reply_message_my=reply_message_my)
    db.session.add(intent)
    db.session.commit()
    return intent

def create_training_data(user_message, intent_id):
    if not user_message:
        raise EmptyRequiredField('The training sample field')
    user_message = user_message[:MAX_USER_INPUT_LEN]

    intent = Intent.query.get(intent_id)
    if not intent:
        raise CustomError('Cannot find intent')
    
    same_sample = TrainingData.query.filter(func.lower(TrainingData.user_message) == func.lower(user_message)).first()
    if same_sample:
        raise CustomError('Sample <em>' + user_message + '</em> exists in <em>' + same_sample.intent.intent_name + '</em>')
    
    training_data = TrainingData(user_message=user_message, intent_id=intent_id, encoding=json.dumps(model.encode(user_message).tolist()))
    db.session.add(training_data)
    db.session.commit()
    return training_data

def update_training_data(training_data_id, user_message):
    old_training_data = TrainingData.query.get(training_data_id)
    if not old_training_data:
        raise CustomError('Cannot find the training sample')

    if old_training_data.user_message == user_message:
        return old_training_data
    
    new_training_data = create_training_data(user_message, old_training_data.intent_id)
    db.session.delete(old_training_data)
    db.session.add(new_training_data)
    db.session.commit()
    return new_training_data

def create_response(intent_id, text, selection):
    primary_lang = get_primary_lang()

    if Response.query.filter_by(intent_id=intent_id).first():
        raise CustomError('Responses for the intent already exists')
    
    intent = Intent.query.get(intent_id)
    if not intent:
        raise CustomError('The intent doesn\'t exist', 404)

    if not text or not selection:
        raise EmptyRequiredField('The reply messages')

    selection = ' '.join(intent.intent_name.split('_'))
    print(text, selection)
    for lang in get_langs():
        if lang == primary_lang or lang not in get_selected_lang():
            translated_text = text
            translated_selection = selection
        else:
            try:
                translated_text = translate(text, dest=lang)[:MAX_REPLY_LEN]
                translated_selection = translate(selection, dest=lang)[:MAX_USER_INPUT_LEN]
            except:
                db.session.rollback()
                raise CustomError('Google API error')
        
        print(translated_text, translated_selection)
        
        db.session.add(Response(intent_id=intent_id, lang=lang, 
                                text=translated_text, selection=translated_selection))
        
    db.session.commit()

def update_response(intent_id, field, lang, value):
    if not value:
        raise EmptyRequiredField('The reply messages')

    primary_lang = get_primary_lang()

    response = Response.query.filter_by(intent_id=intent_id, lang=lang).first()
    if not response:
        raise CustomError('The response cannot be found')
    
    if getattr(response, field) == value:
        return
#     if not responses
    setattr(response, field, value[:lens[field]])
    
    if lang == primary_lang:
        other_lang_responses = Response.query.filter(Response.intent_id==intent_id, Response.lang!=lang).all()
        for other_lang_response in other_lang_responses:
            try:
                translated_value = translate(value, dest=other_lang_response.lang)[:lens[field]]
            except:
                db.session.rollback()
                raise CustomError('Google API error')
            setattr(other_lang_response, field, translated_value)
    
    db.session.commit()

def refresh_response(intent_id, field):
    primary_lang = get_primary_lang()

    primary_response = Response.query.filter_by(intent_id=intent_id, lang=primary_lang).first()
    
    other_lang_responses = Response.query.filter(Response.intent_id==intent_id, Response.lang!=primary_lang).all()
    for other_lang_response in other_lang_responses:
        translated_value = translate(getattr(primary_response, field), dest=other_lang_response.lang)[:lens[field]]
        setattr(other_lang_response, field, translated_value)


######################
###                ###
###   EXCEPTIONS   ###
###                ###
######################

class CustomError(werkzeug.exceptions.HTTPException):
    def __init__(self, description='Something is not right', code=400):
        super().__init__()
        self.description = description
        self.code = code

class EmptyRequiredField(CustomError):
    def __init__(self, field='This field', code=400):
        super().__init__(field+' cannot be left empty', code)