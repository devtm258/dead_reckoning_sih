# Quick Start Guide - SIH 2026 Dead Reckoning Navigation System

## 🎯 What is This?

AI-powered dead reckoning system for GNSS-denied environments using IMU sensor fusion with Extended Kalman Filter.

**Tech Stack:**
- **Frontend**: React 19 + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI + Python + Scikit-learn
- **Database**: MongoDB
- **Deployment**: Vercel (frontend) + Fly.io/Railway (backend)

---

## 🚀 Quick Deployment to Vercel

### Prerequisites
```bash
- Node.js 18+
- Git + GitHub account
- Vercel account (free at vercel.com)
```

### 3-Step Deployment

#### Step 1: Prepare Code
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/your-repo.git
git branch -M main
git push -u origin main
```

#### Step 2: Connect to Vercel
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. **Keep default settings** (Vercel auto-detects Next.js/React)

#### Step 3: Set Environment Variables
In Vercel Dashboard:
1. Go to Project Settings → Environment Variables
2. Add:
   ```
   REACT_APP_API_URL=http://localhost:3001/api
   REACT_APP_ENVIRONMENT=production
   ```
3. Click Deploy

**Done! Your frontend is live on Vercel! 🎉**

---

## 💻 Local Development

### Setup

```bash
# Install frontend dependencies
cd frontend
npm install

# Create .env.local in frontend directory
REACT_APP_API_URL=http://localhost:3001/api
REACT_APP_ENVIRONMENT=development
```

### Run Development Server

```bash
# Terminal 1: Start React frontend
cd frontend
npm start
# Opens http://localhost:3000

# Terminal 2: Start Python backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create backend/.env
MONGO_URL=mongodb://localhost:27017
DB_NAME=sih_dr_navigation
CORS_ORIGINS=localhost:3000,localhost:3001

# Start backend
uvicorn server:app --reload --port 3001
# Backend runs at http://localhost:3001
```

### Test Everything Works
```bash
# Frontend should be at http://localhost:3000
# Backend API at http://localhost:3001/api/
# Load preset dataset and train model
```

---

## 🌍 Deploy Backend (Choose One)

### Option A: Fly.io (Easiest)

```bash
# Install Fly CLI: https://fly.io/docs/getting-started/

cd backend

# Create Fly app
flyctl launch --name my-dr-backend

# Set secrets
flyctl secrets set MONGO_URL="your-mongodb-url"
flyctl secrets set DB_NAME="sih_dr_navigation"
flyctl secrets set CORS_ORIGINS="your-vercel-frontend-url.vercel.app,localhost:3000"

# Deploy
flyctl deploy
```

### Option B: Railway.app

1. Connect GitHub repo to Railway
2. Create new environment
3. Add MongoDB database
4. Set environment variables
5. Done! (auto-deploys on push)

### Option C: Render.com

1. Create new "Web Service"
2. Connect GitHub repo
3. Runtime: Python 3.11
4. Start command: `pip install -r requirements.txt && uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

---

## 🔗 Connect Frontend to Deployed Backend

After backend is deployed (e.g., to `my-dr-backend.fly.dev`):

### Update Vercel Environment

1. Go to Vercel Dashboard → Project Settings
2. Update `REACT_APP_API_URL`:
   ```
   https://my-dr-backend.fly.dev/api
   ```
3. Redeploy (or it auto-redeploys on commit)

### That's it! Frontend and backend are now connected! 🔗

---

## 📁 File Structure

```
├── frontend/                    # React app
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── pages/             # Page components
│   │   ├── lib/api.js         # API client (update REACT_APP_API_URL here)
│   │   └── App.js
│   ├── package.json
│   └── .env.local             # Local env variables
│
├── backend/                    # Python FastAPI
│   ├── server.py             # Main API
│   ├── pipeline.py           # ML pipeline
│   ├── requirements.txt       # Dependencies
│   └── .env                  # Backend secrets (don't commit!)
│
├── vercel.json               # Vercel configuration
├── package.json              # Root config
└── VERCEL_DEPLOYMENT.md     # Full deployment guide
```

---

## 🎮 Using the Dashboard

1. **Load Dataset**: Click "Load Preset Dataset" to load sample IMU data
2. **View Sensors**: See accelerometer, gyroscope, magnetometer time-series
3. **Train Model**: Click "Train Velocity Model" to fit ML predictor
4. **Simulate**: Define GPS blackout window, run dead-reckoning simulation
5. **Analyze Results**: Compare INS-only vs ML+EKF fused performance

---

## 🔧 Troubleshooting

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Backend connection fails
```bash
# Check backend is running
curl http://localhost:3001/api/

# Check CORS settings
# Must include frontend URL in CORS_ORIGINS
```

### MongoDB connection error
```bash
# Start MongoDB locally
mongod

# Or use MongoDB Atlas (cloud):
# MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/dbname
```

### Vercel build fails
- Check `vercel.json` syntax
- Ensure Node.js 18+ is selected
- Check build logs: Dashboard → Deployments → Logs

---

## 📚 Resources

- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev
- **Fly.io Guide**: https://fly.io/docs/getting-started
- **MongoDB Atlas**: https://www.mongodb.com/cloud/atlas

---

## 🎯 Next Steps

1. ✅ Deploy frontend to Vercel (3 minutes)
2. ✅ Deploy backend to Fly.io/Railway (5 minutes)
3. ✅ Connect frontend to backend
4. ✅ Upload your own IMU data
5. ✅ Train models with your data
6. ✅ Monitor performance metrics

---

**Questions? Check VERCEL_DEPLOYMENT.md for detailed guide!** 📖

