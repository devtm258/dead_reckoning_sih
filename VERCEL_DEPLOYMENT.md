# Vercel Deployment Guide - SIH 2026 Dead Reckoning System

This guide explains how to deploy this full-stack application to Vercel.

## 📋 Project Structure

```
├── frontend/              # React app (deployed to Vercel)
├── backend/              # FastAPI Python service (deploy separately)
├── vercel.json           # Vercel configuration
├── package.json          # Root configuration
└── .env.example          # Environment variables template
```

## 🚀 Deployment Strategy

Since Vercel is primarily a **frontend-first platform**, here are your options:

### **Option 1: Frontend-Only on Vercel (Recommended for MVP)**
- Deploy **React frontend** to Vercel ✅
- Deploy **Python backend** to a separate service (Fly.io, Railway, Render, Heroku)
- Frontend calls backend via API URL

### **Option 2: Full Vercel with Serverless Functions**
- Deploy frontend to Vercel ✅
- Use Vercel Serverless Functions (Node.js) for simple proxy/API routes ✅
- Python backend still runs separately but behind authentication

## 🔧 Frontend Deployment to Vercel

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Prepare the Project
```bash
cd VERCEL_READY
vercel login
```

### Step 3: Deploy
```bash
vercel --prod
```

Or use GitHub integration:
1. Push code to GitHub
2. Connect repository to Vercel dashboard
3. Vercel auto-deploys on push

### Step 4: Configure Environment Variables

In Vercel Dashboard → Project Settings → Environment Variables:

```
REACT_APP_API_URL=https://your-backend-api.com/api
REACT_APP_ENVIRONMENT=production
```

**Note**: Environment variables in Vercel must be prefixed with `REACT_APP_` to be accessible in React.

## 🐍 Backend Deployment Options

### Option A: Deploy to Fly.io (Recommended)

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# From backend directory
cd backend

# Initialize Fly app
flyctl launch --name "sih-dr-backend"

# Set environment variables
flyctl secrets set MONGO_URL="mongodb+srv://..."
flyctl secrets set DB_NAME="sih_dr_navigation"
flyctl secrets set CORS_ORIGINS="your-vercel-frontend-url.vercel.app"

# Deploy
flyctl deploy
```

### Option B: Deploy to Railway.app

1. Connect GitHub repo to Railway
2. Create MongoDB database in Railway
3. Set environment variables in Railway dashboard
4. Railway auto-deploys

### Option C: Deploy to Render

1. Connect GitHub repo
2. Create new "Web Service"
3. Set start command: `uvicorn backend.server:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

## 📦 Building Frontend for Vercel

The `vercel.json` configuration handles:
- **Build Command**: `npm run build` in frontend directory
- **Output Directory**: `frontend/build`
- **Environment Variables**: Automatically prefixed with `REACT_APP_`

### Build Process
```bash
# Vercel runs this automatically
cd frontend && npm run build
```

The built frontend is deployed to Vercel's CDN.

## 🔌 Connecting Frontend to Backend

### In `frontend/src/lib/api.js`:

```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

export const apiClient = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});
```

### Example API call:
```javascript
// This will hit: https://your-backend-api.com/api/dataset/load-preset
const response = await apiClient.post('/dataset/load-preset');
```

## 🗄️ Database (MongoDB)

### Option 1: MongoDB Atlas (Cloud)
```
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/sih_dr_navigation
```

### Option 2: MongoDB in Railway/Fly
Services handle database provisioning automatically.

## ✅ Deployment Checklist

- [ ] Remove all Emergent dependencies ✓
- [ ] Create `.env.example` ✓
- [ ] Create `vercel.json` ✓
- [ ] Update `REACT_APP_API_URL` environment variable
- [ ] Configure CORS in backend to allow Vercel domain
- [ ] Deploy frontend to Vercel
- [ ] Deploy backend to Fly.io/Railway/Render
- [ ] Test API connectivity
- [ ] Set up monitoring/logging

## 🔐 Security Considerations

1. **Never commit `.env` files** - Use `.gitignore` ✓
2. **Store secrets in Vercel/Railway/Fly dashboard**, not in code
3. **CORS Configuration**: 
   ```python
   CORS_ORIGINS=your-vercel-url.vercel.app,localhost:3000
   ```
4. **API Keys**: Store LLM keys in backend secrets only

## 🚨 Common Issues

### Issue: "Module not found: @emergentbase/visual-edits"
**Solution**: Already removed from package.json ✓

### Issue: "REACT_APP_API_URL is undefined"
**Solution**: 
- Add to Vercel environment variables
- Must be prefixed with `REACT_APP_`
- Redeploy after adding

### Issue: "CORS error when calling API"
**Solution**:
```python
# In backend/server.py
CORS_ORIGINS=os.environ.get("CORS_ORIGINS", "https://your-vercel-app.vercel.app")
```

### Issue: "Backend times out on Vercel"
**Solution**: Backend runs on separate service (Fly/Railway), not Vercel

## 📊 Monitoring & Logs

### Vercel
- Dashboard → Logs → Function Logs
- Frontend runtime errors are logged

### Backend (Fly.io example)
```bash
flyctl logs
```

### Backend (Railway)
- Dashboard → Project → Logs

## 🔄 CI/CD Pipeline

Once deployed:

1. Push to GitHub
2. Vercel auto-detects changes
3. Runs build command: `cd frontend && npm run build`
4. Deploys to Vercel CDN
5. Backend (separate service) deploys independently

## 📝 Final Notes

- **Vercel is optimized for static/serverless deployments**
- **Python backend needs a separate container/service**
- **This separation is a best practice** for scalability and maintenance
- **Environment variables are project-level** (frontend) and **service-level** (backend)

## 🆘 Support Resources

- Vercel Docs: https://vercel.com/docs
- Fly.io Docs: https://fly.io/docs/
- Railway Docs: https://docs.railway.app/
- Next.js Guide: https://nextjs.org/learn (if migrating from CRA)

---

**Deploy with confidence! 🚀**
