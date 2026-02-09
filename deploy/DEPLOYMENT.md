# AlUla Inspection AI - Azure VM Deployment Guide

## Overview
This guide explains how to deploy the AlUla Inspection AI solution to your Azure VM.

---

## Prerequisites

1. **Azure VM** running Ubuntu 22.04 or later
2. **Open ports** in Azure Network Security Group:
   - Port 22 (SSH)
   - Port 80 (HTTP)
   - Port 443 (HTTPS) - optional for SSL

---

## Deployment Steps

### Step 1: Connect to Your Azure VM

```bash
ssh azureuser@YOUR_VM_IP
```

### Step 2: Clone the Repository

```bash
cd /home/azureuser
git clone https://github.com/YOUR_REPO/alula-inspection-ai.git
cd alula-inspection-ai
```

**Or copy files from your local machine:**
```bash
# From your local machine
scp -r /Users/carlostorres/alula-inspection-ai azureuser@YOUR_VM_IP:/home/azureuser/
```

### Step 3: Run the VM Setup Script

```bash
chmod +x deploy/setup-vm.sh
./deploy/setup-vm.sh
```

This installs:
- Node.js 20 LTS
- Python 3.11
- SQL Server ODBC drivers
- Nginx

### Step 4: Configure Environment Variables

```bash
# Copy the example and edit with your credentials
cd backend
cp .env.production.example .env
nano .env
```

Update these values:
```env
AZURE_OPENAI_ENDPOINT=https://your-actual-endpoint.openai.azure.com/
AZURE_OPENAI_KEY=your_actual_api_key
AZURE_DEPLOYMENT_NAME=your_deployment_name
SQL_SERVER=your_server.database.windows.net
SQL_DATABASE=InspectionDB
SQL_USERNAME=your_username
SQL_PASSWORD=your_password
CORS_ORIGINS=http://YOUR_VM_IP
```

### Step 5: Update Deploy Script Configuration

```bash
cd /home/azureuser/alula-inspection-ai
nano deploy/deploy.sh
```

Update the `VM_IP_OR_DOMAIN` variable at the top:
```bash
VM_IP_OR_DOMAIN="20.xxx.xxx.xxx"  # Your actual Azure VM IP
```

### Step 6: Run the Deployment

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

This will:
1. Set up the Python virtual environment
2. Install backend dependencies
3. Install frontend dependencies
4. Build Next.js for production
5. Configure Nginx as reverse proxy
6. Set up systemd services for auto-start
7. Start all services

---

## Accessing the Application

After deployment, access your application at:
```
http://YOUR_VM_IP
```

---

## Useful Commands

### View Logs
```bash
# Backend logs
sudo tail -f /var/log/alula/backend.log
sudo tail -f /var/log/alula/backend-error.log

# Frontend logs
sudo tail -f /var/log/alula/frontend.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Service Management
```bash
# Restart services
sudo systemctl restart alula-backend
sudo systemctl restart alula-frontend
sudo systemctl restart nginx

# Check status
sudo systemctl status alula-backend
sudo systemctl status alula-frontend
sudo systemctl status nginx

# Stop services
sudo systemctl stop alula-backend
sudo systemctl stop alula-frontend
```

### Manual Testing
```bash
# Test backend directly
curl http://localhost:8000/health

# Test frontend directly
curl http://localhost:3000

# Test through nginx
curl http://YOUR_VM_IP
```

---

## Troubleshooting

### Backend Not Starting
```bash
# Check logs
sudo tail -100 /var/log/alula/backend-error.log

# Test manually
cd /home/azureuser/alula-inspection-ai/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend Not Starting
```bash
# Check logs
sudo tail -100 /var/log/alula/frontend.log

# Rebuild
cd /home/azureuser/alula-inspection-ai/frontend
npm run build
npm start
```

### Database Connection Issues
```bash
# Test ODBC connection
cd /home/azureuser/alula-inspection-ai/backend
source venv/bin/activate
python -c "from database import Database; db = Database(); print(db.test_connection())"
```

### Nginx Issues
```bash
# Test configuration
sudo nginx -t

# Check error log
sudo tail -50 /var/log/nginx/error.log
```

---

## Updating the Application

When you have new code changes:

```bash
cd /home/azureuser/alula-inspection-ai

# Pull latest changes (if using git)
git pull

# Rebuild and restart
cd frontend && npm install && npm run build
sudo systemctl restart alula-frontend
sudo systemctl restart alula-backend
```

---

## Security Recommendations

1. **Enable HTTPS** with Let's Encrypt:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

2. **Restrict SSH access** in Azure Network Security Group

3. **Use Azure Key Vault** for sensitive credentials

4. **Enable Azure VM auto-shutdown** for cost savings during non-testing hours
