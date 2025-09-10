# Growtopia Proxy Tester v3.0

Advanced proxy testing tool specifically designed for Growtopia compatibility, built based on analysis of the [Mori](https://github.com/CLOEI/mori) Growtopia client.

## 🎯 Features

### Comprehensive Testing Suite
- **SOCKS5 Basic Connectivity**: Verifies proxy can establish connections
- **HTTP Website Access**: Tests access to Growtopia's main website
- **Server Data Endpoints**: Critical test for game server discovery 
- **TCP Game Server Connection**: Direct connection to Growtopia game servers
- **ENet Protocol Compatibility**: Tests UDP/ENet protocol support
- **Scoring System**: 0-100 compatibility score based on test results

### Advanced Proxy Management
- **Automated IP Rotation**: Uses Heroku IPBurger addon for fresh IPs
- **Smart Blocking Detection**: Identifies 403 blocks and other proxy issues
- **Multi-Location Support**: Rotates between AU, US, CA, UK, DE, FR, NL, SG
- **Working Proxy Storage**: Saves compatible proxies with timestamps and scores

### Enhanced Reliability
- **Multi-Server Testing**: Tests multiple Growtopia server endpoints
- **Retry Logic**: Handles temporary failures gracefully  
- **Protocol Accuracy**: Based on real Growtopia client implementation
- **Detailed Logging**: Color-coded status messages with timestamps

## 🛠 Installation

### Prerequisites
- Arch Linux (or similar)
- Python 3.7+
- Heroku CLI
- Heroku app with IPBurger addon

### Quick Setup
```bash
git clone <this-repo>
cd cproxy
./setup.fish
```

### Manual Setup
```bash
# Install system dependencies
sudo pacman -S python python-pip heroku-cli

# Install Python packages
pip install -r requirements.txt

# Make executable
chmod +x gt_proxy_tester.py
```

## 🚀 Usage

### Basic Usage
```bash
# Run with default settings
./gt_proxy_tester.py

# Use custom Heroku app
./gt_proxy_tester.py --app your-app-name

# More attempts for finding working proxy
./gt_proxy_tester.py --max-attempts 20
```

### Test Specific Proxy
```bash
# Test your own SOCKS5 proxy
./gt_proxy_tester.py --test-proxy "socks5://username:password@ip:port"
```

### Advanced Options
```bash
# Full command with all options
./gt_proxy_tester.py \
    --app your-heroku-app \
    --max-attempts 15
```

## 🧪 Testing Methodology

Based on analysis of the Mori Growtopia client, our testing follows these steps:

### 1. SOCKS5 Basic Connectivity (20 points)
- Tests basic SOCKS5 proxy functionality
- Verifies authentication works
- Essential baseline test

### 2. HTTP Website Access (25 points) 
- Connects to `https://growtopiagame.com/`
- Detects 403 blocks (common proxy blocking method)
- Uses proper User-Agent strings

### 3. Server Data Endpoints (30 points) - **CRITICAL**
- Tests `growtopia2.com/growtopia/server_data.php`
- Tests `growtopia1.com/growtopia/server_data.php`
- Uses actual game protocol parameters
- Required for game server discovery

### 4. TCP Game Server Connection (20 points)
- Direct TCP test to `login.growtopiagame.com:17091`
- Tests `growtopia1.com:17091` and `growtopia2.com:17091`
- Verifies proxy can reach actual game servers

### 5. ENet Protocol Compatibility (5 points)
- Tests UDP functionality (ENet uses UDP)
- Checks SOCKS5 UDP association support
- Optional but enhances connection quality

## 📊 Compatibility Scoring

- **90-100**: Excellent compatibility, all tests pass
- **70-89**: Good compatibility, minor issues
- **50-69**: Fair compatibility, may have connection issues
- **Below 50**: Poor compatibility, not recommended

**Minimum Requirements for "Compatible":**
- SOCKS5 Basic: ✅ Required
- Server Data Access: ✅ Required  
- Either HTTP Website OR TCP Game Server: ✅ Required
- No 403 blocks: ✅ Required

## 🔧 Configuration

### Heroku Setup
1. Create Heroku app: `heroku create your-app-name`
2. Add IPBurger addon: `heroku addons:create ipburger --app your-app-name`
3. Login to Heroku: `heroku login`

### Proxy Locations
The tool rotates between these regions:
- `au` - Australia
- `us` - United States  
- `ca` - Canada
- `uk` - United Kingdom
- `de` - Germany
- `fr` - France
- `nl` - Netherlands
- `sg` - Singapore

## 📁 Output Files

### working_proxies.txt
Stores compatible proxies in format:
```
2025-09-11 15:30:25 - 192.168.1.1:1080:user:pass (Score: 95/100)
```

## 🔍 Technical Details

### Protocol Implementation
Based on Mori client analysis:
- Game Version: `5.26`
- Protocol Version: `216`
- User-Agent: `UbiServices_SDK_2022.Release.9_PC64_ansi_static`
- Uses proper ENet packet handling
- Implements SOCKS5 UDP association

### Connection Flow
1. SOCKS5 handshake with authentication
2. HTTP/HTTPS requests through proxy
3. Server data discovery via POST requests
4. TCP connection establishment to game servers
5. UDP/ENet compatibility verification

### Error Handling
- Proxy connection failures
- Authentication errors
- Timeout handling
- HTTP status code interpretation
- Network unreachable scenarios

## 🐛 Troubleshooting

### Common Issues

**"Heroku CLI not found"**
```bash
# Install via AUR
yay -S heroku-cli
# OR via npm
sudo npm install -g heroku
```

**"No proxy credential found"**
```bash
# Check Heroku app and addon
heroku addons --app your-app-name
heroku config --app your-app-name
```

**"SOCKS5 test failed"**  
```bash
# Install missing dependencies
pip install PySocks requests[socks]
```

**"403 Forbidden errors"**
- This means Growtopia blocked the proxy IP
- Tool will automatically rotate to new IP
- Some IP ranges are permanently blocked

### Debug Mode
```bash
# Enable verbose logging
export PYTHONPATH=/usr/lib/python3.11/site-packages
./gt_proxy_tester.py --max-attempts 5
```

## 🔒 Security & Privacy

- No data collection or external reporting
- Proxy credentials stored locally only
- Uses secure HTTPS connections
- Respects Growtopia's terms of service
- Educational/testing purposes only

## 📈 Performance Tips

1. **Optimal Attempt Count**: 10-15 attempts usually sufficient
2. **Peak Hours**: Avoid during Growtopia peak hours (evening US time)
3. **Multiple Locations**: Let tool rotate through different regions
4. **Patience**: Quality proxy detection takes time

## 🤝 Contributing

This tool is based on analysis of the excellent [Mori](https://github.com/CLOEI/mori) project by CLOEI. 

Improvements welcome:
- Additional test methods
- Better error handling  
- Performance optimizations
- More detailed protocol analysis

## ⚖️ Legal Disclaimer

This tool is for educational and testing purposes only. Users are responsible for:
- Complying with Growtopia's Terms of Service
- Respecting proxy provider terms
- Following local laws and regulations
- Using proxies ethically and legally

## 🔄 Migration from PowerShell Version

### Key Improvements Over v2.0:
- ✅ Cross-platform (Linux native)
- ✅ More accurate protocol testing
- ✅ Better error handling
- ✅ Detailed compatibility scoring  
- ✅ Based on actual game client analysis
- ✅ Enhanced proxy detection logic
- ✅ Proper SOCKS5 implementation

### Migration Steps:
1. Install new Python version
2. Import existing working_proxies.txt
3. Update Heroku credentials if needed
4. Run new tests to verify compatibility

---

**Version**: 3.0  
**Platform**: Linux/Python3  
**Based on**: [Mori Growtopia Client](https://github.com/CLOEI/mori)  
**Language**: Python 3.7+
