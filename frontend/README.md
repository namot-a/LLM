# Notion TG Frontend

Modern admin panel for Notion Telegram Bot built with Next.js 15.

## Features

- 📊 Dashboard with statistics
- 📄 View and manage documents from Notion
- 💬 View query logs with token usage and costs
- ⭐ View user feedback
- 🗑️ Delete records with one click
- ⚡ Server-side rendering for fast performance
- 🎨 Clean and modern UI

## Tech Stack

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety
- **CSS** - Simple styling without external dependencies

## Getting Started

### Prerequisites

- Node.js 20+
- Backend API running (FastAPI)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Configure environment variables:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
API_URL=http://localhost:8000
```

> **Note:** `NEXT_PUBLIC_API_URL` is used for client-side requests, `API_URL` is used for server-side requests.

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

## Deployment to Vercel

### Option 1: Deploy via Vercel CLI

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. Set environment variables in Vercel dashboard:
   - Go to your project settings
   - Navigate to "Environment Variables"
   - Add:
     - `NEXT_PUBLIC_API_URL` - Your backend URL (e.g., `https://api.yourdomain.com`)
     - `API_URL` - Same as above

### Option 2: Deploy via Vercel Dashboard

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Import your repository
5. Set the root directory to `frontend`
6. Add environment variables:
   - `NEXT_PUBLIC_API_URL`
   - `API_URL`
7. Click "Deploy"

### Important Notes for Vercel Deployment

- Make sure your backend API has CORS configured to allow requests from your Vercel domain
- Environment variables must be set before deployment
- The backend API should be accessible from the internet
- Use production backend URL (not localhost)

## Project Structure

```
frontend/
├── app/
│   ├── api/              # API route handlers (proxy to backend)
│   │   ├── documents/
│   │   ├── chunks/
│   │   ├── query-logs/
│   │   └── feedback/
│   ├── documents/        # Documents page
│   ├── query-logs/       # Query logs page
│   ├── feedback/         # Feedback page
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Home page
│   └── globals.css       # Global styles
├── lib/
│   └── api.ts            # API client functions
├── types/
│   └── index.ts          # TypeScript types
├── package.json
├── tsconfig.json
├── next.config.ts
└── vercel.json           # Vercel configuration
```

## API Endpoints

The frontend communicates with the backend through Next.js API routes:

- `GET /api/documents` - List all documents
- `GET /api/documents/[id]` - Get document by ID
- `DELETE /api/documents/[id]` - Delete document
- `PUT /api/documents/[id]` - Update document
- `GET /api/chunks` - List all chunks
- `GET /api/chunks/[id]` - Get chunk by ID
- `DELETE /api/chunks/[id]` - Delete chunk
- `PUT /api/chunks/[id]` - Update chunk
- `GET /api/query-logs` - List all query logs
- `GET /api/query-logs/[id]` - Get query log by ID
- `DELETE /api/query-logs/[id]` - Delete query log
- `GET /api/feedback` - List all feedback
- `GET /api/feedback/[id]` - Get feedback by ID
- `DELETE /api/feedback/[id]` - Delete feedback

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL (client-side) | `http://localhost:8000` |
| `API_URL` | Backend API URL (server-side) | `http://localhost:8000` |

## Pages

### Dashboard (`/`)
- Overview statistics
- Recent documents
- Recent queries
- Recent feedback

### Documents (`/documents`)
- List all documents
- Delete documents
- View document details
- Open in Notion

### Query Logs (`/query-logs`)
- List all queries
- View token usage
- View costs
- Delete logs

### Feedback (`/feedback`)
- List all feedback
- View satisfaction rate
- Delete feedback

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT

