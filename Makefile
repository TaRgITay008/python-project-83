# Установка зависимостей
install:
	uv sync

# Запуск в режиме разработки
dev:
	uv run flask --debug --app page_analyzer:app run

# Запуск в продакшене
PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

# Сборка для деплоя
build:
	./build.sh

# Запуск на render.com
render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

# Линтер
lint:
	uv run flake8 page_analyzer

# Тесты
test:
	uv run pytest

.PHONY: install dev start build render-start lint test

lint:
	uv run ruff check page_analyzer
