from flask import Flask
from flask.cli import FlaskGroup
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime

app = Flask(__name__)

# Config from environment variables
app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
cli = FlaskGroup(app)

# User model example
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(120), nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)

	@property
	def serialize(self):
	  return {
			'id': self.id,
			'username': self.username,
			'created_at': self.created_at.isoformat()
		}

# CLI Commands
@cli.command('init-db')
def init_db():
	"""Initialize the database."""
	db.create_all()
	print('Database initialized!')

@cli.command('create-user')
def create_user():
	"""Create a new user."""
	username = input('Username: ')
	password = input('Password: ')
	user = User(username=username, password=password)
	db.session.add(user)
	db.session.commit()
	print(f'User {username} created successfully!')

if __name__ == '__main__':
	cli()
