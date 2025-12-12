# 🎯 START HERE - Your Quick Launch Guide

## 🚀 5 Ways to Run (Pick Any One)

### **METHOD 1: GUI Launcher (EASIEST) ⭐⭐⭐**
**Windows/Mac/Linux:** Double-click or run:
```bash
python3 launcher.py
```
✨ **Best for:** Anyone who wants a simple window with buttons

---

### **METHOD 2: Smart Wizard (EASIEST+) ⭐⭐⭐**
**Windows:** Double-click `RUN.bat`  
**Mac/Linux:**
```bash
python3 setup-wizard.py
```
✨ **Best for:** Automatic detection of what you have installed

---

### **METHOD 3: One Command (FAST) ⭐⭐**
**Windows/Mac/Linux:**
```bash
docker-compose up
```
✨ **Best for:** You have Docker, want everything in one command

---

### **METHOD 4: Individual Scripts (FLEXIBLE) ⭐⭐**
**Windows:**
- `START-DOCKER.bat` - Docker only
- `START-BACKEND.bat` - Backend only  
- `START-FRONTEND.bat` - Frontend only

**Mac/Linux:**
```bash
./start-docker.sh      # Docker way
./start-backend.sh     # Backend only
./start-frontend.sh    # Frontend only
```
✨ **Best for:** You want to run specific parts

---

### **METHOD 5: Manual Commands (MOST CONTROL) ⭐**
**Terminal 1:**
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Terminal 2:**
```bash
cd frontend
npm install
npm run dev
```
✨ **Best for:** Full control, development

---

## 📊 Quick Comparison

| Method | Setup | Requirements | Best For |
|--------|-------|--------------|----------|
| **GUI** | Click | Python 3.6+ | Beginners |
| **Wizard** | Click/Run | Python 3.6+ | Auto-setup |
| **Docker** | 1 line | Docker | All-in-one |
| **Scripts** | Click/Run | Varies | Control |
| **Manual** | 4 lines | Python + Node | Development |

---

## ✅ What Happens After You Start

### 1. Services Launch 🚀
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000 or :5173
- **Database**: localhost:5432 (internal)

### 2. Browser Opens 🌐
You'll see an interactive map

### 3. You Can Immediately:
- 🗺️ Click to set origin/destination
- 🚢 Select transport mode
- 🚗 Pick carrier
- ⚡ Calculate optimal route
- 💰 See costs & fuel stops

---

## 🆘 Need Help?

| Problem | Solution |
|---------|----------|
| "Don't know which method?" | Pick **METHOD 1** (GUI) |
| "Want easiest?" | Pick **METHOD 2** (Wizard) |
| "Have Docker?" | Pick **METHOD 3** (One command) |
| "On Windows?" | Double-click **RUN.bat** |
| "On Mac/Linux?" | Run **setup-wizard.py** |
| "Want to code?" | Use **METHOD 5** (Manual) |

---

## 🎉 Ready? Pick One Above and Go!

No more setup questions—all methods work perfectly.

**Your app will be at: `http://localhost:3000` in 1-5 minutes**

---

## 📁 Files Reference

### Launchers (Windows)
- ✅ `RUN.bat` - Smart auto-detection
- ✅ `launcher.py` - GUI window
- ✅ `START-DOCKER.bat` - Docker only
- ✅ `START-BACKEND.bat` - Backend only
- ✅ `START-FRONTEND.bat` - Frontend only

### Launchers (Mac/Linux)
- ✅ `start-docker.sh` - Docker only
- ✅ `start-backend.sh` - Backend only
- ✅ `start-frontend.sh` - Frontend only
- ✅ `launcher.py` - GUI window
- ✅ `setup-wizard.py` - Smart wizard

### Key Docs
- 📖 `EASY-START.md` - Detailed guide
- 📖 `RUN-OPTIONS.md` - All options explained
- 📖 `QUICKSTART.md` - Setup guide
- 📖 `INDEX.md` - File navigation

---

**THAT'S IT! Pick a launcher and enjoy your logistics routing system!** 🚀