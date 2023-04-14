from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin

db = SQLAlchemy()


# Creating database tables
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    todo_list = relationship('Todo', back_populates='user')


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(250), nullable=False)
    estimated_end_date = db.Column(db.DateTime, nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    task_started = db.Column(db.Boolean, default=False, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    task_finished = db.Column(db.Boolean, default=False, nullable=False)
    archived = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', back_populates='todo_list')
