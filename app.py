# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from config import config  # Import the selected config
from models import db, User, Task
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config.from_object(config)  # Apply configuration
db.init_app(app)

# --- Flask-Login setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = None  # Suppress the default flash message

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Authentication Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists', 'error')
            return redirect(url_for('register'))
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Sign in page."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            user = User.query.filter_by(username=username).first()
        except Exception:
            flash('Database error: Please initialize the database with "flask init-db".', 'error')
            return render_template('login.html')
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout route."""
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
@login_required
def index():
    """Home page showing user's tasks."""
    tasks = current_user.tasks
    return render_template('index.html', tasks=tasks)

@app.route('/create-task', methods=['GET', 'POST'])
@login_required
def create_task():
    """Task creation page."""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        status = request.form.get('status', 'Pending')
        from datetime import datetime
        due_date_obj = None
        if due_date:
            try:
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                flash('Invalid due date format.')
                return redirect(url_for('create_task'))
        task = Task(title=title, description=description, due_date=due_date_obj, status=status, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!')
        return redirect(url_for('index'))
    return render_template('create_task.html')

@app.cli.command("init-db")
def init_db():
    db.create_all()
    print(f"Database initialized in {app.config['ENVIRONMENT']} mode!")

if __name__ == '__main__':
    app.run()
