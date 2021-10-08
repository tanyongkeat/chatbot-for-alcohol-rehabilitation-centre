from dataclasses import dataclass
import flask
from flask import render_template, render_template_string, jsonify, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required
import werkzeug
from werkzeug.urls import url_parse
from werkzeug.exceptions import BadRequest
from werkzeug.wrappers import Response

from app import app, db, login_manager
from app.intent import detect_intention
from app.models import HistoryFull, Intent, TrainingData, ChatHistory, Admin, Response,\
    MAX_USER_INPUT_LEN, MAX_REPLY_LEN, MAX_EMAIL_LEN, MAX_INTENT_NAME_LEN
from app.forms import LoginForm
from app.util import create_training_data, update_training_data, create_intent, get_ordered_intent,\
    FIELD_EMPTY_MESSAGE, EmptyRequiredField, CustomError, strip_tags, sanitize,\
    get_selected_lang, update_selected_lang, get_primary_lang, update_primary_lang, get_langs,\
    create_response, update_response, refresh_response, compare_response
from app.plot import percentage_thumbsdown_by_week, percentage_thumbsdown_by_intent, popular_questions, number_of_users
from sqlalchemy import func
from functools import cmp_to_key
import json
import re



no_information_required = False


@app.route('/')
def index():
    print('yoyoyoyoyo')
    registered = False

    if no_information_required or 'chat_id' in session:
        registered = True

    opening_text = Intent.query.filter_by(intent_name='opening text').first()
    opening_text = dict(map(lambda x: (x.lang, x.text), opening_text.response))

    apology_text = Intent.query.filter_by(intent_name='thumbsdown text').first()
    apology_text = dict(map(lambda x: (x.lang, x.text), apology_text.response))

    appreciation_text = Intent.query.filter_by(intent_name='thumbsup text').first()
    appreciation_text = dict(map(lambda x: (x.lang, x.text), appreciation_text.response))

    confirmation_text = Intent.query.filter_by(intent_name='confirmation text').first()
    confirmation_text = dict(map(lambda x: (x.lang, x.text), confirmation_text.response))

    contact_information_text = Intent.query.filter_by(intent_name='admin contact').first()
    contact_information_text = dict(map(lambda x: (x.lang, x.text), contact_information_text.response))

    error_message = Intent.query.filter_by(intent_name='error message').first()
    error_message = dict(map(lambda x: (x.lang, x.text), error_message.response))

    contact_admin = Intent.query.filter_by(intent_name='not in selection').first()
    contact_admin = dict(map(lambda x: (x.lang, x.text), contact_admin.response))

    return render_template('user.html', registered=registered, primary_lang=get_primary_lang(), opening_text=opening_text, 
                           apology_text=apology_text, appreciation_text=appreciation_text, confirmation_text=confirmation_text, 
                           contact_information_text=contact_information_text, error_message=error_message, contact_admin=contact_admin)

@app.route('/reply', methods=['POST'])
def reply():
    if not 'chat_id' in session:
        if no_information_required:
            session['chat_id'] = 1
        else:
            flask.abort(406) # important
    ut = sanitize(request.form['utterence'])[:MAX_USER_INPUT_LEN]
    prediction, lang = detect_intention(ut)
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
    return jsonify({'id': obj.id, 'prediction': prediction, 'lang': lang})

@app.route('/capture', methods=['POST'])
def capture():
    message_id = request.form['message_id']
    feedback = request.form['feedback']
    # TODO only limit to messages sent in current session
    #      don't set duplicate captured messages
    history_full_instance = HistoryFull.query.get_or_404(message_id)
    setattr(history_full_instance, feedback, True)
    db.session.commit()
    return jsonify({})

@app.route('/user_information', methods=['POST'])
def user_information():
    if not 'chat_id' in session:
        user_name = request.form['user_name'][:MAX_USER_INPUT_LEN]
        user_email = request.form['user_email'][:MAX_EMAIL_LEN]
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

        opening_text = Intent.query.filter_by(intent_name='opening text').first()
        opening_text = dict(map(lambda x: (x.lang, x.text), opening_text.response))

    return jsonify({'code': 200, 'user_name': user_name, 'user_email': user_email, 
                    'chatbox': render_template('user_chatbox.html', opening_text=opening_text, primary_lang=get_primary_lang())})


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

@app.route('/view_missed_intent', methods=['POST'])
def view_missed_intent():
    intents = Intent.query.filter_by(system=False).distinct().all()
    # intents = sorted(intents, key=lambda x: x[1])
    with app.app_context():
        return jsonify({'data': intents})



