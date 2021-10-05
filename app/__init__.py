from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
# from flask_migrate import Migrate
from config import Config


app = Flask(__name__, template_folder='templates')

# user = 'postgres'
# pw = 'admin'
# host = 'localhost'
# port = '5432'
# url = f'{host}:{port}'
# database = 'fyp_viva'

# DB_URL = f'postgresql+psycopg2://{user}:{pw}@{url}/{database}'

# app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = '7423'

app.config.from_object(Config)
db = SQLAlchemy(app)

# migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import routes
