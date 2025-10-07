# Railway Setup

## 1. Переменные окружения

В Railway Dashboard добавьте следующие переменные:

### База данных (автоматически)
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### Telegram
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
ALLOWED_TELEGRAM_USER_IDS=123456789,987654321
WEBHOOK_SECRET_PATH=your_random_secret_path
```

### Notion
```bash
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_IDS=database_id_1,database_id_2
```

### OpenAI
```bash
OPENAI_API_KEY=your_openai_api_key
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
```

### API URL (важно!)
```bash
API_URL=https://your-service-name.up.railway.app
```

## 2. Настройка PostgreSQL

После создания Postgres сервиса:

1. Откройте Postgres сервис
2. Перейдите в "Connect" → "Postgres Connection URL"
3. Подключитесь через CLI:
```bash
railway connect postgres
```

4. Выполните команду для установки pgvector:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## 3. Деплой

После настройки переменных:
1. Railway автоматически пересоберёт проект
2. Проверьте логи: `railway logs`
3. Проверьте здоровье: `curl https://your-service.up.railway.app/health`

## 4. Синхронизация Notion

После успешного деплоя, синхронизируйте базу:
```bash
curl -X POST https://your-service.up.railway.app/api/v1/admin/ingest?secret=your_webhook_secret
```

