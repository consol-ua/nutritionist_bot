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

# Підключення до інстансу

gcloud compute ssh telegram-bot-vm --zone=europe-west1-b

як оновити файли проекта в інстансі?

Ось як оновити файли проекту в інстансі:

1. З вашого локального комп'ютера скопіюйте всі файли: gcloud compute scp
   gcloud compute scp --recurse ./* telegram-bot-vm:~/app/ --zone=europe-west1-b

2. Підключіться до інстансу: gcloud compute ssh telegram-bot-vm
   gcloud compute ssh telegram-bot-vm --zone=europe-west1-b

3. Перейдіть до директорії проекту: cd ~/app

4. Перезапустіть контейнер: docker stop nutritionist-bot docker rm
    docker stop nutritionist-bot
    docker rm nutritionist-bot
    docker build -t nutritionist-bot .
    docker run -d \
      --name nutritionist-bot \
      --env-file .env \
      -p 8080:8080 \
      -v ~/app/credentials:/app/credentials \
      nutritionist-bot

5. Перевірте логи: docker logs nutritionist-bot
