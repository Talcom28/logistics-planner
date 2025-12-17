# IT Administrator Setup Guide

## Overview

This guide helps IT administrators deploy and maintain the Logistics Route Planner without requiring deep programming knowledge. It covers cloud deployment, database setup, and basic maintenance.

---

## Quick Deployment Options

### Option 1: Cloud Deployment (Recommended for Most Organizations)
**Easiest method - No servers to manage**

**What you need:**
- GitHub account (free)
- Railway.app account (free tier available)
- 30 minutes of time

**Steps:**

1. **Get the code on GitHub**
   - Create a free account at github.com
   - Create a new repository called "logistics-planner"
   - Upload the project files (or have the developer push them)

2. **Deploy to Railway.app**
   - Go to railway.app and sign up
   - Click "New Project"
   - Select "Deploy from GitHub"
   - Choose your logistics-planner repository
   - Railway will automatically detect it's a Python project

3. **Add a database**
   - In your Railway project, click "New"
   - Select "PostgreSQL"
   - Railway will create a database and connect it automatically
   - The DATABASE_URL will be set automatically

4. **Get your public URL**
   - Railway provides a public URL like: `https://logistics-planner-prod.railway.app`
   - Give this URL to your users
   - Users visit: `https://your-url.railway.app/docs`

**Cost:** Railway free tier includes $5/month credit (sufficient for small teams)

---

### Option 2: Docker Deployment (For On-Premise Servers)
**Good if you need to run on your own servers**

**What you need:**
- A server (Windows Server, Linux, or Mac)
- Docker Desktop installed (free from docker.com)
- Access to install software on the server

**Steps:**

1. **Install Docker**
   - Download Docker Desktop from docker.com
   - Install using the default settings
   - Restart your computer if prompted

2. **Copy project files to server**
   - Copy the entire project folder to your server
   - Open Command Prompt or Terminal
   - Navigate to the project folder

3. **Start everything**
   - Double-click `START-DOCKER.bat` (Windows)
   - Or run `./start-docker.sh` (Mac/Linux)
   - Wait 2-3 minutes for everything to start

4. **Access the application**
   - Backend API: `http://your-server-ip:8000/docs`
   - Frontend: `http://your-server-ip:5173`
   - Users on your network can access these URLs

**Port requirements:** Make sure ports 8000, 5173, and 5432 are open in your firewall

---

### Option 3: Simple Python Deployment (For Testing)
**Quick setup for development or small teams**

**What you need:**
- Python 3.11 or newer installed
- Access to command line

**Steps:**

1. **Install Python**
   - Download from python.org
   - During installation, check "Add Python to PATH"

2. **Open command line in project folder**
   - Right-click the project folder
   - Select "Open in Terminal" or "Open Command Prompt"

3. **Run the setup script**
   - Windows: Double-click `RUN.bat`
   - Mac/Linux: Run `./start-backend.sh`

4. **Access locally**
   - Open browser to `http://localhost:8000/docs`
   - Only accessible from this computer

---

## Database Setup

### Using Railway PostgreSQL (Easiest)
- Railway automatically creates and connects the database
- No manual configuration needed
- Automatic backups included
- Connection string is set for you

### Using Your Own PostgreSQL Server
If you have an existing PostgreSQL server:

1. **Create a database**
   - Database name: `logistics`
   - Username: `logistics` (or your choice)
   - Password: (choose a strong password)

2. **Set the connection string**
   - Format: `postgresql://username:password@server:5432/logistics`
   - Example: `postgresql://logistics:mypassword123@db.company.com:5432/logistics`

3. **Configure the application**
   - **Railway/Cloud:** Add environment variable `DATABASE_URL` with your connection string
   - **Docker:** Edit `docker-compose.yml` and update the DATABASE_URL
   - **Local:** Set environment variable before running

4. **Enable PostGIS extension**
   - Connect to your database using pgAdmin or similar tool
   - Run command: `CREATE EXTENSION postgis;`
   - This enables geographic calculations

---

## Initial Data Setup

### Loading Port and Airport Data

The system needs data about ports and airports to calculate routes.

**Sample data is included:**
- The app will create sample ports automatically on first start
- Good enough for testing and small deployments

