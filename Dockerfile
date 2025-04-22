FROM python:3.9-slim

WORKDIR /app

# Встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код
COPY main/ .

# Налаштування для production
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Запускаємо через gunicorn для кращої продуктивності
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app