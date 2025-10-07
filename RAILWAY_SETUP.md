# Railway Setup - Быстрая настройка

## ✅ Что уже сделано:
- ✅ Код загружен на GitHub
- ✅ Проект создан в Railway
- ✅ PostgreSQL база данных добавлена
- ✅ Сервис приложения создан

## 🔧 Что нужно сделать:

### 1. Добавить переменные окружения

В Railway Dashboard (уже открыт в браузере):
1. Выберите сервис **LLM**
2. Перейдите на вкладку **Variables**  
3. Нажмите **New Variable** и добавьте:

**Обязательные переменные:**

```bash
# База данных (reference к Postgres сервису)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_from_@BotFather
ALLOWED_TELEGRAM_USER_IDS=your_telegram_id
WEBHOOK_SECRET_PATH=random_secret_123456

# Notion  
NOTION_TOKEN=secret_xxxxxxxxxxxx
NOTION_DATABASE_IDS=notion_db_id_1,notion_db_id_2

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxx
```

**Опциональные (уже есть значения по умолчанию):**
```bash
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
API_URL=https://your-service.up.railway.app
LOG_LEVEL=INFO
```

### 2. Получить API URL

После добавления переменных:
1. Railway автоматически запустит деплой
2. Дождитесь успешного деплоя (2-3 минуты)
3. Скопируйте URL сервиса (например: `https://llm-production.up.railway.app`)
4. Добавьте переменную `API_URL` с этим URL

### 3. Проверка деплоя

```bash
# Локально через CLI
railway logs --service LLM

# Или проверьте в браузере
curl https://your-service.up.railway.app/health
```

Должен вернуться ответ:
```json
{"status":"healthy","timestamp":"2025-01-..."}
```

### 4. Настройка pgvector (автоматически)

База данных и расширение pgvector инициализируются автоматически при первом запуске!

## 4. Синхронизация Notion

После успешного деплоя, синхронизируйте базу:
```bash
curl -X POST https://your-service.up.railway.app/api/v1/admin/ingest?secret=your_webhook_secret
```