@app.route('/missed', methods=['GET', 'POST'])
@login_required
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
                # return jsonify({'code': 400})
                raise EmptyRequiredField('The utterance')
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
                # return jsonify({'code': 400})
                raise werkzeug.exceptions.BadRequestKeyError()

                # intents = Intent.query.with_entities(Intent.id, Intent.intent_name).distinct().all()
                # intents = sorted(intents, key=lambda x: x[1])
                # return render_template('intents_add.html', current_page='intents', intents=intents, preset_sample_id=target_id, preset_training_sample=target.utterance)
            intent_id = data['intent']
            new_training_data = create_training_data(target.utterance, intent_id)

            target.trained = True
            db.session.commit()
            # refresh_dataset()
            return jsonify({'code': 200})

    captureds = HistoryFull.query.filter_by(negative=True, trained=False).order_by(HistoryFull.id).all()
    return render_template('missed.html', current_page='missed', captureds=captureds, intents=get_ordered_intent())

@app.route('/missed_new_intent', methods=['POST'])
@login_required
def missed_new_intent():
    target_id = request.form['id']
    target = HistoryFull.query.get_or_404(target_id)
    return render_template('intents_add.html', current_page='intents', previous_page='missed', intents=get_ordered_intent(), primary_lang=get_primary_lang(), 
                            preset_sample_id=target_id, preset_training_sample=target.utterance)



########################
###                  ###
###   INTENTS_EDIT   ###
###                  ###
########################

#GETTER
@app.route('/view_intents_edit', methods=['POST'])
def view_intents_edit():
    data = json.loads(request.data.decode())
    intent_name = data['intent_id']
    print(intent_name)
    intent = Intent.query.get_or_404(intent_name)
    
    with app.app_context():
        return jsonify({'training_data': intent.training_data, 'deployed': intent.deployed, 'small_talk': intent.small_talk})



@app.route('/intents_edit')
@login_required
def intents_base():
    return render_template('intents_base.html', current_page='intents', intents=get_ordered_intent())

@app.route('/intents_edit/<intent_name>', methods=['GET', 'POST'])
@login_required
def intents(intent_name):
    '''
    TODO
    404 error for non-existance intents
    '''
    intent = Intent.query.filter_by(intent_name=intent_name).first_or_404()
    responses = Response.query.filter(Response.intent_id==intent.id, Response.lang.in_(get_selected_lang())).all()
    responses.sort(key=cmp_to_key(compare_response))
    lang = None

    if request.method == 'POST':
        if request.data: # ajax
            data = json.loads(request.data.decode())
            job = data['job']
        else: # form submission
            job = request.form['job']

        if job == 'update_reply_message':
            lang = request.form['lang']
            text = request.form['modified_content']
            try:
                update_response(intent.id, 'text', lang, text)
            except CustomError as ce:
                flash(ce.description)
        elif job == 'update':
            id = data['id']
            new_training_data = update_training_data(id, data['modified_content'])
            return jsonify({'code': 200})
        elif job == 'delete':
            id = data['id']
            temp = TrainingData.query.get(id)
            db.session.delete(temp)
            db.session.commit()
            return jsonify({'code': 200})
        # elif job == 'add_sample':
        #     training_data = create_training_data(request.form['user_message'], intent.id)
        #     if training_data:
        #         db.session.add(training_data)
        db.session.commit()
        # refresh_dataset()
    
    return render_template('intents_edit.html', current_page='intents', intents=get_ordered_intent(), intent=intent, responses=responses, 
                           primary_lang=get_primary_lang(), language=lang)

@app.route('/intents_edit/toggle', methods=['POST'])
@login_required
def toggle():
    data = json.loads(request.data.decode())
    print(data)
    intent = Intent.query.get_or_404(data['intent_id'])
    setattr(intent, data['field'], data['value'])
    db.session.commit()
    return jsonify({'code': 200, 'deployed': intent.deployed, 'small_talk': intent.small_talk})

@app.route('/intents_edit/add_sample', methods=['POST'])
@login_required
def add_sample():
    data = json.loads(request.data.decode())
    print(data)
    training_data = create_training_data(data['user_message'], data['intent_id'])
    return jsonify({'code': 200})


#######################
###                 ###
###   INTENTS_ADD   ###
###                 ###
#######################

