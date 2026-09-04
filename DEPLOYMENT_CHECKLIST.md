# ✅ Pre-Deployment Verification Checklist

## 🧹 Cleanup & Setup

- [x] Removed `@emergentbase/visual-edits` dependency
- [x] Removed Emergent import from backend
- [x] Created `.env.example` template
- [x] Created `.gitignore` (prevents committing secrets)
- [x] Created `.vercelignore` (optimizes build)
- [x] Removed hardcoded environment variables

## 📝 Configuration Files

- [x] **vercel.json** - Vercel build configuration
  - Build command: `cd frontend && npm run build`
  - Output directory: `frontend/build`
  - Environment variables setup
  
- [x] **package.json** (root) - Monorepo configuration
  - Frontend workspace defined
  - Node 18+ required
  
- [x] **backend/Dockerfile** - Container for backend
  - Python 3.11 slim image
  - Gunicorn + Uvicorn for production
  - Health check configured
  
- [x] **backend/fly.toml** - Fly.io deployment config
  - Correct port: 8000
  - Health check endpoint: /api/
  
- [x] **railway.json** - Railway.app config
  - Dockerfile-based build

## 🔐 Security

- [x] `.env` files ignored in `.gitignore`
- [x] `.env.example` provides template (no secrets)
- [x] Backend secrets stored in:
  - Fly.io: `flyctl secrets set`
  - Railway: Dashboard environment variables
  - Vercel: Dashboard environment variables
- [x] No hardcoded API keys in code
- [x] CORS configured for production domains

## 🔗 API Integration

- [x] Frontend API client (`frontend/src/lib/api.js`)
  - Uses `REACT_APP_API_URL` environment variable
  - Falls back to `localhost:3001` for development
  
- [x] Backend CORS middleware
  - Configured to accept `CORS_ORIGINS` from environment
  - Allows credentials for authentication

## 📦 Dependencies

- [x] `requirements.txt` updated with:
  - `gunicorn==22.0.0` (production WSGI server)
  - All FastAPI dependencies
  - All ML dependencies (scikit-learn, pandas, numpy)

- [x] `frontend/package.json` cleaned
  - Removed Emergent visual-edits
  - All other dependencies intact
  - Production-ready versions

## 🚀 Deployment-Specific

- [x] **Vercel Frontend**
  - `vercel.json` configured
  - Build command tested locally: `npm run build`
  - Environment variables template provided
  
- [x] **Fly.io Backend**
  - `fly.toml` configured
  - Dockerfile multi-stage optimized
  - Health checks configured
  
- [x] **Railway Backend** (alternative)
  - `railway.json` configured
  - Dockerfile ready
  
- [x] **Database**
  - MongoDB connection via `MONGO_URL`
  - Atlas cloud ready
  - Local MongoDB support

## 📋 Documentation

- [x] **README.md** - Project overview
  - Quick deploy guide
  - Tech stack
  - Local development setup
  
- [x] **QUICKSTART.md** - 5-minute deployment
  - Step-by-step deployment
  - Environment variable setup
  - Verification steps
  
- [x] **VERCEL_DEPLOYMENT.md** - Complete guide
  - All deployment options
  - Troubleshooting
  - Security considerations
  
- [x] **DEPLOYMENT_CHECKLIST.md** (this file)
  - Verification for each step

## 🔍 Verification Steps (Before Deployment)

### Local Frontend Build
```bash
cd frontend
npm install
npm run build
# Should create frontend/build/ directory
```

### Local Backend Test
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn server:app --port 8000
# Should respond to: curl http://localhost:8000/api/
```

### Environment Configuration
```bash
# Create .env.local in frontend
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENVIRONMENT=development

# Create .env in backend
MONGO_URL=mongodb://localhost:27017
DB_NAME=sih_dr_navigation
CORS_ORIGINS=localhost:3000,localhost:3001
```

## 🎯 Deployment Path

### Path 1: Vercel + Fly.io (Recommended)

1. **Frontend on Vercel**
   ```
   GitHub → Vercel → Auto-deploy on push ✓
   ```
   
2. **Backend on Fly.io**
   ```
   git push → flyctl deploy ✓
   ```
   
3. **Connect**
   ```
   Set REACT_APP_API_URL in Vercel env vars ✓
   ```

### Path 2: Vercel + Railway

1. **Frontend on Vercel** (same as Path 1)
2. **Backend on Railway** (connect GitHub in Railway dashboard)
3. **Connect** (update REACT_APP_API_URL)

## 📊 Pre-Flight Checklist

Before clicking "Deploy":

- [ ] All files pushed to GitHub
- [ ] `vercel.json` present in root
- [ ] `package.json` present in root
- [ ] Frontend builds locally: `npm run build`
- [ ] Backend tests locally: `python -m uvicorn server:app`
- [ ] `.env.example` created with all required variables
- [ ] No `.env` file in git (check `.gitignore`)
- [ ] Backend `requirements.txt` includes `gunicorn`
- [ ] `REACT_APP_API_URL` is configurable per environment
- [ ] Backend CORS allows Vercel domain
- [ ] MongoDB connection string ready (Atlas or local)

## ⚡ Performance Optimization

- [x] `.vercelignore` excludes backend & data files
  - Reduces build time
  - Reduces bundle size
  
- [x] Frontend build optimization
  - Craco configuration for fast builds
  - Tailwind CSS purging enabled
  
- [x] Backend Dockerfile
  - Multi-stage build (implied by slim image)
  - Production-ready with gunicorn

## 🔒 Security Checklist

- [x] No secrets in code
- [x] No hardcoded API keys
- [x] Environment variables templated
- [x] CORS properly configured
- [x] Backend validates input
- [x] `.gitignore` prevents secret leaks
- [x] MongoDB authentication required in production
- [x] HTTPS enforced (Vercel & Fly.io both support)

## 📞 Post-Deployment

After deployment:

- [ ] Test frontend: `https://your-app.vercel.app`
- [ ] Test backend: `https://your-api.fly.dev/api/`
- [ ] Test API call: Load preset dataset
- [ ] Monitor logs: Vercel Dashboard & Fly.io Dashboard
- [ ] Set up error tracking (optional)
- [ ] Configure monitoring alerts (optional)

## 🎉 Success Criteria

When deployed correctly, you should see:

✅ Frontend loads at `https://your-app.vercel.app`  
✅ Dashboard displays without errors  
✅ "Load Preset Dataset" button works  
✅ Data loads from backend API  
✅ No CORS errors in console  
✅ Training & simulation work end-to-end  

## 📞 Troubleshooting

See [VERCEL_DEPLOYMENT.md - Common Issues](./VERCEL_DEPLOYMENT.md#-common-issues)

---

**Ready to deploy? Follow the [QUICKSTART.md](./QUICKSTART.md)!** 🚀

