# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from config import config  # Import the selected config
from models import db, User, Task
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime

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
    sort_by = request.args.get('sort', 'created')
    tasks = current_user.tasks

    # Convert to list for sorting
    tasks_list = list(tasks)

    if sort_by == 'start_date':
        # Sort by start date, tasks without start date go to the end
        tasks_list.sort(key=lambda x: (x.start_date is None, x.start_date or datetime.max))
    elif sort_by == 'due_date':
        # Sort by due date, tasks without due date go to the end
        tasks_list.sort(key=lambda x: (x.due_date is None, x.due_date or datetime.max))
    else:
        # Default sort by creation date (newest first)
        tasks_list.sort(key=lambda x: x.created_at, reverse=True)

    return render_template('index.html', tasks=tasks_list, current_sort=sort_by)

@app.route('/create-task', methods=['GET', 'POST'])
@login_required
def create_task():
    """Task creation page."""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        due_date = request.form.get('due_date')
        from datetime import datetime
        start_date_obj = None
        due_date_obj = None
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                flash('Invalid start date format.', 'error')
                return redirect(url_for('create_task'))
        if due_date:
            try:
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                flash('Invalid due date format.', 'error')
                return redirect(url_for('create_task'))
        task = Task(title=title, description=description, start_date=start_date_obj, due_date=due_date_obj, user_id=current_user.id)
        # Set initial status based on start date
        task.status = task.get_effective_status()
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!')
        return redirect(url_for('index'))
    from datetime import datetime
    today_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('create_task.html', today_date=today_date)

@app.route('/edit-task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Edit task page."""
    task = Task.query.get_or_404(task_id)
    # Ensure the task belongs to the current user
    if task.user_id != current_user.id:
        flash('You can only edit your own tasks.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form.get('description')
        task.status = request.form.get('status', 'Not started')
        start_date = request.form.get('start_date')
        due_date = request.form.get('due_date')
        from datetime import datetime
        start_date_obj = None
        due_date_obj = None
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                flash('Invalid start date format.', 'error')
                return redirect(url_for('edit_task', task_id=task_id))
        if due_date:
            try:
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                flash('Invalid due date format.', 'error')
                return redirect(url_for('edit_task', task_id=task_id))
        task.start_date = start_date_obj
        task.due_date = due_date_obj

        # Auto-update status based on start date (only if not completed)
        if task.status != 'Completed':
            task.status = task.get_effective_status()

        db.session.commit()
        flash('Task updated successfully!')
        return redirect(url_for('index'))
    return render_template('edit_task.html', task=task)

@app.route('/delete-task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete task."""
    task = Task.query.get_or_404(task_id)
    # Ensure the task belongs to the current user
    if task.user_id != current_user.id:
        flash('You can only delete your own tasks.', 'error')
        return redirect(url_for('index'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!')
    return redirect(url_for('index'))

@app.route('/complete-task/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    """Mark task as completed."""
    task = Task.query.get_or_404(task_id)
    # Ensure the task belongs to the current user
    if task.user_id != current_user.id:
        flash('You can only modify your own tasks.', 'error')
        return redirect(url_for('index'))

    task.status = 'Completed'
    db.session.commit()
    flash('Task marked as completed!')
    return redirect(url_for('index'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """Account settings page."""
    if request.method == 'POST':
        # Check if this is a profile update or password change
        if 'current_password' in request.form:
            # Password change
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_new_password = request.form['confirm_new_password']

            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'error')
                return redirect(url_for('account'))

            if new_password != confirm_new_password:
                flash('New passwords do not match.', 'error')
                return redirect(url_for('account'))

            if len(new_password) < 6:
                flash('New password must be at least 6 characters long.', 'error')
                return redirect(url_for('account'))

            current_user.set_password(new_password)
            db.session.commit()
            flash('Password updated successfully!')
            return redirect(url_for('account'))
        else:
            # Profile update
            username = request.form['username']
            email = request.form['email']

            # Check if username or email already exists (excluding current user)
            existing_user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).filter(User.id != current_user.id).first()

            if existing_user:
                flash('Username or email already exists.', 'error')
                return redirect(url_for('account'))

            current_user.username = username
            current_user.email = email
            db.session.commit()
            flash('Profile updated successfully!')
            return redirect(url_for('account'))

    return render_template('account.html')

@app.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html')

@app.route('/api/tasks')
@login_required
def api_tasks():
    tasks = current_user.tasks
    events = []
    for task in tasks:
        events.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'start': task.start_date.strftime('%Y-%m-%d') if task.start_date else None,
            'end': task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
            'status': task.status
        })
    return jsonify(events)

@app.cli.command("init-db")
def init_db():
    db.create_all()
    print(f"Database initialized in {app.config['ENVIRONMENT']} mode!")

if __name__ == '__main__':
    app.run()
