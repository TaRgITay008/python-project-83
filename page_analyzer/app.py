"""Flask application for page analyzer."""

import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-for-development')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
    
    @app.route('/')
    def index():
        """Home page."""
        return 'Page Analyzer'
    
    return app


app = create_app()
