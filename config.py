import os


user = 'user'
pw = 'pw'
host = 'psqldb'
port = '1234'
url = f'{host}:{port}'
database = 'database'

DB_URL = f'postgresql+psycopg2://{user}:{pw}@{url}/{database}'

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'yeah-babe'
    SQLALCHEMY_DATABASE_URI = DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
