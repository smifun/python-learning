import os

basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = 'flasktaskr.db'

CSRF_ENABLED = True
SECRET_KEY = 'my_very_secret_key'

DATABASE_PATH = os.path.join(basedir, DATABASE)

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
