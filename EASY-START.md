# 🚀 Easy Start Guide

Choose your preferred way to run the application:

## Option 1: GUI Launcher (Easiest) ⭐

### Windows
Double-click: **`launcher.py`**
- A window appears
- Click "▶ Start"
- Click "🌐 Open App"
- Done!

### Mac/Linux
```bash
python3 launcher.py
```

---

## Option 2: One-Click Scripts

### Windows 🪟

**With Docker** (Recommended):
```
Double-click: START-DOCKER.bat
```

**Without Docker** (Manual setup):
```
Double-click: START-BACKEND.bat
(then in another terminal)
Double-click: START-FRONTEND.bat
```

### Mac/Linux 🍎🐧

**With Docker** (Recommended):
```bash
chmod +x start-docker.sh
./start-docker.sh
```

**Without Docker** (Manual setup):
```bash
chmod +x start-backend.sh start-frontend.sh
./start-backend.sh  # In one terminal
./start-frontend.sh # In another terminal
```

---

## Option 3: Manual Commands

### Docker Way (All-in-one)
```bash
docker-compose up
```

### Manual Way (Separate processes)

Terminal 1 - Backend:
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm install
npm run dev
```

---

## What You Get After Startup

| Component | URL | Purpose |
|-----------|-----|---------|
| **Web App** | http://localhost:3000 | Interactive map & routing UI |
| **API Docs** | http://localhost:8000/docs | Test endpoints |
| **API** | http://localhost:8000 | Backend server |
| **Database** | localhost:5432 | PostgreSQL (internal) |

---

## 🎯 Quick Test

After startup, open your browser and:

1. **Visit**: http://localhost:3000
2. **Select**: Transport mode (Ocean/Air/Road/Rail)
3. **Pick**: Carrier model
4. **Click map**: Origin & destination
5. **Click**: "Compute Plan"
6. **See**: Route optimization results!

---

## 📋 Prerequisites by Mode

### Docker Mode ✅
- Docker Desktop installed
  - Download: https://www.docker.com/products/docker-desktop
- That's it!

### Manual Mode
- Python 3.11+
  - Download: https://www.python.org/
- Node.js 18+
  - Download: https://nodejs.org/
- PostgreSQL 15 + PostGIS
  - Download: https://www.postgresql.org/
  - Install PostGIS extension

---

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yml
# Or use different port:
uvicorn app.main:app --port 8001
```

### Docker Won't Start
```bash
# Check if Docker daemon is running
docker ps

# Or restart Docker Desktop
```

### npm command not found
- Node.js not installed
- Download from: https://nodejs.org/

### Python module not found
```bash
pip install -r requirements.txt
```

### Database connection error
- PostgreSQL not running (manual mode)
- Wait 10 seconds for Docker to start DB

---

## 🎉 Success!

You now have:
- ✅ Multi-modal logistics routing
- ✅ Interactive map interface
- ✅ API with auto-documentation
- ✅ Production-ready code
- ✅ Easy setup options

**Choose your launcher above and get started!**