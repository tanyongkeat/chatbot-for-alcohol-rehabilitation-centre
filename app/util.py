from config import host, port, database, user, pw
import psycopg2
import pandas as pd
import json
import werkzeug
from app.models import Intent, TrainingData, Response, Setting, db, MAX_USER_INPUT_LEN, MAX_REPLY_LEN, MAX_EMAIL_LEN, MAX_INTENT_NAME_LEN
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

# primary_lang = 'en'
# selected_lang = ['en', 'ms', 'zh-cn', 'ta']
OUTDATED_FLAG = '7423SFTT-=TJYK=-5269FTSN=='

def get_primary_lang():
    return Setting.query.get(1).primary_lang

def update_primary_lang(new_primary_lang):
    if not new_primary_lang:
        raise CustomError('The primary language field cannot be left blank')

    if new_primary_lang not in get_langs():
        raise CustomError('The language specified is not supported')

    old_primary_lang = get_primary_lang()
    selected_lang_temp = [item for item in get_selected_lang()] # don't change it here

    # global primary_lang
    # primary_lang = new_primary_lang
    Setting.query.get(1).primary_lang = new_primary_lang

    if new_primary_lang not in selected_lang_temp:
        print('it is not here')
        selected_lang_temp.append(new_primary_lang)
        update_selected_lang(selected_lang_temp, old_primary_lang)
    
    db.session.commit()

def get_selected_lang():
    return json.loads(Setting.query.get(1).selected_lang)

def update_selected_lang(new_selected_lang, old_primary_lang):
    old_selected_lang = get_selected_lang()
    if set(old_selected_lang) == set(new_selected_lang):
        print('we got the same thing')
        return

    if not new_selected_lang:
        raise CustomError('At least one language must be selected')

    langs = get_langs()
    for nsl in new_selected_lang:
        if nsl not in langs:
            raise CustomError('The language specified is not supported')

    added_selected_lang = list(set(new_selected_lang) - set(old_selected_lang))

    if added_selected_lang:
        print('translating for ', added_selected_lang)
        responses = Response.query.distinct(Response.intent_id).all()
        for response in responses:
            refresh_response(response.intent_id, ['text', 'selection'], old_primary_lang, dest_lang=added_selected_lang)

    # global selected_lang
    # selected_lang = new_selected_lang
    # print(get_selected_lang())
    primary_lang = get_primary_lang()
    if primary_lang not in new_selected_lang:
        new_selected_lang.append(primary_lang)
    Setting.query.get(1).selected_lang = json.dumps(new_selected_lang)
    db.session.commit()


from googletrans import Translator
translator = Translator()

def get_langs():
    return ['en', 'ms', 'ta', 'zh-cn']

def translate(text, dest):
    print('translating:--:', text)
    return translator.translate(text, dest=dest).text
    
def detect_lang(text):
    lang = translator.detect(text).lang.lower()
    print('detected -', lang, '-')
    if lang not in lang_mapping or lang_mapping[lang] not in get_selected_lang():
        return get_primary_lang()
    return lang_mapping[lang]

lens = {
    'selection': MAX_USER_INPUT_LEN, 
    'text': MAX_REPLY_LEN
}

lang_mapping = {
    'zh-cn': 'zh-cn', 
    'zh-tw': 'zh-cn', 
    'ms': 'ms', 
    'id': 'ms', 
    'en': 'en', 
    'ta': 'ta'
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

    intent = Intent(intent_name=intent_name, reply_message_en=reply_message_en, reply_message_my=reply_message_my, children=json.dumps([]))
    db.session.add(intent)
    db.session.commit()
    return intent

def get_ordered_intent():
    intents = Intent.query.with_entities(Intent.id, Intent.intent_name, Intent.system).distinct().all()
    return sorted(intents, key=lambda x: (-int(x[2]), x[1]))

def create_training_data(user_message, intent_id):
    if not user_message:
        raise EmptyRequiredField('The training sample field')
    user_message = user_message[:MAX_USER_INPUT_LEN]

    intent = Intent.query.get(intent_id)
    if not intent:
        raise CustomError('Cannot find intent')
    if intent.system:
        raise CustomError('Operation not allowed')
    
    same_sample = TrainingData.query.filter(func.lower(TrainingData.user_message) == func.lower(user_message)).all()
    for ss in same_sample:
        if ss.intent_id != intent_id:
            raise CustomError('Sample <em>' + user_message + '</em> exists in <em>' + ss.intent.intent_name + '</em>')
    
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

def model_encode(text):
    print('encoding', text)
    return json.dumps(model.encode(text).tolist())

def encode_response_selection(response, outdated=False):
    if not outdated:
        response.selection_encoding = model_encode(response.selection)
    else:
        response.selection_encoding = OUTDATED_FLAG

def create_response(intent_id, text, selection):
    primary_lang = get_primary_lang()
    selected_lang = get_selected_lang()

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
        if lang == primary_lang:
            translated_text = text
            translated_selection = selection
            translated_selection_encoding = model_encode(translated_selection)
        elif lang not in selected_lang:
            translated_text = OUTDATED_FLAG
            translated_selection = OUTDATED_FLAG
            translated_selection_encoding = OUTDATED_FLAG
        else:
            try:
                translated_text = translate(text, dest=lang)[:MAX_REPLY_LEN]
                translated_selection = translate(selection, dest=lang)[:MAX_USER_INPUT_LEN]
                translated_selection_encoding = model_encode(translated_selection)
            except:
                db.session.rollback()
                raise CustomError('Google API error')
        
        print(translated_text, translated_selection)
        
        db.session.add(Response(intent_id=intent_id, lang=lang, 
                                text=translated_text, selection=translated_selection, selection_encoding=translated_selection_encoding))
        
    db.session.commit()

def update_response(intent_id, field, lang, value):
    if not value:
        raise EmptyRequiredField('The reply messages')

    primary_lang = get_primary_lang()
    selected_lang = get_selected_lang()

    response = Response.query.filter_by(intent_id=intent_id, lang=lang).first()
    if not response:
        raise CustomError('The response cannot be found')
    
    if getattr(response, field) == value:
        return
#     if not responses
    setattr(response, field, value[:lens[field]])
    if field == 'selection':
        encode_response_selection(response)
    
    if lang == primary_lang:
        other_lang_responses = Response.query.filter(Response.intent_id==intent_id, Response.lang!=lang).all()
        for other_lang_response in other_lang_responses:
            if not other_lang_response.lang in selected_lang:
                setattr(other_lang_response, field, OUTDATED_FLAG)
                if field == 'selection':
                    encode_response_selection(other_lang_response, outdated=True)
                print('skipping', other_lang_response.lang)
                continue
            
            try:
                translated_value = translate(value, dest=other_lang_response.lang)[:lens[field]]
            except:
                db.session.rollback()
                raise CustomError('Google API error')
            setattr(other_lang_response, field, translated_value)
            if field == 'selection':
                encode_response_selection(other_lang_response)
    
    db.session.commit()

def refresh_response(intent_id, fields, src_lang, dest_lang=None):
    # primary_lang = get_primary_lang()

    primary_response = Response.query.filter_by(intent_id=intent_id, lang=src_lang).first()
    
    if not dest_lang:
        filter_con = Response.lang!=src_lang
    else:
        filter_con = Response.lang.in_(dest_lang)
    
    other_lang_responses = Response.query.filter(Response.intent_id==intent_id, filter_con).all()
    for other_lang_response in other_lang_responses:
        for field in fields:
            if getattr(other_lang_response, field) != OUTDATED_FLAG:
                print(other_lang_response.intent.intent_name)
                print(other_lang_response.lang, getattr(other_lang_response, field), 'is not outdated')
                continue
            print(other_lang_response.lang, 'is outdated')
            try:
                translated_value = translate(getattr(primary_response, field), dest=other_lang_response.lang)[:lens[field]]
                # setattr(other_lang_response, field, translated_value)
                # if field == 'selection':
                #     encode_response_selection(other_lang_response)
            except:
                db.session.rollback()
                raise CustomError('Google API error')
            setattr(other_lang_response, field, translated_value)
            if field == 'selection':
                encode_response_selection(other_lang_response)


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