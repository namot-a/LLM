# 🤖 Notion Telegram RAG Bot

A production-ready Telegram bot that answers questions based on your Notion documentation using RAG (Retrieval-Augmented Generation) with OpenAI embeddings.

## ✨ Features

- 🔍 **RAG System**: Retrieves relevant information from Notion and generates accurate answers
- 📚 **Notion Integration**: Automatically syncs and indexes Notion databases
- 💬 **Telegram Bot**: Natural conversation interface
- 🎯 **Vector Search**: Fast semantic search using pgvector
- 📊 **Admin Panel**: Modern web interface to view and manage data
- 💰 **Cost Tracking**: Monitor OpenAI usage and costs
- ⭐ **User Feedback**: Track bot performance with user ratings
- 🚀 **Production Ready**: Async architecture, proper error handling, logging

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Telegram  │────▶│   FastAPI    │────▶│  PostgreSQL  │
│     Bot     │◀────│   Backend    │◀────│  + pgvector  │
└─────────────┘     └──────────────┘     └──────────────┘
                           │
                           │
                    ┌──────▼───────┐
                    │   Next.js    │
                    │   Frontend   │
                    └──────────────┘
                           │
                    ┌──────▼───────┐
                    │    Vercel    │
                    └──────────────┘
```
### Frontend (Next.js 15)
```

#### Страницы

1. **Dashboard (`/`)**
   - Статистика (документы, запросы, отзывы)
   - Последние 5 документов
   - Последние 5 запросов
   - Последние 5 отзывов
   - Процент удовлетворенности

2. **Documents (`/documents`)**
   - Список всех документов из Notion
   - Кнопки: Открыть в Notion, Просмотр, Удалить
   - Детальная страница документа с chunks

3. **Query Logs (`/query-logs`)**
   - Все запросы пользователей
   - Вопросы и ответы
   - Токены и стоимость
   - Время обработки
   - Кнопка удаления

4. **Feedback (`/feedback`)**
   - Все отзывы пользователей
   - Рейтинги (👍/👎)
   - Комментарии
   - Статистика удовлетворенности
   - Кнопка удаления

#### API Routes (Next.js)

Все роуты проксируют запросы к backend:

**Documents:**
- `GET /api/documents` - Список документов
- `GET /api/documents/[id]` - Один документ
- `PUT /api/documents/[id]` - Обновить документ
- `DELETE /api/documents/[id]` - Удалить документ

**Chunks:**
- `GET /api/chunks` - Список chunks
- `GET /api/chunks/[id]` - Один chunk
- `PUT /api/chunks/[id]` - Обновить chunk
- `DELETE /api/chunks/[id]` - Удалить chunk

**Query Logs:**
- `GET /api/query-logs` - Список логов
- `GET /api/query-logs/[id]` - Один лог
- `DELETE /api/query-logs/[id]` - Удалить лог

**Feedback:**
- `GET /api/feedback` - Список отзывов
- `GET /api/feedback/[id]` - Один отзыв
- `DELETE /api/feedback/[id]` - Удалить отзыв

#### Особенности

- ✅ Server-Side Rendering для быстрой загрузки
- ✅ TypeScript для type safety
- ✅ Реактивные компоненты с `"use client"`
- ✅ Простой CSS без зависимостей
- ✅ Современный дизайн
- ✅ Адаптивная верстка
- ✅ Готовность к Vercel деплою

### 2. Backend CRUD API

**Новый файл:** `app/crud_api.py`

#### Эндпоинты

**Documents:**
```python
GET    /api/documents              # Список всех документов
GET    /api/documents/{id}         # Один документ
PUT    /api/documents/{id}         # Обновить (title, url)
DELETE /api/documents/{id}         # Удалить (+ все chunks)
```

**Chunks:**
```python
GET    /api/chunks                      # Список chunks (limit=100)
GET    /api/chunks/document/{doc_id}    # Chunks одного документа
GET    /api/chunks/{id}                 # Один chunk
PUT    /api/chunks/{id}                 # Обновить (content, heading_path)
DELETE /api/chunks/{id}                 # Удалить
```

**Query Logs:**
```python
GET    /api/query-logs             # Список логов (optional limit)
GET    /api/query-logs/{id}        # Один лог
DELETE /api/query-logs/{id}        # Удалить
```

