from app import host, port, database, user, pw
import psycopg2
import pandas as pd
from app.models import Intent, TrainingData
from sqlalchemy import func
from flask import flash


def query_db(sql):
    conn = psycopg2.connect("host='{}' port={} dbname='{}' user={} password={}".format(host, port, database, user, pw))
    data = pd.read_sql_query(sql, conn)
    conn.close()
    return data


def create_training_data(user_message, intent_name):
    intent_id = Intent.query.filter_by(intent_name=intent_name).first().id
    if not intent_id:
        flash('Cannot find intent')
        return None
    same_sample = TrainingData.query.filter(func.lower(TrainingData.user_message) == func.lower(user_message)).first()
    if same_sample:
        flash('Sample exists in '+same_sample.intent.intent_name)
        return None
    return TrainingData(user_message=user_message, intent_id=intent_id)


def create_intent(intent_name, reply_message_en, reply_message_my):
    same_sample = Intent.query.filter(func.lower(Intent.intent_name) == func.lower(intent_name)).first()
    if same_sample:
        flash('The intent name already exists')
        return None
    return Intent(intent_name=intent_name, reply_message_en=reply_message_en, reply_message_my=reply_message_my)
