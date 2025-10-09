# Quick Start Guide

Get your Notion TG Admin Panel running in 5 minutes!

## Prerequisites

- Node.js 20+ installed
- Backend API running and accessible
- Backend URL (e.g., `http://localhost:8000` or `https://your-backend.railway.app`)

## Local Development

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

> If your backend is on Railway or another platform, use that URL instead.

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 4. Build for Production (Optional)

```bash
npm run build
npm start
```

## Deploy to Vercel (5 minutes)

### Method 1: Vercel CLI (Fastest)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL
# Enter your backend URL when prompted

# Deploy to production
vercel --prod
```

### Method 2: GitHub + Vercel Dashboard

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add frontend"
   git push
   ```

2. **Import to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your repository
   - Set root directory: `frontend`

3. **Configure**:
   - Add environment variable:
     - Key: `NEXT_PUBLIC_API_URL`
     - Value: Your backend URL (e.g., `https://your-backend.railway.app`)

4. **Deploy**:
   - Click "Deploy"
   - Wait 1-2 minutes
   - Done! 🎉

## Verify Everything Works

### 1. Check Backend Connection

Visit your Vercel URL, you should see:
- Dashboard with statistics
- Documents list (if you've synced Notion)
- Query logs (if bot received queries)

### 2. Test API Endpoints

The frontend should automatically fetch data from your backend. Check browser console for any errors.

### 3. Test Functionality

- ✅ View documents
- ✅ View query logs
- ✅ View feedback
- ✅ Delete records

## Troubleshooting

### Frontend shows "No documents yet"

✅ **Normal** - This means frontend is working but backend has no data.

**Solution**: Sync Notion data on backend:
```bash
curl -X POST "https://your-backend.railway.app/api/v1/admin/ingest?secret=YOUR_SECRET"
```

### Error: "Failed to fetch documents"

❌ Backend connection issue

**Solutions**:
1. Check backend is running:
   ```bash
   curl https://your-backend.railway.app/health
   ```

2. Verify `NEXT_PUBLIC_API_URL` in Vercel:
   - Go to Vercel dashboard
   - Click your project
   - Settings → Environment Variables
   - Check value is correct

3. Check CORS settings in backend (`main.py`):
   ```python
   allow_origins=["*"]  # Should allow all origins
   ```

### Pages not loading

❌ Build error

**Solution**: Check Vercel logs:
- Go to Vercel dashboard
- Click "Deployments"
- Click latest deployment
- Check build logs

## Update After Changes

### Update Frontend Code

```bash
# Local changes
git add .
git commit -m "Update frontend"
git push

# Vercel automatically redeploys
```

### Update Environment Variables

```bash
# Via CLI
vercel env add NEXT_PUBLIC_API_URL production

# Or via dashboard:
# Settings → Environment Variables → Edit
```

## Next Steps

- 🎨 Customize styles in `app/globals.css`
- 🔧 Add more features
- 📊 Add analytics
- 🔐 Add authentication (optional)

## Need Help?

Common issues and solutions are in the main README.md and DEPLOYMENT.md files.

## What You've Built

- ✅ Modern Next.js admin panel
- ✅ Real-time data from PostgreSQL
- ✅ CRUD operations
- ✅ Responsive design
- ✅ Fast server-side rendering
- ✅ Production-ready deployment

Enjoy your admin panel! 🎉

