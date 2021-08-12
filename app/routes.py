from dataclasses import dataclass
import flask
from flask import render_template, render_template_string, jsonify, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db, login_manager
from app.intent import detect_intention
from app.models import HistoryFull, Intent, TrainingData, ChatHistory, Admin
from app.forms import LoginForm
from app.util import create_training_data, create_intent
from sqlalchemy import func
import json
import re



FIELD_EMPTY_MESSAGE = 'please kindly fill in all the needed field'
no_information_required = False


@app.route('/')
def index():
    print('yoyoyoyoyo')
    registered = False

    if no_information_required or 'chat_id' in session:
        registered = True

    return render_template('user.html', registered=registered)

@app.route('/reply', methods=['POST'])
def reply():
    if not 'chat_id' in session:
        if no_information_required:
            session['chat_id'] = 1
        else:
            flask.abort(406) # importatnt
    ut = request.form['utterence']
    prediction = detect_intention(ut)
    predicted_intent_ids = [pre['intent_id'] for pre in prediction]
    obj = HistoryFull(
        chat_id=session['chat_id'], 
        utterance_original=ut, 
        utterance=ut, 
        predicted_intent_id_top=int(predicted_intent_ids[0]), 
        predicted_intent_id=','.join([str(id) for id in predicted_intent_ids])
    )
    db.session.add(obj)
    db.session.commit()
    return jsonify({'id': obj.id, 'prediction': prediction})

@app.route('/capture', methods=['POST'])
def capture():
    message_id = request.form['message_id']
    feedback = request.form['feedback']
    history_full_instance = HistoryFull.query.get(message_id)
    setattr(history_full_instance, feedback, True)
    db.session.commit()
    return jsonify({})

@app.route('/user_information', methods=['POST'])
def user_information():
    if not 'chat_id' in session:
        user_name = request.form['user_name'][:150]
        user_email = request.form['user_email'][:320]
        email_pattern = "^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
        error = {}

        if not user_name:
            error['user_name'] = 'Please fill in your name'

        if not user_email:
            error['user_email'] = 'Please fill in your email address'
        elif not re.match(email_pattern, user_email):
            error['user_email'] = 'Please enter a valid email address'

        if error:
            return jsonify({'code': 400, 'error': error})

        obj = ChatHistory(user_name=user_name, user_email=user_email)
        db.session.add(obj)
        db.session.commit()

        session['chat_id'] = obj.id
        session['user_name'] = user_name
        session['user_email'] = user_email

    return jsonify({'code': 200, 'user_name': user_name, 'user_email': user_email, 'chatbox': render_template('user_chatbox.html')})


