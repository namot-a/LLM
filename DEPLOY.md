# Деплой Notion RAG Bot

## Быстрый старт

### 1. Локальная разработка

```bash
# Клонирование и установка
git clone <repository>
cd notiontgLLM

# Установка зависимостей
make install

# Настройка окружения
cp env.example .env
# Отредактируйте .env файл

# Инициализация базы данных
make init-db

# Синхронизация с Notion
make sync-notion

# Запуск приложения
make run
```

### 2. Docker деплой

```bash
# Запуск с Docker Compose
make docker-run

# Проверка логов
make docker-logs

# Остановка
make docker-stop
```

## Production деплой

### Railway

1. Создайте проект на Railway
2. Подключите PostgreSQL с pgvector
3. Добавьте переменные окружения
4. Деплойте код

### Heroku

1. Создайте приложение на Heroku
2. Добавьте PostgreSQL addon
3. Настройте переменные окружения
4. Деплойте через Git

### VPS/Сервер

```bash
# Установка зависимостей
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql postgresql-contrib

# Установка pgvector
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Настройка PostgreSQL
sudo -u postgres psql
CREATE EXTENSION vector;
CREATE DATABASE notionbot;
CREATE USER notionuser WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE notionbot TO notionuser;

# Деплой приложения
git clone <repository>
cd notiontgLLM
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Настройка systemd service
sudo cp notion-bot.service /etc/systemd/system/
sudo systemctl enable notion-bot
sudo systemctl start notion-bot
```

## Мониторинг

### Health Checks

- `GET /health` - базовая проверка
- `GET /ready` - готовность к работе

### Логи

```bash
# Docker
docker-compose logs -f app

# Systemd
journalctl -u notion-bot -f

# Файлы
tail -f logs/app.log
```

### Метрики

- Время ответа API
- Использование токенов
- Количество запросов
- Ошибки и исключения

## Безопасность

### Переменные окружения

- Никогда не коммитьте `.env` файл
- Используйте сильные пароли
- Регулярно ротируйте токены

### Сеть

- Настройте firewall
- Используйте HTTPS в production
- Ограничьте доступ к базе данных

### Telegram

- Используйте webhook вместо polling
- Настройте секретный путь
- Ограничьте пользователей по ID

## Troubleshooting

### Частые проблемы

1. **Ошибка подключения к БД**
   - Проверьте DATABASE_URL
   - Убедитесь что PostgreSQL запущен
   - Проверьте права доступа

2. **Ошибки Notion API**
   - Проверьте NOTION_TOKEN
   - Убедитесь что интеграция имеет доступ к базам
   - Проверьте лимиты API

3. **Ошибки OpenAI**
   - Проверьте OPENAI_API_KEY
   - Убедитесь что есть средства на счету
   - Проверьте лимиты API

4. **Проблемы с Telegram**
   - Проверьте TELEGRAM_BOT_TOKEN
   - Убедитесь что webhook настроен
   - Проверьте логи бота

### Логи и отладка

```bash
# Включить debug режим
export LOG_LEVEL=DEBUG

# Проверить конфигурацию
python -c "from app.config import settings; print(settings.dict())"

# Тест подключения к БД
python -c "from app.db import engine; print('DB OK')"

# Тест Notion API
python -c "from app.notion_sync import notion; print('Notion OK')"
```

## Масштабирование

### Горизонтальное масштабирование

- Используйте load balancer
- Настройте shared session storage
- Масштабируйте базу данных

### Вертикальное масштабирование

- Увеличьте ресурсы сервера
- Настройте connection pooling
- Оптимизируйте запросы

### Кэширование

- Redis для кэширования эмбеддингов
- CDN для статических файлов
- Кэширование ответов API

## Backup и восстановление

### База данных

```bash
# Backup
pg_dump notionbot > backup.sql

# Restore
psql notionbot < backup.sql
```

### Конфигурация

```bash
# Backup env
cp .env .env.backup

# Backup migrations
tar -czf migrations.tar.gz migrations/
```

## Обновления

### Минорные обновления

```bash
git pull
make install
make docker-build
make docker-run
```

### Мажорные обновления

```bash
# Backup данных
make backup

# Обновление кода
git pull
make install

# Миграции БД
make migrate

# Перезапуск
make docker-run
```