**Feedback:**
```python
GET    /api/feedback               # Список отзывов (optional limit)
GET    /api/feedback/{id}          # Один отзыв
DELETE /api/feedback/{id}          # Удалить
```

### Tech Stack

**Backend**:
- Python 3.13+
- FastAPI (async web framework)
- PostgreSQL + pgvector (vector database)
- OpenAI (embeddings + chat)
- Notion API (document sync)
- python-telegram-bot (bot framework)

**Frontend**:
- Next.js 15 (React framework)
- TypeScript
- Server-side rendering
- Modern CSS

### Public Endpoints

- `GET /health` - Health check
- `POST /query` - Ask a question
- `POST /feedback` - Submit feedback

### Admin Endpoints (require secret)

- `POST /admin/db-init` - Initialize database
- `POST /admin/ingest` - Sync Notion data
- `GET /admin/db-info` - View database info

### CRUD Endpoints

- `GET /api/documents` - List documents
- `GET /api/query-logs` - List query logs
- `GET /api/feedback` - List feedback
- `DELETE /api/documents/{id}` - Delete document
- `DELETE /api/query-logs/{id}` - Delete log
- `DELETE /api/feedback/{id}` - Delete feedback


## 📁 Project Structure

```
notiontgLLM/
├── app/                    # Backend application
│   ├── api.py             # Main API routes
│   ├── crud_api.py        # CRUD endpoints
│   ├── config.py          # Configuration
│   ├── db.py              # Database setup
│   ├── embeddings.py      # Embedding generation
│   ├── llm.py             # OpenAI integration
│   ├── models.py          # SQLAlchemy models
│   ├── notion_sync.py     # Notion synchronization
│   └── retrieval.py       # Vector search
├── bot/                   # Telegram bot
│   └── telegram.py        # Bot handlers
├── frontend/              # Next.js admin panel
│   ├── app/               # Pages and API routes
│   ├── lib/               # Utilities
│   └── types/             # TypeScript types
├── migrations/            # Database migrations
├── main.py               # FastAPI app
├── run.py                # Entry point
└── requirements.txt      # Python dependencies
```

## 🛠️ Development

### Run Tests

```bash
# Backend
pytest

# Frontend
cd frontend
npm test
```

### Code Quality

```bash
# Backend
black .
ruff check .

# Frontend
cd frontend
npm run lint
```

### Database Migrations

```bash
# Apply migrations
python init_db.py
```

## 📊 Monitoring

### View Logs

**Backend**:
- Local: Check console output
- Railway: View in dashboard

**Frontend**:
- Local: Check console output
- Vercel: View in dashboard

### Monitor Costs

Check admin panel for:
- Total tokens used
- Cost per query
- Total spending

### Database Stats

```bash
curl "http://localhost:8000/api/v1/admin/db-info?secret=YOUR_SECRET"
```

## 🔒 Security

- ✅ Webhook secret for admin endpoints
- ✅ Allowed user IDs for Telegram bot
- ✅ Environment variables for secrets
- ✅ CORS configuration
- ✅ SQL injection protection (SQLAlchemy)
- ✅ Input validation (Pydantic)

## 🐛 Troubleshooting

### Backend Issues

**Database connection fails**:
- Check `DATABASE_URL` format
- Verify pgvector extension is installed
- Check database is accessible

**Notion sync fails**:
- Verify `NOTION_TOKEN` is valid
- Check `NOTION_DATABASE_IDS` are correct
- Ensure bot has database access

**OpenAI errors**:
- Verify `OPENAI_API_KEY` is valid
- Check API usage limits
- Monitor costs

### Frontend Issues

**Can't connect to backend**:
- Verify `NEXT_PUBLIC_API_URL` is set
- Check CORS settings in backend
- Ensure backend is accessible

**Build fails on Vercel**:
- Check build logs in Vercel dashboard
- Verify all dependencies are listed
- Check TypeScript errors

## 📈 Performance

- **Response Time**: ~2-3 seconds per query
- **Concurrent Requests**: 100+ (async architecture)
- **Database**: Optimized with vector indexes
- **Caching**: FastAPI response caching
- **Frontend**: Server-side rendering for speed

- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [OpenAI](https://openai.com/)
- [Notion](https://www.notion.so/)
- [python-telegram-bot](https://python-telegram-bot.org/)
- [pgvector](https://github.com/pgvector/pgvector)