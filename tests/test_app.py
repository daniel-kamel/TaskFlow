import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from models import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def register(client, username, email, password):
    return client.post('/register', data={
        'username': username,
        'email': email,
        'password': password
    }, follow_redirects=True)

def login(client, username, password):
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_register_login_logout(client):
    # Register
    rv = register(client, 'testuser', 'test@example.com', 'testpass')
    assert b'Registration successful' in rv.data

    # Login
    rv = login(client, 'testuser', 'testpass')
    assert b'Hello, testuser!' in rv.data

    # Access protected route
    rv = client.get('/')
    assert b'Hello, testuser!' in rv.data

    # Logout
    rv = logout(client)
    assert b'You have been logged out.' in rv.data

    # Access protected route after logout
    rv = client.get('/', follow_redirects=True)
    assert b'Login' in rv.data
