from app.models import db, HistoryFull, ChatHistory, TrainingData, Intent
import pandas as pd
import numpy as np
import json
from datetime import datetime
import datetime as dt

import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

margin = dict(t=3, r=3, b=3, l=3, pad=0)

def percentage_thumbsdown_by_week():
    sql_1 = HistoryFull.query\
    .with_entities(
        db.func.date_trunc('week', HistoryFull.timestamp).label('week'), 
        db.func.count(HistoryFull.id).label('total_messages'), 
        db.func.sum(db.cast(HistoryFull.negative, db.Integer)).label('total_thumbsdown')
    )\
    .group_by(db.text('1'))\
    .order_by(db.text('1'))

    df_1 = pd.read_sql_query(
        sql = sql_1.statement, 
        con = db.session.bind
    )

    df_1['thumbsdown_rate'] = df_1.total_thumbsdown/df_1.total_messages
    df_1 = df_1.set_index('week').reindex(pd.date_range(df_1.week.min(), df_1.week.max(), freq='W-MON')).fillna(0)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_1.index, y=df_1.total_thumbsdown, fill='tozeroy', 
            marker=dict(color=px.colors.qualitative.Plotly[1]), 
            name='Responses with thumbsdown', 
            hoverlabel = dict(namelength = -1), 
            hovertemplate = '%{y} %{text}', 
            text = [f'({r*100:.2f}%)' for r in df_1.thumbsdown_rate]
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_1.index, y=df_1.total_messages, fill='tonexty', 
            marker=dict(color=px.colors.qualitative.Plotly[0]), 
            name='Total responses', hoverlabel = dict(namelength = -1)
        )
    )

    fig.update_layout(
        xaxis_title='Week', 
        xaxis_showgrid=False, 
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', 
        hovermode='x unified', 
        hoverlabel=dict(
            bgcolor="white"
        ), 
        legend=dict(
            orientation='h', 
            yanchor="bottom",
            y=1,
            xanchor="left", 
            x=0.05
        ), 
        margin=margin
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def percentage_thumbsdown_by_intent():
    aggregate = HistoryFull.query\
    .with_entities(
        HistoryFull.predicted_intent_id_top, 
        db.func.count(HistoryFull.id).label('n_messages'), 
        db.func.avg(db.cast(HistoryFull.negative, db.Integer)).label('thumbsdown_rate')
    )\
    .group_by(db.text('1'))\
    .subquery()

    sql_2 = Intent.query\
    .with_entities(
        Intent.intent_name, 
        Intent.id, 
        aggregate.c.n_messages, 
        aggregate.c.thumbsdown_rate
    )\
    .join(aggregate, Intent.id==aggregate.c.predicted_intent_id_top)\
    .order_by(aggregate.c.thumbsdown_rate)

    df_2 = pd.read_sql_query(
        sql = sql_2.statement, 
        con = db.session.bind
    )

    df_2['thumbsdown_rate'] = df_2.thumbsdown_rate * 100
    df_2['thumbsdown_rate_string'] = df_2.thumbsdown_rate.apply(lambda x: f'{x:.2f}')

    fig = px.bar(df_2, x="thumbsdown_rate", y="intent_name", orientation='h', custom_data=['n_messages', 'thumbsdown_rate_string'])

    fig.update_layout(
        xaxis=dict(side="top"), 
        xaxis_title='Thumbsdown rate (%)', 
        xaxis_title_font_size=12, 
        yaxis_title='', 
        yaxis_matches=None, 
        yaxis_tickfont_size=11, 
        # yaxis_title_standoff=0, 
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', 
        hovermode='y', 
    #     hoverlabel=dict(
    #         bgcolor="white"
    #     ), 
        legend=dict(
            orientation='h', 
            yanchor="top",
            y=0.99,
            xanchor="left", 
            x=0.5
        ), 
        margin=margin
    )

    fig.update_traces(
        hovertemplate="%{customdata[1]}% of total %{customdata[0]} reponse(s)"
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def popular_questions():
    current_time = datetime.utcnow()
    starting_point = (current_time - dt.timedelta(days=7)).date()

    aggregate = HistoryFull.query\
    .with_entities(
        HistoryFull.predicted_intent_id_top, 
        db.func.count(HistoryFull.id).label('n_messages')
    )\
    .filter(HistoryFull.timestamp >= starting_point)\
    .group_by(db.text('1'))\
    .subquery()

    sql_3 = Intent.query\
    .with_entities(
        Intent.intent_name, 
        Intent.id, 
        aggregate.c.n_messages
    )\
    .join(aggregate, Intent.id==aggregate.c.predicted_intent_id_top)

    df_3 = pd.read_sql_query(
        sql = sql_3.statement, 
        con = db.session.bind
    )

    fig = px.pie(df_3, values='n_messages', names='intent_name', title='Popular Intents')

    fig = go.Figure(
        data=[
            go.Pie(
                labels=df_3.intent_name, values=df_3.n_messages, textinfo='percent',
                insidetextorientation='radial'
            )
        ]
    )

    fig.update_traces(
        hole=.5, 
        hoverinfo='label+value'
    )

    fig.update_layout(
        # title_text="Popular quetions (past 7 days)", 
        # title_x=0.5, 
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', 
        annotations=[dict(text=f'{df_3.n_messages.sum()}<br>messages', x=0.5, y=0.5, font_size=20, showarrow=False)], 
        margin=margin
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def number_of_users():
    sql_3 = HistoryFull.query\
    .with_entities(
        ChatHistory.user_email, 
        HistoryFull.chat_id, 
        db.func.min(HistoryFull.timestamp).label('chat_first_message_time')
    )\
    .join(HistoryFull)\
    .group_by(db.text('1'), db.text('2'))

    first_chat_message = pd.read_sql_query(
        sql = sql_3.statement, 
        con = db.session.bind
    )

    first_chat_message.sort_values('user_email')

    second = first_chat_message.merge(
        first_chat_message.groupby('user_email').chat_first_message_time.min().reset_index()\
            .rename({'chat_first_message_time': 'user_first_message_time'}, axis=1), 
        left_on='user_email', right_on='user_email')

    second['first_chat'] = second['chat_first_message_time'] == second['user_first_message_time']

    second['chat_first_message_week'] = (second['chat_first_message_time'] - pd.to_timedelta(second['chat_first_message_time'].dt.dayofweek, 'D')).dt.date

    second = second.groupby('chat_first_message_week').agg({'chat_id': 'count', 'first_chat': 'mean'})

    weeks = pd.date_range(second.index.min(), second.index.max(), freq='W-MON')
    second = second.reindex(weeks).fillna(0)

    color_0 = px.colors.qualitative.Plotly[0]
    color_1 = px.colors.qualitative.Plotly[6]

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Bar(x=second.index, y=second.chat_id, name="Total users", hoverlabel = dict(namelength = -1), marker_color=color_0),
        secondary_y=False, 
    )

    fig.add_trace(
        go.Scatter(x=second.index, y=second.first_chat, name="Percentage of new users (%)", hoverlabel = dict(namelength = -1), marker_color=color_1),
        secondary_y=True, 
    )

    # Add figure title
    fig.update_layout(
        # title=dict(
        #     text='<b>Number of users</b>', 
        #     x=0.5
        # ), 
        xaxis_title='Week', 
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', 
        hovermode='x unified', 
        hoverlabel=dict(
            bgcolor="white"
        ), 
        legend=dict(
            orientation='h', 
            yanchor="bottom",
            y=1.1,
            xanchor="center", 
            x=0.5
        ), 
        margin=margin
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="Total users", titlefont_color=color_0, tickfont_color=color_0, showgrid=False, secondary_y=False)
    fig.update_yaxes(title_text="Percentage of new users(%)", titlefont_color=color_1, 
                    tickformat='.2%', tickfont_color=color_1, showgrid=False, secondary_y=True)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON