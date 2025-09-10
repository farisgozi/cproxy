#!/usr/bin/env fish

# Growtopia Proxy Tester - Setup Script for Arch Linux
echo "🚀 Setting up Growtopia Proxy Tester..."

# Check if Python 3 is installed
if not command -v python3 > /dev/null
    echo "❌ Python 3 not found. Installing..."
    sudo pacman -S python python-pip --noconfirm
end

# Check if Heroku CLI is installed  
if not command -v heroku > /dev/null
    echo "❌ Heroku CLI not found. Installing..."
    
    # Install Heroku CLI for Arch Linux
    if command -v yay > /dev/null
        yay -S heroku-cli --noconfirm
    else if command -v paru > /dev/null
        paru -S heroku-cli --noconfirm
    else
        echo "Installing heroku-cli via npm (fallback)..."
        sudo pacman -S nodejs npm --noconfirm
        sudo npm install -g heroku
    end
end

# Install Python dependencies
echo "📦 Installing Python dependencies..."

# Create virtual environment if it doesn't exist
if not test -d venv
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv venv
end

# Activate virtual environment and install packages
echo "📦 Installing packages in virtual environment..."
source venv/bin/activate.fish
pip install --upgrade pip
pip install -r requirements.txt

# Make script executable
chmod +x gt_proxy_tester.py

echo "✅ Setup complete!"
echo ""
echo "🎯 Usage examples:"
echo "  ./gt_proxy_tester.py                                    # Run full test cycle"
echo "  ./gt_proxy_tester.py --app your-heroku-app             # Use different app"
echo "  ./gt_proxy_tester.py --max-attempts 20                 # More attempts" 
echo "  ./gt_proxy_tester.py --test-proxy socks5://user:pass@ip:port  # Test specific proxy"
echo ""
echo "📋 Before running, make sure you're logged into Heroku:"
echo "  heroku login"
echo ""
echo "🚀 Ready to find working Growtopia proxies!"
