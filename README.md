# TaskFlow - Flask Task Management App

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.x-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

A comprehensive task management web application built with **Python Flask**, featuring user authentication, advanced task management, and a modern web interface. Developed as a portfolio project demonstrating full-stack web development skills.

🔗 **Live Demo**: [Coming Soon]

## ✨ Features

### 🔐 User Authentication & Management
- **User Registration & Login**: Secure user registration with email validation
- **Password Management**: Password hashing, change functionality, and validation
- **Account Settings**: Profile updates (username, email) and password changes
- **Session Management**: Flask-Login integration with secure session handling

### 📋 Task Management
- **Full CRUD Operations**: Create, read, update, and delete tasks
- **Task Details**: Title, description, status tracking, start dates, and due dates
- **Smart Status Management**: Automatic status updates based on dates
- **Task Sorting**: Sort by creation date, start date, or due date
- **Quick Actions**: Mark tasks as completed with one click

### 📅 Calendar Integration
- **Calendar View**: Visual calendar interface for task management
- **API Endpoint**: RESTful API for calendar data integration
- **Date-based Task Display**: Tasks shown on their respective dates

### 🎨 User Interface
- **Responsive Design**: Bootstrap 5 integration for mobile-friendly interface
- **Modern UI**: Clean, intuitive interface with proper form validation
- **Flash Messages**: User feedback for all actions
- **Navigation**: Intuitive navigation between different sections

### 🗄️ Database & Configuration
- **Flexible Database**: SQLite (development) / PostgreSQL (production-ready)
- **Environment Configuration**: Separate dev/prod configurations
- **Database Initialization**: CLI command for easy database setup
- **Data Validation**: Comprehensive input validation and error handling

### 🧪 Testing
- **Unit Tests**: Comprehensive test suite for models and application logic
- **Test Coverage**: Tests for user authentication, task operations, and data validation

## 🛠️ Technologies Used

### Backend
- **Python 3.9+**: Core programming language
- **Flask 2.3.2**: Web framework
- **Flask-SQLAlchemy 3.0.3**: Database ORM
- **Flask-Login 0.6.2**: User session management
- **Werkzeug 2.3.7**: Security utilities (password hashing)

### Frontend
- **HTML5/CSS3**: Semantic markup and styling
- **Bootstrap 5**: Responsive UI framework
- **Jinja2 3.1.2**: Template engine
- **JavaScript**: Interactive calendar functionality

### Database
- **SQLAlchemy 2.0.19**: Database abstraction layer
- **SQLite**: Development database
- **PostgreSQL**: Production database

### Development & Deployment
- **Python-dotenv**: Environment variable management
- **Pytest**: Testing framework
- **Git**: Version control

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/daniel-kamel/TaskFlow.git
   cd TaskFlow
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (create a `.env` file):
   ```bash
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///taskflow.db
   ENVIRONMENT=dev
   ```

5. **Initialize the database**:
   ```bash
   flask init-db
   ```

6. **Run the application**:
   ```bash
   python app.py
   ```

7. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

## 📁 Project Structure

```
TaskFlow/
├── app.py                 # Main Flask application
├── models.py              # Database models (User, Task)
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Task dashboard
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── create_task.html   # Task creation
│   ├── edit_task.html     # Task editing
│   ├── account.html       # Account settings
│   └── calendar.html      # Calendar view
├── static/                # Static assets
│   └── style.css          # Custom CSS
├── tests/                 # Test suite
│   ├── test_app.py        # Application tests
│   └── test_models.py     # Model tests
└── instance/              # Instance-specific files (database)
```

## 🧪 Running Tests

```bash
pytest tests/
```

## 🚀 Deployment

### Production Setup
1. Set `ENVIRONMENT=prod` in your environment variables
2. Configure PostgreSQL database URL
3. Set a strong `SECRET_KEY`
4. Use Gunicorn as the WSGI server:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

### Environment Variables
- `SECRET_KEY`: Flask secret key for session security
- `DATABASE_URL`: Database connection string
- `ENVIRONMENT`: Set to 'prod' for production mode

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 👨‍💻 Author

**Daniel Kamel** - Backend-focused software engineer

---

⭐ **Star this repository if you find it helpful!**