**To load real-world data:**

1. **Download port data**
   - OurPorts: https://ourairports.com/data/ (free)
   - UN/LOCODE: https://unece.org/trade/cefact/unlocode-code-list-country-and-territory (official but requires registration)

2. **Import the data**
   - Open your browser to: `http://your-url/docs`
   - Look for "import" endpoints
   - Or contact your developer to run the import script

3. **Update fuel prices**
   - Edit the `data/carriers.json` file
   - Update prices in the database using the API
   - Prices are estimates; update monthly for accuracy

---

## User Access Setup

### Public Access (No Login Required)
The default setup allows anyone with the URL to use the system.

**To restrict access:**
- Add authentication via Railway environment variables
- Use a VPN to restrict to your network
- Place behind corporate SSO (requires developer assistance)

### Creating User Accounts
Current version doesn't include built-in user accounts. Options:

- Use Railway's authentication addon
- Add API keys for programmatic access
- Integrate with your existing SSO system (requires customization)

---

## Monitoring and Maintenance

### Checking if the System is Running

**Railway/Cloud:**
- Visit your app's URL - you should see the API docs
- Railway dashboard shows service status (green = running)
- Check logs in Railway dashboard

**Docker:**
- Run: `docker ps` to see running containers
- All three services should show "Up"
- Visit: `http://localhost:8000/docs`

**Local Python:**
- Check if you see "Uvicorn running on..." in the terminal
- Visit: `http://localhost:8000/docs`

### Viewing Logs

**Railway:**
- Click on your service in Railway dashboard
- Select "Deployments" tab
- Click "View Logs"
- Look for errors (lines starting with ERROR or WARN)

**Docker:**
- Run: `docker logs logistics-planner-backend`
- Run: `docker logs logistics-planner-db`

**Local:**
- Logs appear in the terminal where you started the app
- Scroll up to see error messages

### Restarting the Service

**Railway:**
- Click the three dots (...) on your service
- Select "Restart"
- Wait 1-2 minutes for it to come back online

**Docker:**
- Run: `docker-compose restart`
- Or stop and start: `docker-compose down` then `docker-compose up -d`

**Local:**
- Press Ctrl+C to stop
- Run the start script again

---

## Common Issues and Solutions

### "Application Failed to Start"
**What it means:** The backend service crashed during startup

**How to fix:**
1. Check logs for error messages
2. Verify DATABASE_URL is set correctly
3. Ensure database is running and accessible
4. Try restarting the service

### "Database Connection Error"
**What it means:** Can't connect to PostgreSQL

**How to fix:**
1. Verify database is running
2. Check DATABASE_URL format: `postgresql://user:pass@host:5432/dbname`
3. Ensure firewall allows connection to port 5432
4. Test connection using a database tool (pgAdmin, DBeaver)

### "No Ports Found"
**What it means:** Database is empty or not loading sample data

**How to fix:**
1. Check if database tables were created
2. Restart the application (it seeds sample data on startup)
3. Manually import port data using the import endpoints

### "Module Not Found" or "Import Error"
**What it means:** Missing Python packages

**How to fix:**
1. Railway: Redeploy (it reinstalls packages automatically)
2. Docker: Run `docker-compose build --no-cache`
3. Local: Run `pip install -r requirements.txt`

### Users Can't Access the URL
**What it means:** Network/firewall issue

**How to fix:**
1. Verify the URL is correct
2. Check if service is running (see Monitoring section)
3. For on-premise: Ensure firewall allows incoming connections
4. For cloud: Verify Railway service has public URL enabled

---

## Performance Optimization

### For Small Teams (Under 50 users)
- Railway free tier is sufficient
- No optimization needed
- Sample port data works fine

### For Medium Organizations (50-500 users)
- Upgrade to Railway Pro plan ($20/month)
- Import full port/airport datasets
- Monitor memory usage in Railway dashboard
- Consider caching frequently-requested routes

### For Large Deployments (500+ users)
- Use dedicated PostgreSQL server (AWS RDS, Azure Database)
- Deploy multiple backend instances (load balancing)
- Add Redis for caching
- Consult with developer for scaling strategy

---

## Backup and Recovery

