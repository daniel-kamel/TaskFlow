# app.py
from flask import Flask
from config import config  # Import the selected config
from models import db

app = Flask(__name__)
app.config.from_object(config)  # Apply configuration
db.init_app(app)

@app.cli.command("init-db")
def init_db():
    db.create_all()
    print(f"Database initialized in {app.config['ENVIRONMENT']} mode!")

if __name__ == '__main__':
    app.run()
