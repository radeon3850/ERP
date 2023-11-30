import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'erp.db')

    base_path = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(base_path, 'app', 'uploads')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'mp4', 'mov', 'avi', 'wmv', 'flv'}
    FLASK_ADMIN_SWATCH = 'cerulean'
    BABEL_DEFAULT_LOCALE = 'ru' # або інша мова
    SESSION_TYPE = 'sqlalchemy'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=600)

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['vosmoechudosveta@ukr.net']
