import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from models import db, User, Task
from flask import Flask
from datetime import datetime, timedelta

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def session(app):
    with app.app_context():
        yield db.session

def test_user_password_hashing(session):
    user = User(username='alice', email='alice@example.com', password='secret')
    session.add(user)
    session.commit()
    assert user.password_hash != 'secret'
    assert user.check_password('secret')
    assert not user.check_password('wrong')

def test_user_creation_requires_password():
    with pytest.raises(ValueError):
        User(username='bob', email='bob@example.com')

def test_task_creation_and_defaults(session):
    user = User(username='bob', email='bob@example.com', password='pw')
    session.add(user)
    session.commit()
    task = Task(title='Test Task', user_id=user.id)
    session.add(task)
    session.commit()
    assert task.id is not None
    assert task.status == 'Pending'
    assert task.author == user
    assert isinstance(task.created_at, datetime)
    assert task.due_date is None

def test_task_due_date(session):
    user = User(username='carol', email='carol@example.com', password='pw')
    session.add(user)
    session.commit()
    due = datetime.utcnow() + timedelta(days=3)
    task = Task(title='Due Task', user_id=user.id, due_date=due)
    session.add(task)
    session.commit()
    assert task.due_date == due
    assert task.status == 'Pending'
    assert task.author.username == 'carol'
