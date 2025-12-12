# 🎯 Easy Run Options - Choose Your Way

## **⭐ EASIEST: One-Click GUI** 

### Windows
Double-click: **`launcher.py`**

### Mac/Linux
```bash
python3 launcher.py
```

**What you get:**
- Interactive window
- Auto-detects Docker
- Shows status
- One-click browser open

---

## **FAST: Smart Auto-Detection**

### Windows
Double-click: **`RUN.bat`**

### Mac/Linux
```bash
python3 setup-wizard.py
```

**What you get:**
- Checks what's installed
- Offers available options
- Automatic setup

---

## **SUPER SIMPLE: One Command**

### Docker (All-in-one)
```bash
docker-compose up
```

### Manual (Separate)
Terminal 1:
```bash
uvicorn app.main:app --reload
```

Terminal 2:
```bash
cd frontend && npm run dev
```

---

## **CUSTOM: Full Control**

### Windows Batch Scripts
- `START-DOCKER.bat` - Docker only
- `START-BACKEND.bat` - Backend only
- `START-FRONTEND.bat` - Frontend only

### Mac/Linux Shell Scripts
- `start-docker.sh` - Docker only
- `start-backend.sh` - Backend only
- `start-frontend.sh` - Frontend only

---

## 🚀 Quick Start Comparison

| Method | Setup Time | Requirements | Complexity |
|--------|-----------|--------------|-----------|
| **GUI Launcher** | <1 min | Python 3.6+ | ⭐ Easiest |
| **RUN.bat/setup-wizard.py** | 1-2 min | Python 3.6+ | ⭐⭐ Easy |
| **Docker Compose** | 2-5 min | Docker Desktop | ⭐⭐ Easy |
| **Manual Scripts** | 5-10 min | Node.js + Python | ⭐⭐⭐ Medium |

---

## 📍 After You Start

All methods open the same services:

| Service | URL | Purpose |
|---------|-----|---------|
| Web App | http://localhost:3000 | Interactive UI |
| API | http://localhost:8000 | Backend API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Database | localhost:5432 | PostgreSQL |

---

## 🎯 Recommended Startup Path

### If you have Docker:
1. Double-click `launcher.py` OR
2. Run `docker-compose up`

### If you don't have Docker:
1. Double-click `RUN.bat` OR
2. Run `python3 setup-wizard.py`

### For development:
```bash
# Terminal 1
uvicorn app.main:app --reload --port 8000

# Terminal 2
cd frontend && npm run dev
```

---

## ✅ What Gets Downloaded/Installed

### Docker Method
- Docker images (auto-downloaded on first run)
- Total size: ~1-2 GB
- Time: 5-10 minutes first run

### Manual Method
- Python packages (pip): ~500 MB
- Node modules (npm): ~800 MB
- Total size: ~1.3 GB
- Time: 10-20 minutes first run

---

## 🆘 Troubleshooting Quick Links

### "Command not found"
- Docker: https://docker.com/products/docker-desktop
- Python: https://python.org
- Node.js: https://nodejs.org

### "Port already in use"
```bash
# Change port in docker-compose.yml
# Or use:
uvicorn app.main:app --port 8001
```

### "Database connection failed"
- Docker: Wait 10 seconds for PostgreSQL
- Manual: Install PostgreSQL with PostGIS

---

## 📦 Downloadable Package Options

### Option 1: Windows Installer (Coming Soon)
- Single .exe file
- Auto-installs Docker
- One-click startup

### Option 2: Standalone Python Script
```bash
python3 launcher.py
```
Just requires Python 3.6+

### Option 3: Docker Image
```bash
docker run -p 3000:3000 -p 8000:8000 logistics-router
```

---

## 🎉 You're Ready!

Choose **ANY** of these methods and start using the application:

1. **Easiest**: Double-click `launcher.py`
2. **Smart**: Double-click `RUN.bat` (Windows) or run `setup-wizard.py`
3. **Quick**: `docker-compose up`
4. **Custom**: Use individual scripts

**All will get you to: http://localhost:3000** ✨