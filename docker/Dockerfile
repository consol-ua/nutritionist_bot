FROM python:3.9-slim

WORKDIR /app

# Встановлення залежностей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання коду
COPY . .

# Створення директорії для логів
RUN mkdir -p logs

# Запуск додатку
CMD ["python", "main.py"] 