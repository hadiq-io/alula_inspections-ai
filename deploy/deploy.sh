#!/bin/bash
# =============================================================================
# AlUla Inspection AI - Deployment Script
# Run this script after setup-vm.sh to deploy the application
# =============================================================================

set -e  # Exit on error

# Configuration
VM_IP_OR_DOMAIN="20.3.236.169"
APP_DIR="/home/azureuser/alula-inspection-ai"

echo "=========================================="
echo "AlUla Inspection AI - Deployment"
echo "=========================================="

cd $APP_DIR

# ============================================
# Backend Setup
# ============================================
echo "🔧 Setting up Backend..."
cd $APP_DIR/backend

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3.11 -m venv venv
fi

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "Please create backend/.env with your Azure OpenAI and SQL Server credentials"
    echo "Use .env.example as a template"
fi

deactivate

# ============================================
# Frontend Setup
# ============================================
echo "🎨 Setting up Frontend..."
cd $APP_DIR/frontend

# Install dependencies
npm install

# Create .env.local for production API URL
echo "NEXT_PUBLIC_API_URL=http://$VM_IP_OR_DOMAIN" > .env.local

# Build for production
echo "📦 Building Next.js for production..."
npm run build

# ============================================
# Nginx Configuration
# ============================================
echo "🌐 Configuring Nginx..."

# Update nginx config with actual IP/domain
sed "s/YOUR_DOMAIN_OR_IP/$VM_IP_OR_DOMAIN/g" $APP_DIR/deploy/nginx.conf | sudo tee /etc/nginx/sites-available/alula-inspection-ai

# Enable the site
sudo ln -sf /etc/nginx/sites-available/alula-inspection-ai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx config
sudo nginx -t

# ============================================
# Systemd Services
# ============================================
echo "⚙️ Setting up systemd services..."

# Update frontend service with actual domain
sed "s/YOUR_DOMAIN_OR_IP/$VM_IP_OR_DOMAIN/g" $APP_DIR/deploy/alula-frontend.service | sudo tee /etc/systemd/system/alula-frontend.service

# Copy backend service
sudo cp $APP_DIR/deploy/alula-backend.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable alula-backend
sudo systemctl enable alula-frontend

# ============================================
# Start Services
# ============================================
echo "🚀 Starting services..."

sudo systemctl restart alula-backend
sudo systemctl restart alula-frontend
sudo systemctl restart nginx

# Wait for services to start
sleep 5

# Check status
echo ""
echo "=========================================="
echo "📊 Service Status"
echo "=========================================="
echo ""
echo "Backend status:"
sudo systemctl status alula-backend --no-pager -l | head -10
echo ""
echo "Frontend status:"
sudo systemctl status alula-frontend --no-pager -l | head -10
echo ""
echo "Nginx status:"
sudo systemctl status nginx --no-pager -l | head -5

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "🌐 Your application is now available at:"
echo "   http://$VM_IP_OR_DOMAIN"
echo ""
echo "📋 Useful commands:"
echo "   View backend logs:  sudo tail -f /var/log/alula/backend.log"
echo "   View frontend logs: sudo tail -f /var/log/alula/frontend.log"
echo "   Restart backend:    sudo systemctl restart alula-backend"
echo "   Restart frontend:   sudo systemctl restart alula-frontend"
echo "   Restart nginx:      sudo systemctl restart nginx"
echo ""
