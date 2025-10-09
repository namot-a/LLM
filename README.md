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

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL 12+ with pgvector extension
- Node.js 20+
- Telegram Bot Token
- Notion API Token
- OpenAI API Key

### 1. Backend Setup

```bash
# Clone repository
git clone <your-repo>
cd notiontgLLM

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run backend
python run.py
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with backend URL

# Run development server
npm run dev
```

Visit:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

## 📦 Deployment

### Backend → Railway/Render

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

Quick deploy to Railway:
```bash
railway login
railway init
railway up
```

### Frontend → Vercel

See [frontend/QUICKSTART.md](frontend/QUICKSTART.md) for detailed instructions.

Quick deploy to Vercel:
```bash
cd frontend
vercel login
vercel --prod
```

## 🔧 Configuration

### Environment Variables

#### Backend (`.env`)

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
ALLOWED_TELEGRAM_USER_IDS=123456789,987654321
WEBHOOK_SECRET_PATH=your_webhook_secret

# Notion
NOTION_TOKEN=secret_...
NOTION_DATABASE_IDS=database_id_1,database_id_2

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# API Settings
API_URL=https://your-backend-url.railway.app
HOST=0.0.0.0
PORT=8000
```

#### Frontend (`frontend/.env`)

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
API_URL=https://your-backend-url.railway.app
```

## 📚 API Endpoints

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

See [API documentation](http://localhost:8000/docs) for full details.

## 🎯 Usage

### 1. Sync Notion Data

```bash
curl -X POST "http://localhost:8000/api/v1/admin/ingest?secret=YOUR_SECRET"
```

### 2. Ask Questions via Telegram

Open your bot in Telegram:
```
/start
What is the deployment process?
```

### 3. View Data in Admin Panel

Open http://localhost:3000 to see:
- 📊 Dashboard with statistics
- 📄 Documents from Notion
- 💬 Query logs with costs
- ⭐ User feedback

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

## 💡 Features Roadmap

- [ ] Multi-language support
- [ ] Voice message support
- [ ] Image processing
- [ ] Advanced analytics
- [ ] Rate limiting
- [ ] User authentication for admin panel
- [ ] Scheduled Notion syncs
- [ ] Export data functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [OpenAI](https://openai.com/)
- [Notion](https://www.notion.so/)
- [python-telegram-bot](https://python-telegram-bot.org/)
- [pgvector](https://github.com/pgvector/pgvector)

## 📞 Support

For issues and questions:
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
- Check [frontend/QUICKSTART.md](frontend/QUICKSTART.md) for frontend help
- Open an issue on GitHub

---

Made with ❤️ for better documentation access

