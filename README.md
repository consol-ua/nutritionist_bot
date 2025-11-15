# Telegram Bot Project

## Структура проекту

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
docker-compose -f docker/docker-compose.yml --env-file .env up -d
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
docker-compose -f docker/docker-compose.yml --env-file .env up -d --build
```

############################ Розгортання на Google Compute Engine

1. Підключаємося до GCE

```bash
gcloud compute ssh instance-20250512-170304 --zone=europe-west1-b
```

3. Переносимо файли

```bash
gcloud compute scp --recurse app docker .env main.py requirements.txt instance-20250512-170304:~/bot/ --zone=europe-west1-b
```

**Рекомендований метод (надійніший):**

```bash
# Спочатку директорії
gcloud compute scp --recurse app instance-20250512-170304:~/bot/ --zone=europe-west1-b
gcloud compute scp --recurse docker instance-20250512-170304:~/bot/ --zone=europe-west1-b

# Потім окремі файли (важливо копіювати окремо, щоб уникнути проблем)
gcloud compute scp main.py instance-20250512-170304:~/bot/ --zone=europe-west1-b
gcloud compute scp requirements.txt instance-20250512-170304:~/bot/ --zone=europe-west1-b
gcloud compute scp .env instance-20250512-170304:~/bot/ --zone=europe-west1-b
```

**Перевірка синхронізації (опціонально):**

```bash
# Перевірка розмірів ключових файлів
for file in app/bot/templates/responses.py app/api/routes/webhook.py app/bot/templates/send_payment_link.py main.py; do
  local_size=$(stat -f "%z" "$file" 2>/dev/null || echo "0")
  remote_size=$(gcloud compute ssh instance-20250512-170304 --zone=europe-west1-b --command="stat -c '%s' ~/bot/$file 2>/dev/null || echo '0'" 2>/dev/null | tail -1)
  if [ "$local_size" != "$remote_size" ]; then
    echo "❌ $file: локально=$local_size, на сервері=$remote_size"
  else
    echo "✅ $file: $local_size байт"
  fi
done
```

**Примітка:** Команда `gcloud compute scp --recurse` іноді може пропускати
окремі файли через тимчасові помилки. Якщо файл не оновився, скопіюйте його
окремо:

```bash
gcloud compute scp app/services/wayforpay_service.py instance-20250512-170304:~/bot/app/services/ --zone=europe-west1-b
```

4. Зупинка контейнера:

```bash
docker-compose -f docker/docker-compose.yml down
```

5. Запустіть контейнер:

```bash
docker-compose -f docker/docker-compose.yml --env-file .env up -d --build
```

6. Перегляньте логи:

```bash
docker-compose -f docker/docker-compose.yml logs -f
```

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
