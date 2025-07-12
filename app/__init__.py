from flask import Flask
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Buat objek MySQL sekali di level global
mysql = MySQL()

def create_app():
    app = Flask(__name__)

    # Load configuration from environment variables
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'telkom-dashboard-secret'
    app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST') or 'localhost'
    app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER') or 'root'
    app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD') or ''
    app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT') or 3306)
    app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB') or 'db_kp'

    # Init MySQL ke app
    mysql.init_app(app)

    # Register blueprints
    from .routes import main
    from .routes_user_features import user_features
    app.register_blueprint(main)
    app.register_blueprint(user_features)

    # Initialize DB tables
    with app.app_context():
        from .database import init_mysql_db
        init_mysql_db()

    return app
