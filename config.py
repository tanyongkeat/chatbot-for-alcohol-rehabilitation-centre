import os


user = 'postgres'
pw = 'Byte$Postgres9479'
host = 'psqldb'
port = '5432'
url = f'{host}:{port}'
database = 'fyp_viva'

DB_URL = f'postgresql+psycopg2://{user}:{pw}@{url}/{database}'

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'yeah-babe'
    SQLALCHEMY_DATABASE_URI = DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
