from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')

user = 'postgres'
pw = 'admin'
host = 'localhost'
port = '5432'
url = f'{host}:{port}'
database = 'fyp_viva'

DB_URL = f'postgresql+psycopg2://{user}:{pw}@{url}/{database}'

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '7423'

db = SQLAlchemy(app)

from app import routes
