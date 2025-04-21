# Telegram Bot на Google Cloud Run

## Опис проекту

Цей проект представляє собою Telegram бота, який розгортається на Google Cloud
Run.

## Конфігурація проекту

Проект використовує наступні налаштування:

### Python налаштування

- Форматування коду: Black
- Лінтер: Pylint
- Автоматичне організування імпортів
- Автоматичне форматування при збереженні

### Ігноровані файли

- Віртуальне середовище (venv)
- Кеш Python (**pycache**, \*.pyc)
- Конфігураційні файли (.env, .git)
- Логи (\*.log)
- Docker файли (Dockerfile, docker-compose.yml, .dockerignore)
- Cloud Build конфігурація (cloudbuild.yaml)
- Залежності Python (requirements.txt)
- YAML файли (_.yaml, _.yml)

### Telegram налаштування

- Bot Token
- Webhook URL

### Google Cloud налаштування

- Project ID
- Region
- Service Name

## Встановлення та запуск

(Тут буде додана інструкція з встановлення та запуску)

для запуску:

python3 main/main.py

ngrok http 8080
