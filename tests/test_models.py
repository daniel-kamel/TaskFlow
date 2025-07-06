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
    assert task.status == 'Not started'
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
    assert task.status == 'Not started'
    assert task.author.username == 'carol'

def test_task_effective_status(session):
    """Test the get_effective_status method."""
    user = User(username='dave', email='dave@example.com', password='pw')
    session.add(user)
    session.commit()

    # Test task with no start date (but it will have default current time)
    task1 = Task(title='No Start Date', user_id=user.id)
    session.add(task1)
    session.commit()
    # Since start_date defaults to current time, it should be 'Pending'
    assert task1.get_effective_status() == 'Pending'

    # Test task with future start date
    future_date = datetime.utcnow() + timedelta(days=1)
    task2 = Task(title='Future Task', user_id=user.id, start_date=future_date)
    session.add(task2)
    session.commit()
    assert task2.get_effective_status() == 'Not started'

    # Test task with past start date
    past_date = datetime.utcnow() - timedelta(days=1)
    task3 = Task(title='Past Task', user_id=user.id, start_date=past_date)
    session.add(task3)
    session.commit()
    assert task3.get_effective_status() == 'Pending'

    # Test completed task
    task4 = Task(title='Completed Task', user_id=user.id, status='Completed')
    session.add(task4)
    session.commit()
    assert task4.get_effective_status() == 'Completed'
