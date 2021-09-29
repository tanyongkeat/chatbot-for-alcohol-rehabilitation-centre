from config import host, port, database, user, pw
import psycopg2
import pandas as pd
import json
import werkzeug
from app.models import Intent, TrainingData
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


def create_training_data(user_message, intent_id):
    if not user_message:
        flash(FIELD_EMPTY_MESSAGE)
        return None

    intent = Intent.query.get(intent_id)
    if not intent:
        flash('Cannot find intent')
        return None
    
    same_sample = TrainingData.query.filter(func.lower(TrainingData.user_message) == func.lower(user_message)).first()
    if same_sample:
        flash('Sample <em>' + user_message + '</em> exists in <em>' + same_sample.intent.intent_name + '</em>')
        return None
    return TrainingData(user_message=user_message, intent_id=intent_id, encoding=json.dumps(model.encode(user_message).tolist()))


def create_intent(intent_name, reply_message_en, reply_message_my):
    same_sample = Intent.query.filter(func.lower(Intent.intent_name) == func.lower(intent_name)).first()
    if same_sample:
        flash('The intent name already exists')
        return None
    return Intent(intent_name=intent_name, reply_message_en=reply_message_en, reply_message_my=reply_message_my)

def strip_tags(string):
    return flask.Markup(string).striptags()

def sanitize(string):
    return flask.escape(string)