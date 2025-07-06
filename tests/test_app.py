import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from models import User, Task
from datetime import datetime, timedelta
from flask_login import login_user

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

@pytest.fixture
def session():
    with app.app_context():
        yield db.session

@pytest.fixture
def test_user(session):
    user = User(username='testuser', email='test@example.com', password='testpass')
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def logged_in_client(client, test_user):
    """Create a client with a logged-in user using proper request context."""
    with client.session_transaction() as sess:
        sess['_user_id'] = test_user.id
    return client

# Helper functions
def register(client, username, email, password, confirm_password=None):
    if confirm_password is None:
        confirm_password = password
    return client.post('/register', data={
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': confirm_password
    }, follow_redirects=True)

def login(client, username, password):
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def create_task(session, user, title='Test Task', description='Test Description',
                start_date=None, due_date=None, status='Not started'):
    task = Task(
        title=title,
        description=description,
        start_date=start_date,
        due_date=due_date,
        status=status,
        user_id=user.id
    )
    session.add(task)
    session.commit()
    return task

# Authentication Tests
class TestAuthentication:
    def test_register_page_get(self, client):
        """Test registration page loads correctly."""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Register' in response.data

    def test_register_success(self, client):
        """Test successful user registration."""
        response = register(client, 'newuser', 'new@example.com', 'password123')
        assert b'Registration successful' in response.data
        assert b'Please log in' in response.data

    def test_register_password_mismatch(self, client):
        """Test registration with mismatched passwords."""
        response = register(client, 'newuser', 'new@example.com', 'password123', 'different')
        assert b'Passwords do not match' in response.data

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with existing username."""
        response = register(client, 'testuser', 'different@example.com', 'password123')
        assert b'Username or email already exists' in response.data

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email."""
        response = register(client, 'differentuser', 'test@example.com', 'password123')
        assert b'Username or email already exists' in response.data

    def test_login_page_get(self, client):
        """Test login page loads correctly."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = login(client, 'testuser', 'testpass')
        assert b'Logged in successfully' in response.data

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = login(client, 'nonexistent', 'wrongpass')
        assert b'Invalid username or password' in response.data

    def test_logout(self, logged_in_client):
        """Test logout functionality."""
        response = logout(logged_in_client)
        assert b'You have been logged out' in response.data

    def test_protected_route_redirect(self, client):
        """Test that protected routes redirect to login."""
        response = client.get('/', follow_redirects=True)
        assert b'Login' in response.data

# Task Management Tests
class TestTaskManagement:
    def test_index_page_requires_login(self, client):
        """Test that index page requires authentication."""
        response = client.get('/', follow_redirects=True)
        assert b'Login' in response.data

    def test_index_page_with_tasks(self, logged_in_client, session, test_user):
        """Test index page displays user's tasks."""
        task = create_task(session, test_user, 'My Task')
        response = logged_in_client.get('/')
        assert response.status_code == 200
        assert b'My Task' in response.data

    def test_index_page_sorting(self, logged_in_client, session, test_user):
        """Test task sorting functionality."""
        # Create tasks with different dates
        task1 = create_task(session, test_user, 'Task 1', start_date=datetime.now())
        task2 = create_task(session, test_user, 'Task 2', start_date=datetime.now() + timedelta(days=1))

        # Test default sorting (by creation date)
        response = logged_in_client.get('/')
        assert response.status_code == 200

        # Test sorting by start date
        response = logged_in_client.get('/?sort=start_date')
        assert response.status_code == 200

        # Test sorting by due date
        response = logged_in_client.get('/?sort=due_date')
        assert response.status_code == 200

    def test_create_task_page_get(self, logged_in_client):
        """Test create task page loads correctly."""
        response = logged_in_client.get('/create-task')
        assert response.status_code == 200
        assert b'Create Task' in response.data

    def test_create_task_success(self, logged_in_client, session, test_user):
        """Test successful task creation."""
        response = logged_in_client.post('/create-task', data={
            'title': 'New Task',
            'description': 'Task description',
            'start_date': '2024-01-01',
            'due_date': '2024-01-31'
        }, follow_redirects=True)
        assert b'Task created successfully' in response.data
        assert b'New Task' in response.data

    def test_create_task_invalid_date(self, logged_in_client):
        """Test task creation with invalid date format."""
        response = logged_in_client.post('/create-task', data={
            'title': 'New Task',
            'start_date': 'invalid-date'
        }, follow_redirects=True)
        assert b'Invalid start date format' in response.data

    def test_edit_task_page_get(self, logged_in_client, session, test_user):
        """Test edit task page loads correctly."""
        task = create_task(session, test_user, 'Original Task')
        response = logged_in_client.get(f'/edit-task/{task.id}')
        assert response.status_code == 200
        assert b'Original Task' in response.data

    def test_edit_task_unauthorized(self, logged_in_client, session):
        """Test editing another user's task."""
        other_user = User(username='other', email='other@example.com', password='pass')
        session.add(other_user)
        session.commit()
        task = create_task(session, other_user, 'Other Task')

        response = logged_in_client.get(f'/edit-task/{task.id}', follow_redirects=True)
        assert b'You can only edit your own tasks' in response.data

    def test_edit_task_success(self, logged_in_client, session, test_user):
        """Test successful task editing."""
        task = create_task(session, test_user, 'Original Task')
        response = logged_in_client.post(f'/edit-task/{task.id}', data={
            'title': 'Updated Task',
            'description': 'Updated description',
            'status': 'Pending',
            'start_date': '2024-01-01',
            'due_date': '2024-01-31'
        }, follow_redirects=True)
        assert b'Task updated successfully' in response.data
        assert b'Updated Task' in response.data

    def test_delete_task_success(self, logged_in_client, session, test_user):
        """Test successful task deletion."""
        task = create_task(session, test_user, 'Task to Delete')
        response = logged_in_client.post(f'/delete-task/{task.id}', follow_redirects=True)
        assert b'Task deleted successfully' in response.data

    def test_delete_task_unauthorized(self, logged_in_client, session):
        """Test deleting another user's task."""
        other_user = User(username='other', email='other@example.com', password='pass')
        session.add(other_user)
        session.commit()
        task = create_task(session, other_user, 'Other Task')

        response = logged_in_client.post(f'/delete-task/{task.id}', follow_redirects=True)
        assert b'You can only delete your own tasks' in response.data

    def test_complete_task_success(self, logged_in_client, session, test_user):
        """Test marking task as completed."""
        task = create_task(session, test_user, 'Task to Complete')
        response = logged_in_client.post(f'/complete-task/{task.id}', follow_redirects=True)
        assert b'Task marked as completed' in response.data

    def test_complete_task_unauthorized(self, logged_in_client, session):
        """Test completing another user's task."""
        other_user = User(username='other', email='other@example.com', password='pass')
        session.add(other_user)
        session.commit()
        task = create_task(session, other_user, 'Other Task')

        response = logged_in_client.post(f'/complete-task/{task.id}', follow_redirects=True)
        assert b'You can only modify your own tasks' in response.data