### Railway (Automatic)
- Database backups happen automatically
- To restore: Railway dashboard → Database → Backups
- Can restore to any point in last 7 days

### Docker/On-Premise
**Backup database:**
```
docker exec logistics-planner-db pg_dump -U logistics logistics > backup.sql
```

**Restore database:**
```
docker exec -i logistics-planner-db psql -U logistics logistics < backup.sql
```

**Schedule backups:**
- Windows: Use Task Scheduler
- Linux: Use cron jobs
- Run backup command daily at minimum

### What to Backup
- Database (most important)
- `data/carriers.json` (if customized)
- Environment variables/configuration
- Custom code changes (if any)

---

## Updating the Software

### Railway (Automatic Updates)
When new code is pushed to GitHub:
- Railway automatically detects changes
- Builds and deploys new version
- Takes 2-3 minutes
- No downtime for users

### Docker
1. Pull latest code from repository
2. Run: `docker-compose down`
3. Run: `docker-compose build`
4. Run: `docker-compose up -d`

### Local Python
1. Pull latest code
2. Run: `pip install -r requirements.txt --upgrade`
3. Restart the application

### Before Updating
- Backup database
- Test in development environment first
- Notify users of maintenance window (if needed)

---

## Security Checklist

- [ ] Database password is strong (12+ characters, mixed case, numbers, symbols)
- [ ] DATABASE_URL is not exposed publicly
- [ ] Railway environment variables are private
- [ ] HTTPS is enabled (Railway does this automatically)
- [ ] Only necessary ports are open in firewall
- [ ] Database backups are scheduled
- [ ] Logs are monitored for suspicious activity
- [ ] Users are trained not to enter sensitive data in route descriptions

---

## Getting Support

### Self-Help Resources
- This guide
- USER-GUIDE.md (for end users)
- `/docs` endpoint (API documentation)
- Railway documentation: https://docs.railway.app

### When to Contact Developer
- Custom features needed
- Integration with other systems
- Performance issues with large datasets
- Security incidents
- Major configuration changes

### Information to Provide
When asking for help, include:
- Deployment method (Railway, Docker, Local)
- Error messages from logs
- What you were trying to do
- Steps to reproduce the problem
- Screenshots if applicable

---

## Cost Estimates

### Railway Cloud Hosting
- **Free Tier:** $5/month credit (good for testing, small teams)
- **Hobby Plan:** $5/month (includes $5 credit)
- **Pro Plan:** $20/month (recommended for production)
- **Database:** Included in credit usage
- **Estimated cost for 50 users:** $10-15/month

### On-Premise Hosting
- **Server:** Use existing infrastructure (cost: $0)
- **Electricity:** Minimal (a few dollars/month)
- **IT time:** Initial setup (4 hours) + maintenance (1 hour/month)
- **Estimated cost:** $100-200 setup, $20/month ongoing

### Cloud Server (AWS, Azure, etc.)
- **Small instance:** $20-50/month
- **Database:** $15-30/month
- **Bandwidth:** Usually included
- **Estimated total:** $35-80/month

---

## Next Steps After Deployment

1. **Test the system**
   - Create a test route plan
   - Verify ports load correctly
   - Check that carriers are available

2. **Train users**
   - Share the USER-GUIDE.md
   - Demonstrate basic route planning
   - Show how to interpret results

3. **Load real data**
   - Import accurate port/airport data
   - Update carrier models for your fleet
   - Set realistic fuel prices

4. **Set up monitoring**
   - Add your URL to an uptime monitor
   - Schedule weekly log reviews
   - Set up database backups

5. **Plan for updates**
   - Subscribe to update notifications
   - Test updates in development first
   - Schedule monthly maintenance window

---

## Quick Reference Commands

**Check if Docker is running:**
```
docker --version
```

**View running containers:**
```
docker ps
```

**Restart Railway service:**
- Railway dashboard → Service → Menu → Restart

**View Python version:**
```
python --version
```

**Test database connection:**
- Connect using pgAdmin or DBeaver
- Use the DATABASE_URL connection string

**Check if port is open:**
```
netstat -an | find "8000"
```

---

*Last updated: December 2025*

For technical support, consult with your development team or the software vendor.
