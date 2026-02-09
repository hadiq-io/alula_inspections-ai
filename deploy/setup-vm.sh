#!/bin/bash
# =============================================================================
# AlUla Inspection AI - Azure VM Setup Script
# Run this script on your Azure VM to set up the environment
# =============================================================================

set -e  # Exit on error

echo "=========================================="
echo "AlUla Inspection AI - VM Setup"
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Node.js 20 LTS
echo "📦 Installing Node.js 20 LTS..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python 3.11 and pip
echo "🐍 Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install ODBC drivers for SQL Server
echo "🔌 Installing ODBC drivers..."
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt update
sudo ACCEPT_EULA=Y apt install -y msodbcsql18 unixodbc-dev

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt install -y nginx

# Create log directory
echo "📁 Creating log directory..."
sudo mkdir -p /var/log/alula
sudo chown azureuser:azureuser /var/log/alula

# Verify installations
echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo "Node.js version: $(node -v)"
echo "npm version: $(npm -v)"
echo "Python version: $(python3.11 --version)"
echo ""
echo "Next steps:"
echo "1. Clone your repository to /home/azureuser/alula-inspection-ai"
echo "2. Run the deploy.sh script"