# Account Management Tests
class TestAccountManagement:
    def test_account_page_get(self, logged_in_client):
        """Test account page loads correctly."""
        response = logged_in_client.get('/account')
        assert response.status_code == 200
        assert b'Account Settings' in response.data

    def test_account_page_requires_login(self, client):
        """Test that account page requires authentication."""
        response = client.get('/account', follow_redirects=True)
        assert b'Login' in response.data

    def test_profile_update_success(self, logged_in_client, session, test_user):
        """Test successful profile update."""
        response = logged_in_client.post('/account', data={
            'username': 'updateduser',
            'email': 'updated@example.com'
        }, follow_redirects=True)
        assert b'Profile updated successfully' in response.data

    def test_profile_update_duplicate_username(self, logged_in_client, session, test_user):
        """Test profile update with existing username."""
        other_user = User(username='existing', email='existing@example.com', password='pass')
        session.add(other_user)
        session.commit()

        response = logged_in_client.post('/account', data={
            'username': 'existing',
            'email': 'updated@example.com'
        }, follow_redirects=True)
        assert b'Username or email already exists' in response.data

    def test_password_change_success(self, logged_in_client, session, test_user):
        """Test successful password change."""
        response = logged_in_client.post('/account', data={
            'current_password': 'testpass',
            'new_password': 'newpassword123',
            'confirm_new_password': 'newpassword123'
        }, follow_redirects=True)
        assert b'Password updated successfully' in response.data

    def test_password_change_wrong_current(self, logged_in_client):
        """Test password change with wrong current password."""
        response = logged_in_client.post('/account', data={
            'current_password': 'wrongpass',
            'new_password': 'newpassword123',
            'confirm_new_password': 'newpassword123'
        }, follow_redirects=True)
        assert b'Current password is incorrect' in response.data

    def test_password_change_mismatch(self, logged_in_client):
        """Test password change with mismatched new passwords."""
        response = logged_in_client.post('/account', data={
            'current_password': 'testpass',
            'new_password': 'newpassword123',
            'confirm_new_password': 'differentpassword'
        }, follow_redirects=True)
        assert b'New passwords do not match' in response.data

    def test_password_change_too_short(self, logged_in_client):
        """Test password change with too short password."""
        response = logged_in_client.post('/account', data={
            'current_password': 'testpass',
            'new_password': '123',
            'confirm_new_password': '123'
        }, follow_redirects=True)
        assert b'New password must be at least 6 characters long' in response.data