######################
###                ###
###     LOG IN     ###
###                ###
######################
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('missed'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('missed')
        return redirect(next_page)
    return render_template('admin_login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

######################
###                ###
###     MISSED     ###
###                ###
######################

# GETTER
@app.route('/view_missed', methods=['POST'])
def view_missed():
    captureds = HistoryFull.query.filter_by(negative=True, trained=False).order_by(HistoryFull.id).all()
    with app.app_context():
        return jsonify({'data': captureds})

#GETTER
@app.route('/view_missed_intent', methods=['POST'])
def view_missed_intent():
    intents = Intent.query.distinct().all()
    # intents = sorted(intents, key=lambda x: x[1])
    with app.app_context():
        return jsonify({'data': intents})



@app.route('/missed', methods=['GET', 'POST'])
# @login_required
def missed():
    '''
    TODO
    1. when a sample exists as a training sample, the sample should be marked or removed 
    '''
    if request.method == 'POST':
        data = json.loads(request.data.decode())
        # target_id = request.form['id']
        target_id = data['id']
        # job = request.form['job']
        job = data['job']
        print(data)
        target = HistoryFull.query.get_or_404(target_id)
        if job == 'update':
            if not data['modified_content']:
                return jsonify({'code': 400})
            else:
                target.utterance = data['modified_content']
                db.session.commit()
                return jsonify({'code': 200})
        elif job == 'delete':
            target.negative = False
            db.session.commit()
            return jsonify({'code': 200})
        elif job == 'retrain':
            print(data)
            if (not data['intent']) or (data['intent']=='new intent'):
                # return error code
                return jsonify({'code': 400})
                # intents = Intent.query.with_entities(Intent.id, Intent.intent_name).distinct().all()
                # intents = sorted(intents, key=lambda x: x[1])
                # return render_template('intents_add.html', current_page='intents', intents=intents, preset_sample_id=target_id, preset_training_sample=target.utterance)
            intent_id = data['intent']
            new_training_data = create_training_data(target.utterance, Intent.query.get(intent_id).intent_name)
            if new_training_data:
                db.session.add(new_training_data)
                target.trained = True
                db.session.commit()
                # refresh_dataset()
                return jsonify({'code': 200})
            else:
                return jsonify({'code': 400})

    captureds = HistoryFull.query.filter_by(negative=True, trained=False).order_by(HistoryFull.id).all()
    intents = Intent.query.with_entities(Intent.id, Intent.intent_name).distinct().all()
    intents = sorted(intents, key=lambda x: x[1])
    return render_template('missed.html', current_page='missed', captureds=captureds, intents=intents)

@app.route('/missed_new_intent', methods=['POST'])
def missed_new_intent():
    target_id = request.form['id']
    target = HistoryFull.query.get_or_404(target_id)
    intents = Intent.query.with_entities(Intent.id, Intent.intent_name).distinct().all()
    intents = sorted(intents, key=lambda x: x[1])
    return render_template('intents_add.html', current_page='intents', intents=intents, preset_sample_id=target_id, preset_training_sample=target.utterance)



########################
###                  ###
###   INTENTS_EDIT   ###
###                  ###
########################

#GETTER
@app.route('/view_intents_edit', methods=['POST'])
def view_intents_edit():
    data = json.loads(request.data.decode())
    intent_name = data['intent_name']
    print(intent_name)
    training_data = Intent.query.filter_by(intent_name=intent_name).first().training_data
    with app.app_context():
        return jsonify({'data': training_data})

@app.route('/intents_edit')
def intents_base():
    intents = Intent.query.with_entities(Intent.id, Intent.intent_name).distinct().all()
    intents = sorted(intents, key=lambda x: x[1])
    return render_template('intents_base.html', current_page='intents', intents=intents)

@app.route('/intents_edit/<intent_name>', methods=['GET', 'POST'])
def intents(intent_name):
    '''
    TODO
    404 error for non-existance intents
    '''
    intent = Intent.query.filter_by(intent_name=intent_name).first()

    if request.method == 'POST':
        if request.data: # ajax
            data = json.loads(request.data.decode())
            job = data['job']
        else: # form submission
            job = request.form['job']

        if job == 'update_reply_message':
            lang = request.form['lang']
            if request.form['modified_content']:
                setattr(intent, 'reply_message_'+lang, request.form['modified_content'])
            else:
                flash(FIELD_EMPTY_MESSAGE)
        elif job == 'update':
            id = data['id']
            if data['modified_content']:
                temp = TrainingData.query.get(id)
                # TODO find if the modified content is present
                temp.user_message = data['modified_content']
                db.session.commit()
                return jsonify({'code': 200})
            else:
                # flash(FIELD_EMPTY_MESSAGE)
                return jsonify({'code': 400})
        elif job == 'delete':
            id = data['id']
            temp = TrainingData.query.get(id)
            db.session.delete(temp)
            db.session.commit()
            return jsonify({'code': 200})
        elif job == 'add_sample':
            training_data = create_training_data(request.form['user_message'], intent_name)
            if training_data:
                db.session.add(training_data)
        db.session.commit()
        # refresh_dataset()
    intents = Intent.query.with_entities(Intent.id, Intent.intent_name).distinct().all()
    intents = sorted(intents, key=lambda x: x[1])
    
    return render_template('intents_edit.html', current_page='intents', intents=intents, intent=intent)

@app.route('/intents_add', methods=['GET', 'POST'])
def intents_add():
    error = False
    if request.method == 'POST':
        training_datas_args = [key for key in request.form if 'training_sample' in key]
        training_datas = [request.form[key] for key in training_datas_args]
        # if 
        """
            behavior:
                - the form will be rejected if intent_name, reply_messages have issues
                - if only training samples have issues, the form will be accepted and the training samples are removed with messages flashed
        """
        intent_name = request.form['intent_name']
        reply_message_en = request.form['reply_message_en']
        reply_message_my = request.form['reply_message_my']
        intent = create_intent(intent_name=intent_name, reply_message_en=reply_message_en, reply_message_my=reply_message_my)
        if intent:
            db.session.add(intent)
            db.session.commit()
            # TODO ajax to signify that a training sample is used
            for training_data in training_datas:
                temp = create_training_data(training_data, intent_name)
                if temp:
                    db.session.add(temp)
            if 'preset_sample_id' in request.form:
                temp = HistoryFull.query.get_or_404(request.form['preset_sample_id'])
                temp.trained = True
            db.session.commit()
            # refresh_dataset()
            return redirect('intents_edit/'+intent_name)
        error = True

    intents = Intent.query.with_entities(Intent.id, Intent.intent_name).distinct().all()
    intents = sorted(intents, key=lambda x: x[1])

    if error:
        form_data = {
            'intent_name': intent_name, 
            'reply_message_en': reply_message_en, 
            'reply_message_my': reply_message_my
        }

        target_id = None
        target_utterance = None
        if 'preset_sample_id' in request.form:
            target_id = request.form['preset_sample_id']
            target = HistoryFull.query.get_or_404(target_id)
            target_utterance = target.utterance
            training_datas = [request.form[key] for key in training_datas_args if key != 'training_sample_0']
        
        return render_template('intents_add.html', current_page='intents', intents=intents, form_data=form_data, training_datas=training_datas, preset_sample_id=target_id, preset_training_sample=target_utterance)
    return render_template('intents_add.html', current_page='intents', intents=intents)

@app.route('/delete_intent', methods=['POST'])
def delete_intent():
    intent_id = request.form['intent_id']
    temp = Intent.query.get(intent_id)
    db.session.delete(temp)
    db.session.commit()
    # refresh_dataset()
    return redirect('/intents_edit')

@app.route('/testing', methods=['GET', 'POST'])
def testing():
    if request.method == 'POST':
        haha = request.form['title']
        return 'you just posted something mdfk ' + haha
    return render_template('testing.html')


# if __name__ == '__main__':
#     app.run(debug=True)
