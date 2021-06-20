from flask import Flask, session
from flask_executor import Executor
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import Config
import os
from flask_mail import Mail, Message

application = Flask(__name__)
application.config.from_object(Config)

# get the path for the route folder of the app
base_path = os.path.dirname(os.path.dirname(__file__))
application.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{base_path}/resurface.db'

application.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
application.config['MAIL_PORT'] = 587
application.config['MAIL_USE_TLS'] = True
application.config['MAIL_USERNAME'] = 'apikey'
#application.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')
#application.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
mail = Mail(application)

db = SQLAlchemy(application)
login = LoginManager(application)
executor = Executor(application)
bootstrap = Bootstrap(application)

from resurface import routes, models
db.create_all()
db.session.commit()
