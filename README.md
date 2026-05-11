### Hexlet tests and linter status:
[![Actions Status](https://github.com/TaRgITay008/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/TaRgITay008/python-project-83/actions)
[![Lint](https://github.com/TaRgITay008/python-project-83/actions/workflows/lint.yml/badge.svg)](https://github.com/TaRgITay008/python-project-83/actions/workflows/lint.yml)
[![Quality](https://img.shields.io/badge/quality-passing-brightgreen)](https://github.com/TaRgITay008/python-project-83)
## Page Analyzer

Page Analyzer — это веб-приложение для SEO-анализа сайтов.

### Функциональность

- Добавление URL с валидацией
- Нормализация URL
- Проверка доступности сайта
- Парсинг SEO-тегов (h1, title, description)
- Хранение истории проверок в PostgreSQL

### Технологии

- Python 3.10+
- Flask
- PostgreSQL
- Bootstrap 5
- Gunicorn
- BeautifulSoup4
- Ruff

### Установка и запуск

```bash
git clone https://github.com/TaRgITay008/python-project-83.git
cd python-project-83
make install
cp .env.example .env
make dev


Деплой
https://python-project-83-gi5s.onrender.com