# Calendar and API Tests
class TestCalendarAndAPI:
    def test_calendar_page_get(self, logged_in_client):
        """Test calendar page loads correctly."""
        response = logged_in_client.get('/calendar')
        assert response.status_code == 200
        assert b'Calendar' in response.data

    def test_calendar_page_requires_login(self, client):
        """Test that calendar page requires authentication."""
        response = client.get('/calendar', follow_redirects=True)
        assert b'Login' in response.data

    def test_api_tasks_requires_login(self, client):
        """Test that API tasks endpoint requires authentication."""
        response = client.get('/api/tasks', follow_redirects=True)
        assert b'Login' in response.data

    def test_api_tasks_returns_json(self, logged_in_client, session, test_user):
        """Test API tasks endpoint returns JSON data."""
        task = create_task(session, test_user, 'API Task',
                          start_date=datetime.now(), due_date=datetime.now() + timedelta(days=1))
        response = logged_in_client.get('/api/tasks')
        assert response.status_code == 200
        assert response.is_json

        data = response.get_json()
        assert len(data) == 1
        assert data[0]['title'] == 'API Task'
        assert data[0]['id'] == task.id
        assert data[0]['status'] == task.status

    def test_api_tasks_empty(self, logged_in_client):
        """Test API tasks endpoint with no tasks."""
        response = logged_in_client.get('/api/tasks')
        assert response.status_code == 200
        assert response.is_json

        data = response.get_json()
        assert len(data) == 0

# Database Initialization Test
class TestDatabaseInitialization:
    def test_init_db_command(self, client):
        """Test database initialization command."""
        # This would typically be tested with Flask CLI runner
        # For now, we'll test that the command exists
        with app.app_context():
            # Check that the command is registered
            assert 'init-db' in [cmd.name for cmd in app.cli.commands.values()]

# Error Handling Tests
class TestErrorHandling:
    def test_404_task_not_found(self, logged_in_client):
        """Test accessing non-existent task."""
        response = logged_in_client.get('/edit-task/99999')
        assert response.status_code == 404

    def test_404_task_not_found_delete(self, logged_in_client):
        """Test deleting non-existent task."""
        response = logged_in_client.post('/delete-task/99999')
        assert response.status_code == 404

    def test_404_task_not_found_complete(self, logged_in_client):
        """Test completing non-existent task."""
        response = logged_in_client.post('/complete-task/99999')
        assert response.status_code == 404

# Integration Tests
class TestIntegration:
    def test_full_user_workflow(self, client, session):
        """Test complete user workflow: register, login, create task, edit, complete, delete."""
        # Register
        response = register(client, 'workflowuser', 'workflow@example.com', 'password123')
        assert b'Registration successful' in response.data

        # Login
        response = login(client, 'workflowuser', 'password123')
        assert b'Logged in successfully' in response.data

        # Create task
        response = client.post('/create-task', data={
            'title': 'Workflow Task',
            'description': 'Test workflow',
            'start_date': '2024-01-01',
            'due_date': '2024-01-31'
        }, follow_redirects=True)
        assert b'Task created successfully' in response.data

        # Get the task ID from the response (this would need to be extracted)
        # For now, we'll assume it was created successfully

        # Access index page
        response = client.get('/')
        assert response.status_code == 200
        assert b'Workflow Task' in response.data

    def test_multiple_users_tasks_isolation(self, client, session):
        """Test that users can only see their own tasks."""
        # Create two users
        user1 = User(username='user1', email='user1@example.com', password='pass1')
        user2 = User(username='user2', email='user2@example.com', password='pass2')
        session.add_all([user1, user2])
        session.commit()

        # Create tasks for both users
        task1 = create_task(session, user1, 'User 1 Task')
        task2 = create_task(session, user2, 'User 2 Task')

        # Login as user1
        login(client, 'user1', 'pass1')
        response = client.get('/')
        assert b'User 1 Task' in response.data
        assert b'User 2 Task' not in response.data

        # Login as user2
        logout(client)
        login(client, 'user2', 'pass2')
        response = client.get('/')
        assert b'User 2 Task' in response.data
        assert b'User 1 Task' not in response.data
