FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main/ .  

# Змінні середовища для локального запуску
# В Cloud Run ці змінні будуть перевизначені або не потрібні
ENV BOT_TOKEN=${BOT_TOKEN}
ENV GOOGLE_SHEET_NAME=${SHEET_NAME}
ENV WEBHOOK_URL=${WEBHOOK_URL}
ENV PORT 8080

CMD ["python", "main.py"]