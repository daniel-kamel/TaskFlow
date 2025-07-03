import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from models import db, User
from flask import Flask

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
