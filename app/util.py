from config import host, port, database, user, pw
import psycopg2
import pandas as pd
import json
import werkzeug
from app.models import Intent, TrainingData, db, MAX_USER_INPUT_LEN, MAX_REPLY_LEN, MAX_EMAIL_LEN, MAX_INTENT_NAME_LEN
from app.intent import model
from sqlalchemy import func
import flask
from flask import flash


FIELD_EMPTY_MESSAGE = 'This field cannot be left empty'


class CustomError(werkzeug.exceptions.HTTPException):
    def __init__(self, description='Something is not right', code=400):
        super().__init__()
        self.description = description
        self.code = code

class EmptyRequiredField(CustomError):
    def __init__(self, field='This field', code=400):
        super().__init__(field+' cannot be left empty', code)



def query_db(sql):
    conn = psycopg2.connect("host='{}' port={} dbname='{}' user={} password={}".format(host, port, database, user, pw))
    data = pd.read_sql_query(sql, conn)
    conn.close()
    return data


def create_intent(intent_name, reply_message_en, reply_message_my):
    if not intent_name:
        raise EmptyRequiredField('The intent name')
    intent_name = intent_name[:MAX_INTENT_NAME_LEN]
    
    if not reply_message_en or not reply_message_my:
        raise EmptyRequiredField('The reply messages')
    reply_message_en = reply_message_en[:MAX_REPLY_LEN]
    reply_message_my = reply_message_my[:MAX_REPLY_LEN]

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

def strip_tags(string):
    return flask.Markup(string).striptags()

def sanitize(string):
    return flask.escape(string)