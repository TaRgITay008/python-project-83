"""Flask application for page analyzer."""

import os
import requests
import validators
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from page_analyzer.db import (
    add_url, get_url, get_all_urls_with_last_check, 
    get_checks_for_url, add_check, init_db, normalize_url
)

load_dotenv()


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-for-development')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

    # Инициализируем базу данных
    try:
        init_db()
    except Exception as e:
        print(f"DB init error: {e}")

    @app.route('/')
    def index():
        """Home page."""
        return render_template('index.html')

    @app.route('/urls', methods=['POST'])
    def add_new_url():
        """Add new URL to database."""
        url = request.form.get('url', '').strip()

        if not url:
            flash('URL обязателен', 'danger')
            return render_template('index.html'), 422

        if len(url) > 255:
            flash('URL превышает 255 символов', 'danger')
            return render_template('index.html'), 422

        if not validators.url(url):
            flash('Некорректный URL', 'danger')
            return render_template('index.html'), 422

        normalized = normalize_url(url)
        url_id, is_new = add_url(normalized)

        if is_new:
            flash('Страница успешно добавлена', 'success')
        else:
            flash('Страница уже существует', 'info')

        return redirect(url_for('show_url', id=url_id))

    @app.route('/urls/<int:id>')
    def show_url(id):
        """Show URL details and checks."""
        url = get_url(id)
        if not url:
            flash('Страница не найдена', 'danger')
            return redirect(url_for('index'))
        
        checks = get_checks_for_url(id)
        return render_template('url.html', url=url, checks=checks)

    @app.route('/urls/<int:id>/checks', methods=['POST'])
    def create_check(id):
        """Create a new check for URL by making a real HTTP request."""
        url = get_url(id)
        if not url:
            flash('Страница не найдена', 'danger')
            return redirect(url_for('index'))
        
        try:
            # Выполняем реальный HTTP-запрос
            response = requests.get(url['name'], timeout=5)
            response.raise_for_status()
            
            # Если успешно — сохраняем проверку с кодом ответа
            add_check(id, status_code=response.status_code)
            flash('Страница успешно проверена', 'success')
            
        except (requests.exceptions.RequestException, requests.exceptions.Timeout):
            # Любая ошибка сети, таймаут, 4xx, 5xx
            flash('Произошла ошибка при проверке', 'danger')
        
        return redirect(url_for('show_url', id=id))

    @app.route('/urls')
    def list_urls():
        """Show all URLs with last check date."""
        urls = get_all_urls_with_last_check()
        return render_template('urls.html', urls=urls)

    return app


app = create_app()
