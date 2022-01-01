import numpy as np
import pandas as pd
import scipy
from app import db
from flask import session
# from app.util import query_db
from app.models import TrainingData, Intent, Response
from sklearn.metrics.pairwise import cosine_similarity
import json
# import matplotlib.pyplot as plt
# import seaborn as sns

from tqdm.auto import tqdm
tqdm.pandas()


model_on = True
target_language = 'en'

if model_on:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('paraphrase-xlm-r-multilingual-v1')
    # dataset = read_data()

from app.util import translate, detect_lang, get_primary_lang, get_langs, get_selected_lang, OUTDATED_FLAG

###########################################################################################################
# from malaya import deep_model
# lol = deep_model(quantized=True)
# print(lol.predict_proba(['moshi moshi', 'seleamat pagi', 'good morning']))
###########################################################################################################

def read_data(target_language, is_selection):
    # dataset = query_db('select user_message, intent_id from training_data')
    dataset = pd.read_sql_query(
        sql = TrainingData.query.with_entities(
            TrainingData.user_message, 
            TrainingData.intent_id, 
            TrainingData.encoding
        ).statement, 
        con = db.session.bind
    )
    
    primary_lang = get_primary_lang()
    filter_con = Response.lang.in_([primary_lang, target_language])
    if is_selection:
        filter_con = Response.lang.in_(get_selected_lang())
    dataset2 = pd.read_sql_query(
        sql = Response.query.with_entities(
            Response.selection.label('user_message'), 
            Response.intent_id, 
            Response.selection_encoding.label('encoding')
        ).filter(filter_con).statement, 
        con = db.session.bind
    )

    dataset = dataset.append(dataset2)
    dataset.reset_index(inplace=True, drop=True)
    # reply = query_db('select id, reply_message, small_talk, intent_name as intention from intent')
    filter_con = ((Intent.deployed==True) | (Intent.id.in_(session['last_selections']))) & (Intent.system==False)
    if is_selection:
        print('including all intents except systems')
        filter_con = Intent.system==False
    reply = pd.read_sql_query(
        sql = Intent.query.with_entities(
            Intent.id, 
            # Intent.reply_message_en, 
            # Intent.reply_message_my, 
            Intent.small_talk, 
            Intent.deployed, 
            Intent.intent_name.label('intention')
        ).filter(filter_con).statement, 
        con = db.session.bind
    )
    dataset = reply.merge(dataset, how='inner', left_on='id', right_on='intent_id')
    # dataset = dataset[dataset.deployed]
    
    print(dataset.encoding)
    loaded_encoding = dataset.encoding.apply(lambda x: json.loads(x)).tolist()
    dataset = pd.concat([dataset, pd.DataFrame(loaded_encoding)], axis=1)
    return dataset


# def refresh_dataset():
#     global dataset
#     dataset = read_data()
#     print('done')


def detect_intention2(user_input, target_language, is_selection):
    dataset = read_data(target_language=target_language, is_selection=is_selection)

    def sort_intent(df):
        return df.sort_values('cos_sim', ascending=False).iloc[0]

    embedding = model.encode([user_input])
    cos_sim = cosine_similarity(embedding, dataset[range(768)].values)[0]
    dataset['lang'] = target_language

    df_temp = dataset[['user_message', 'intention', 'small_talk', 'intent_id', 'lang']]
    # df_temp.rename({'reply_message_'+target_language: 'reply_message'}, axis=1, inplace=True)
    response = pd.read_sql_query(
        sql = Response.query.with_entities(
            Response.intent_id, 
            Response.text.label('reply_message'), 
            Response.selection
        ).filter_by(lang=target_language).statement, 
        con = db.session.bind
    )
    df_temp = df_temp.merge(response, how='inner', on='intent_id')

    df_temp['cos_sim'] = cos_sim

    df_temp = df_temp.groupby('intent_id').apply(sort_intent)

    df_temp = df_temp.sort_values('cos_sim', ascending=False)

    return_col = ['reply_message', 'cos_sim', 'selection', 'intent_id']

    if df_temp.iloc[:3].small_talk.mean() > 0.5:
        return [df_temp.iloc[0][return_col].tolist()]

    df_temp = df_temp[~df_temp.small_talk]
    highest_confidence = scipy.special.softmax(df_temp.cos_sim*10).max()
    print(user_input, highest_confidence)
    if highest_confidence < 0.6:
        return df_temp.iloc[:3][return_col].values.tolist()
    else:
        return [df_temp.iloc[0][return_col].tolist()]


def detect_intention(user_input, is_selection):
    if not model_on:
        pre = [('reply_message_1', 0, 'nearest_message_1', 1), 
            ('reply_message_2', 1, 'nearest_message_2', 1), 
            ('reply_message_3', 2, 'nearest_message_3', 1)]
        if len(user_input) == 1:
            pre = [pre[0]]
        target_language = 'en'
    else:
        target_language = detect_lang(user_input)
        pre = detect_intention2(user_input, target_language=target_language, is_selection=is_selection)
    pre = [{'reply': p[0], 'cosine_similarity': float(p[1]), 'nearest_message': p[2].replace('_', ' '), 'intent_id': int(p[3])} for p in pre]

    return pre, target_language