@app.route('/intents_add', methods=['GET', 'POST'])
@login_required
def intents_add():
    additional_jinja_vars = {}

    if request.method == 'POST':
        try:
            training_datas_args = [key for key in request.form if 'training_sample' in key]
            training_datas = [strip_tags(request.form[key]) for key in training_datas_args]
            # if 
            """
                behavior:
                    - the form will be rejected if intent_name, reply_messages have issues
                    - if only training samples have issues, the form will be accepted and the training samples are removed with messages flashed
            """
            intent_name = request.form['intent_name']
            reply_message = request.form['reply_message']
            # reply_message_en = request.form['reply_message_en']
            # reply_message_my = request.form['reply_message_my']
            intent = create_intent(intent_name=intent_name, reply_message_en='', reply_message_my='')
            create_response(intent.id, reply_message, 'to be filled in')
            # TODO ajax to signify that a training sample is used
            for training_data in training_datas:
                try:
                    temp = create_training_data(training_data, intent.id)
                except CustomError as ce:
                    flash(ce.description)
                
            if 'preset_sample_id' in request.form:
                temp = HistoryFull.query.get_or_404(request.form['preset_sample_id'])
                temp.trained = True
            db.session.commit()
            # refresh_dataset()
            return redirect('intents_edit/'+intent_name)

        except CustomError as ce:
            flash(ce.description)

            form_data = {
                'intent_name': intent_name, 
                'reply_message': reply_message
                # 'reply_message_en': reply_message_en, 
                # 'reply_message_my': reply_message_my
            }

            target_id = None
            target_utterance = None
            if 'preset_sample_id' in request.form:
                target_id = request.form['preset_sample_id']
                target = HistoryFull.query.get_or_404(target_id)
                if 'training_sample_0' in training_datas_args:
                    target_utterance = strip_tags(request.form['training_sample_0'])
                else:
                    target_utterance = target.utterance
                training_datas = [strip_tags(request.form[key]) for key in training_datas_args if key != 'training_sample_0']
            
            additional_jinja_vars['form_data'] = form_data
            additional_jinja_vars['training_datas'] = training_datas
            additional_jinja_vars['preset_sample_id'] = target_id
            additional_jinja_vars['preset_training_sample'] = target_utterance
    
    return render_template('intents_add.html', current_page='intents', intents=get_ordered_intent(), primary_lang=get_primary_lang(), **additional_jinja_vars)

@app.route('/delete_intent', methods=['POST'])
@login_required
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
        haha = request.form.getlist('select_2')
        print(haha)
        return 'you just posted something mdfk ' + str(haha)
    # try:
    #     raise EmptyRequiredField('Haha')
    # except CustomError as ce:
    #     flash(ce.description)
    return render_template('testing.html')


#########################
###                   ###
###     dashboard     ###
###                   ###
#########################

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html', current_page='dashboard', 
                           percentage_thumbsdown_by_week=percentage_thumbsdown_by_week(), 
                           percentage_thumbsdown_by_intent=percentage_thumbsdown_by_intent(), 
                           popular_questions=popular_questions(), 
                           number_of_users=number_of_users())



#########################
###                   ###
###     dashboard     ###
###                   ###
#########################

@app.route('/setting', methods=['GET', 'POST'])
def setting():
    old_primary_lang = get_primary_lang()
    
    if request.method == 'POST':
        try:
            new_primary_lang = request.form['select_1']
            update_primary_lang(new_primary_lang)
            old_primary_lang = get_primary_lang()
            
            new_selected_lang = request.form.getlist('select_2')
            update_selected_lang(new_selected_lang, old_primary_lang)
        except CustomError as ce:
            flash(ce.description)
    
    langs = get_langs()
    selected_lang = get_selected_lang()
    return render_template('setting.html', current_page='setting', primary_lang=old_primary_lang, langs=langs, selected_lang=selected_lang)



##########################
###                    ###
###   ERROR_HANDLING   ###
###                    ###
##########################

@app.errorhandler(CustomError)
def handle_customError(e):
    return jsonify({'error_description': [e.description]}), e.code

@app.errorhandler(werkzeug.exceptions.BadRequestKeyError)
def handle_badRequestKeyError(e):
    return "Uh uh, don't try anything nasty"
    # raise CustomError(jsonify({'text': 'hello'})) # use this to return object
    # try:
    #     raise CustomError('which side will it be on? try catch or wsgi?')
    # except werkzeug.exceptions.HTTPException as ce:
    #     print('it is wsgi!' + ce.description)
    #     return 'it is wsgi!' + ce.description, 400

    

# if __name__ == '__main__':
#     app.run(debug=True)
