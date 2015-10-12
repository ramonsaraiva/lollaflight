from flask import Flask
from flask import send_from_directory

from flask.ext.restful import Api

from models import db

from resources import Check
from resources import Surveys

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update({
	'SQLALCHEMY_DATABASE_URI': 'postgresql://lolla:lolla@localhost/lolla'
})

db.init_app(app)
api = Api(app)

api.add_resource(Surveys, '/surveys/')
api.add_resource(Check, '/check/')

@app.route('/')
def send_template():
	return send_from_directory('templates', 'base.html')

@app.route('/<path:path>')
def send_static(path):
	return send_from_directory('static', path)

@app.cli.command()
def drop():
	db.drop_all()

@app.cli.command()
def create():
	db.create_all()
