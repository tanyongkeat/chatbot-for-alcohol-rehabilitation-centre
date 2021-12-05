from app import app, db
from app.models import Admin, HistoryFull, ChatHistory, TrainingData, Response, Intent, Setting
from app.intent import model
# from waitress import serve

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Admin': Admin, 'HistoryFull': HistoryFull, 'ChatHistory': ChatHistory, 'TrainingData': TrainingData, 'Response': Response, 
            'Intent': Intent, 'Setting': Setting, 'model': model}

if __name__ == '__main__':
    app.run()
    # serve(app, host='0.0.0.0', port=5000)