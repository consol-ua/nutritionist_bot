# Telegram Bot Project

## Структура проекту

```
nutritionist_bot/
├── app/
│   ├── __init__.py
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── common.py
│   │   │   └── user.py
│   │   ├── keyboards/
│   │   │   ├── __init__.py
│   │   │   └── reply.py
│   │   └── middlewares/
│   │       ├── __init__.py
│   │       └── error_handler.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── webhook.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── firestore.py
│   └── services/
│       ├── __init__.py
│       └── scheduler.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── logs/
├── tests/
│   └── __init__.py
├── .env.example
├── .gitignore
├── requirements.txt
└── main.py
```

## Опис компонентів

- `app/bot/` - Основний код телеграм бота

  - `handlers/` - Обробники команд та повідомлень
  - `keyboards/` - Клавіатури для бота
  - `middlewares/` - Проміжні обробники (middleware)

- `app/api/` - FastAPI додаток

  - `routes/` - API ендпоінти
  - `dependencies.py` - Залежності для API

- `app/core/` - Ядро додатку

  - `config.py` - Конфігурація
  - `logging.py` - Налаштування логування
  - `exceptions.py` - Глобальні винятки

- `app/db/` - Робота з базою даних

  - `firestore.py` - Інтеграція з Firestore

- `app/services/` - Сервіси

  - `scheduler.py` - Сервіс для відкладених повідомлень

- `docker/` - Docker конфігурація
- `logs/` - Директорія для логів
- `tests/` - Тести

## Вимоги

- Python 3.9+
- Docker
- Google Cloud SDK

## Встановлення

### 1. Встановлення Docker (MacOS)

1. Завантажте Docker Desktop для Mac з
   [офіційного сайту](https://www.docker.com/products/docker-desktop)
2. Встановіть завантажений пакет
3. Перезавантажте комп'ютер
4. Запустіть Docker Desktop з папки Applications
5. Дочекайтеся повного запуску (іконка в меню буде показувати, що Docker працює)
6. Перевірте встановлення:

```bash
docker --version
docker-compose --version
```

### 2. Встановлення проекту

1. Клонуйте репозиторій
2. Створіть віртуальне середовище:

```bash
python3 -m venv venv
source venv/bin/activate  # для Linux/Mac
```

3. Встановіть залежності:

```bash
pip install -r requirements.txt
```

4. Скопіюйте `.env.example` в `.env` та налаштуйте змінні середовища:

```bash
cp .env.example .env
```

## Запуск

### Локальний запуск

```bash
python main.py
```

### Docker

1. Переконайтеся, що Docker Desktop запущений
2. Запустіть контейнери:

```bash
docker-compose -f docker/docker-compose.yml up -d
```

3. Перевірте статус контейнерів:

```bash
docker-compose -f docker/docker-compose.yml ps
```

4. Перегляньте логи:

```bash
docker-compose -f docker/docker-compose.yml logs -f
```

5. Зупинка контейнера:

```bash
docker-compose -f docker/docker-compose.yml down
```

Перебудуйте Docker контейнер:

```bash
docker-compose -f docker/docker-compose.yml up --build
```

## Розгортання на Google Compute Engine

1. Налаштуйте Google Cloud SDK
2. Створіть інстанс на GCE
3. Налаштуйте Docker на інстансі
4. Запустіть контейнер:

```bash
docker-compose -f docker/docker-compose.yml up -d
```

## Вирішення проблем

### Docker не запускається

1. Перевірте, чи запущений Docker Desktop
2. Спробуйте перезапустити Docker Desktop
3. Перевірте статус Docker:

```bash
docker info
```

### Помилка з ngrok

1. Перевірте наявність токена ngrok в `.env`
2. Перевірте логи ngrok:

```bash
docker-compose -f docker/docker-compose.yml logs ngrok
```
