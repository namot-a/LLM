# Deployment Guide

This guide covers deployment of both backend (FastAPI) and frontend (Next.js) components.

## Architecture

- **Backend**: FastAPI + PostgreSQL (with pgvector) - deployed on Railway/Render/any platform
- **Frontend**: Next.js 15 - deployed on Vercel

## Backend Deployment

### Prerequisites

- PostgreSQL database with pgvector extension
- Environment variables configured

### Deploy to Railway

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login:
```bash
railway login
```

3. Initialize project:
```bash
railway init
```

4. Set environment variables:
```bash
railway variables set TELEGRAM_BOT_TOKEN="your-token"
railway variables set ALLOWED_TELEGRAM_USER_IDS="123456789"
railway variables set WEBHOOK_SECRET_PATH="your-secret"
railway variables set NOTION_TOKEN="your-token"
railway variables set NOTION_DATABASE_IDS="database-id-1,database-id-2"
railway variables set OPENAI_API_KEY="your-key"
railway variables set DATABASE_URL="postgresql://..."
```

5. Deploy:
```bash
railway up
```

### Required Environment Variables

#### Backend

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

# Retrieval
TOP_K=6
SIMILARITY_THRESHOLD=0.25
MAX_CONTEXT_CHARS=12000

# Pricing (per 1K tokens)
PRICE_PROMPT_PER_1K=0.005
PRICE_COMPLETION_PER_1K=0.015
```

## Frontend Deployment to Vercel

### Option 1: Deploy via Vercel CLI

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Navigate to frontend directory:
```bash
cd frontend
```

3. Login to Vercel:
```bash
vercel login
```

4. Deploy:
```bash
vercel
```

5. For production:
```bash
vercel --prod
```

### Option 2: Deploy via Vercel Dashboard

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Import your repository
5. Configure project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

6. Add environment variables:
   - `NEXT_PUBLIC_API_URL`: Your backend URL (e.g., `https://your-backend.railway.app`)
   - `API_URL`: Same as above

7. Click "Deploy"

### Environment Variables for Frontend

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
API_URL=https://your-backend-url.railway.app
```

## Post-Deployment Steps

### 1. Initialize Database

Run the database initialization endpoint:

```bash
curl -X POST "https://your-backend-url.railway.app/api/v1/admin/db-init?secret=YOUR_WEBHOOK_SECRET"
```

### 2. Sync Notion Data

Trigger initial Notion sync:

```bash
curl -X POST "https://your-backend-url.railway.app/api/v1/admin/ingest?secret=YOUR_WEBHOOK_SECRET"
```

### 3. Set Telegram Webhook

The webhook is automatically set on backend startup, but you can verify:

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

### 4. Test the Bot

Send a message to your Telegram bot:
```
/start
```

### 5. Access Admin Panel

Open your Vercel URL in browser:
```
https://your-app.vercel.app
```

## CORS Configuration

The backend allows all origins by default. For production, update in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app"],  # Specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Database Setup

### PostgreSQL with pgvector

If using Railway:
1. Add PostgreSQL plugin
2. The extension will be created automatically via `/admin/db-init`

If using external database:
1. Ensure PostgreSQL 12+ with pgvector extension
2. Connect and run:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Monitoring

### Backend Health Check

```bash
curl https://your-backend-url.railway.app/health
```

### Frontend Health Check

```bash
curl https://your-app.vercel.app
```

### Database Info

```bash
curl "https://your-backend-url.railway.app/api/v1/admin/db-info?secret=YOUR_WEBHOOK_SECRET"
```

## Troubleshooting

### Backend not receiving webhook

1. Check webhook is set:
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

2. Check logs in Railway/Render dashboard

3. Verify webhook secret matches

### Frontend can't connect to backend

1. Check CORS settings
2. Verify `NEXT_PUBLIC_API_URL` environment variable
3. Check backend is accessible from internet
4. Check browser console for errors

### Database connection issues

1. Verify `DATABASE_URL` format
2. Check database is accessible from backend
3. Ensure pgvector extension is installed
4. Check connection limits

### Notion sync fails

1. Verify `NOTION_TOKEN` is valid
2. Check `NOTION_DATABASE_IDS` are correct
3. Ensure bot has access to databases
4. Check Notion API limits

## Security Best Practices

1. **Never commit `.env` files**
2. **Use strong webhook secrets**
3. **Restrict CORS origins in production**
4. **Limit database access by IP if possible**
5. **Use HTTPS for all connections**
6. **Regularly rotate API keys**
7. **Monitor usage and costs**

## Cost Optimization

### Backend
- Use Railway's free tier for development
- Monitor database size
- Set up automatic backups

### Frontend
- Vercel's free tier is sufficient for small projects
- Enable ISR for better caching
- Optimize images

### OpenAI
- Monitor token usage in admin panel
- Use cheaper models when possible (gpt-4o-mini)
- Implement rate limiting

## Maintenance

### Regular Tasks

1. **Monitor costs** (check admin panel)
2. **Sync Notion data** (run weekly or use cron)
3. **Check logs** (for errors)
4. **Update dependencies** (monthly)
5. **Backup database** (automated)

### Updates

#### Update Backend
```bash
git pull
railway up
```

#### Update Frontend
```bash
cd frontend
git pull
vercel --prod
```

## Support

For issues:
1. Check logs in Railway/Vercel dashboard
2. Review environment variables
3. Test API endpoints manually
4. Check database connections
5. Verify external services (Telegram, Notion, OpenAI)

## Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Notion API](https://developers.notion.com)

