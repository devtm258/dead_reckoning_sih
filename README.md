# 🚀 SIH 2026 - ISRO Dead Reckoning Navigation System

**AI-Powered GPS-Denied Navigation** using Extended Kalman Filter (EKF) and Machine Learning velocity estimation.

## ✨ Key Features

- 📊 Real-time dead reckoning in GNSS-denied environments
- 🤖 ML-based velocity prediction (Random Forest + Ridge Regression)
- 🔍 Multi-sensor fusion (accelerometer, gyroscope, magnetometer)
- 📈 Real-time performance metrics and drift analysis
- 🧠 AI-powered insights using Claude API
- 📱 Responsive web dashboard

## 🎯 Quick Deploy (5 Minutes!)

```bash
# 1. Push to GitHub
git push origin main

# 2. Go to Vercel & Connect GitHub repo
# vercel.com/dashboard → Add Project

# 3. Add Environment Variables
# REACT_APP_API_URL=https://your-backend.fly.dev/api

# Done! ✅ Frontend is live!
```

→ **See [QUICKSTART.md](./QUICKSTART.md) for complete guide**

## 📦 Project Structure

```
├── frontend/          # React app → Deployed to Vercel
├── backend/           # FastAPI server → Deploy to Fly.io/Railway
├── data/              # Sample IMU datasets (CSV)
├── vercel.json        # Vercel configuration
├── railway.json       # Railway configuration
├── .env.example       # Environment template
├── QUICKSTART.md      # 5-min deployment guide
└── VERCEL_DEPLOYMENT.md # Complete guide
```

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React 19, Tailwind CSS, Shadcn UI |
| Backend | FastAPI, Python 3.11, Scikit-learn |
| Database | MongoDB Atlas |
| Deployment | Vercel + Fly.io |

## 🚀 Deployment Steps

### Frontend (Vercel)
1. Connect GitHub repo to Vercel
2. Set environment variables
3. Auto-deploys on git push

### Backend (Fly.io)
```bash
cd backend
flyctl launch
flyctl secrets set MONGO_URL="..."
flyctl deploy
```

→ [Full guide: VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md)

## 💻 Local Development

### Frontend
```bash
cd frontend
npm install
npm start
# http://localhost:3000
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn server:app --reload --port 3001
# http://localhost:3001/api/
```

## 🔌 API Endpoints

```
POST   /api/dataset/load-preset
POST   /api/dataset/upload
POST   /api/pipeline/train
POST   /api/pipeline/simulate
POST   /api/ai/summary
```

## 📖 Documentation

- **[QUICKSTART.md](./QUICKSTART.md)** - Get running in 5 minutes
- **[VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md)** - Complete deployment guide

## ✅ Pre-Deployment Checklist

- ✅ Removed Emergent dependencies
- ✅ Created Vercel configuration
- ✅ Added Dockerfile for backend
- ✅ Environment variable templates ready
- ✅ API structure verified
- ✅ CORS configured
- ✅ Documentation complete

## 🎯 Ready to Deploy?

1. **Start here**: [QUICKSTART.md](./QUICKSTART.md)
2. **Need details?**: [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md)

---

**Deploy with Vercel today! 🚀**
