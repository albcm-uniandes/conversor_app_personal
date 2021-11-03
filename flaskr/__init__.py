from flask import Flask
import os


def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.environ["RDS_USERNAME"]}:'
    f'{os.environ["RDS_PASSWORD"]}@{os.environ["RDS_HOST"]}'
    f':{os.environ["RDS_PORT"]}/'
    f'{os.environ["RDS_DATABASE"]}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'no-hay-frase'
    app.config['PROPAGATE_EXCEPTIONS'] = True
    return app
