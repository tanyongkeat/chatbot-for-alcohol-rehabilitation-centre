import os


user = os.environ.get('PSQL_USER')
pw = os.environ.get('PSQL_PW')
host = 'psqldb'
port = os.environ.get('PSQL_PORT')
url = f'{host}:{port}'
database = os.environ.get('PSQL_DATABASE')

DB_URL = f'postgresql+psycopg2://{user}:{pw}@{url}/{database}'

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hello-hello-hello'
    SQLALCHEMY_DATABASE_URI = DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
