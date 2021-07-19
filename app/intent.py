import numpy as np
import pandas as pd
import scipy
from app import db
from app.util import query_db
from app.models import TrainingData, Intent
from sklearn.metrics.pairwise import cosine_similarity
# import matplotlib.pyplot as plt
# import seaborn as sns

from tqdm.auto import tqdm
tqdm.pandas()


model_on = False
target_language = 'en'


def read_data():
    # dataset = query_db('select user_message, intent_id from training_data')
    dataset = pd.read_sql_query(
        sql = TrainingData.query.with_entities(
            TrainingData.user_message, 
            TrainingData.intent_id
        ).statement, 
        con = db.session.bind
    )
    # reply = query_db('select id, reply_message, small_talk, intent_name as intention from intent')
    reply = pd.read_sql_query(
        sql = Intent.query.with_entities(
            Intent.id, 
            Intent.reply_message_en, 
            Intent.reply_message_my, 
            Intent.small_talk, 
            Intent.intent_name.label('intention')
        ).statement, 
        con = db.session.bind
    )
    dataset = dataset.merge(reply, how='left', left_on='intent_id', right_on='id')
    if model_on:
        dataset = pd.concat([dataset, pd.DataFrame(model.encode(dataset.user_message))], axis=1)
    return dataset


def refresh_dataset():
    global dataset
    dataset = read_data()
    print('done')


if model_on:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('paraphrase-xlm-r-multilingual-v1')
    dataset = read_data()


def detect_intention2(user_input, target_language):
    def sort_intent(df):
        return df.sort_values('cos_sim', ascending=False).iloc[0]

    embedding = model.encode([user_input])
    cos_sim = cosine_similarity(embedding, dataset[range(768)].values)[0]

    df_temp = dataset[['user_message', 'intention', 'reply_message_'+target_language, 'small_talk', 'intent_id']]
    df_temp.rename({'reply_message_'+target_language: 'reply_message'}, axis=1, inplace=True)
    df_temp['cos_sim'] = cos_sim

    df_temp = df_temp.groupby('intent_id').apply(sort_intent)

    df_temp = df_temp.sort_values('cos_sim', ascending=False)

    return_col = ['reply_message', 'cos_sim', 'intention', 'intent_id']

    if df_temp.iloc[:3].small_talk.mean() > 0.5:
        return [df_temp.iloc[0][return_col].tolist()]

    df_temp = df_temp[~df_temp.small_talk]
    highest_confidence = scipy.special.softmax(df_temp.cos_sim*10).max()
    print(user_input, highest_confidence)
    if highest_confidence < 0.6:
        return df_temp.iloc[:3][return_col].values.tolist()
    else:
        return [df_temp.iloc[0][return_col].tolist()]


def detect_intention(user_input):
    if not model_on:
        pre = [('reply_message_1', 0, 'nearest_message_1', 1), 
            ('reply_message_2', 1, 'nearest_message_2', 1), 
            ('reply_message_3', 2, 'nearest_message_3', 1)]
        if len(user_input) == 1:
            pre = [pre[0]]
    else:
        pre = detect_intention2(user_input, target_language)
    pre = [{'reply': p[0], 'cosine_similarity': float(p[1]), 'nearest_message': p[2].replace('_', ' '), 'intent_id': int(p[3])} for p in pre]

    return pre
