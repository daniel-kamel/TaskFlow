"""
models module for TaskFlow application.
Defines the User and Task models with relationships and authentication methods.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model, UserMixin):
    """
    User model for authentication and task ownership.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='author', lazy=True)

    def __init__(self, **kwargs):
        # Enforce password requirement on object creation
        if 'password' not in kwargs:
            raise ValueError("Password is required")
        password = kwargs.pop('password')
        super().__init__(**kwargs)
        self.set_password(password)  # Auto-hash during creation

    def set_password(self, password):
        """Hashes and stores the password."""
        if not password:
            raise ValueError("Password cannot be empty")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Task(db.Model):
    """
    Task model with user association.
    """
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Not started')  # e.g., 'Not started', 'Pending', 'Completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def get_effective_status(self):
        """Returns the effective status based on start date and current status."""
        if self.status == 'Completed':
            return 'Completed'

        if not self.start_date:
            return 'Not started'

        current_date = datetime.utcnow().date()
        start_date = self.start_date.date()

        if current_date < start_date:
            return 'Not started'
        else:
            return 'Pending'

    def __repr__(self):
        return f'<Task {self.title} (Status: {self.status})>'
