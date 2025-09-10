#!/home/joy/cproxy/venv/bin/python3

"""
Growtopia Proxy Tester - Demo Script
Shows various features and capabilities of the testing system
"""

import sys
import time
from gt_proxy_tester import GrowtopiaProxyTester

def demo_all_features():
    """Demonstrate all features of the proxy tester"""
    
    print("🚀 Growtopia Proxy Tester - Feature Demo")
    print("=" * 60)
    
    tester = GrowtopiaProxyTester("ipburger-demo-joy")
    
    # Demo 1: Test Prerequisites
    print("\n1. 🔍 Prerequisites Check")
    print("-" * 30)
    prereq_ok = tester.check_prerequisites()
    print(f"Prerequisites OK: {'✅' if prereq_ok else '❌'}")
    
    if not prereq_ok:
        print("⚠️  Please run setup.fish first!")
        return
    
    # Demo 2: Parse proxy URL
    print("\n2. 🔧 Proxy URL Parsing")
    print("-" * 30)
    test_proxy = "socks5://user:pass@192.168.1.1:1080"
    parsed = tester.parse_proxy_url(test_proxy)
    print(f"Input: {test_proxy}")
    print(f"Parsed: {parsed}")
    
    # Demo 3: Test existing proxy from file
    print("\n3. 📁 Testing Existing Proxy")
    print("-" * 30)
    try:
        with open("working_proxies.txt", "r") as f:
            lines = f.readlines()
        
        if lines:
            # Parse the latest proxy
            latest = lines[-1].strip()
            print(f"Latest saved proxy: {latest}")
            
            # Extract proxy URL (simplified)
            import re
            pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (.+?)(?:\s+\(Score: \d+/100\))?$"
            match = re.match(pattern, latest)
            
            if match:
                timestamp, proxy_info = match.groups()
                parts = proxy_info.split(':')
                
                if len(parts) == 4:
                    host, port, username, password = parts
                    proxy_url = f"socks5://{username}:{password}@{host}:{port}"
                    
                    print(f"Testing: {proxy_url}")
                    is_compatible, results = tester.test_full_growtopia_compatibility(proxy_url)
                    
                    print(f"Result: {'🎉 WORKING' if is_compatible else '❌ NOT WORKING'}")
                    print(f"Score: {results['overall_score']}/100")
                    
                    # Show detailed breakdown
                    print("\nDetailed Results:")
                    print(f"  SOCKS5 Basic: {'✅' if results['socks5_basic'] else '❌'}")
                    print(f"  HTTP Website: {'✅' if results['http_website'] else '❌'} ({results['http_status']})")
                    print(f"  Server Data: {'✅' if results['server_data'] else '❌'}")
                    print(f"  TCP Game Server: {'✅' if results['tcp_game_server'] else '❌'}")
                    print(f"  ENet Compatible: {'✅' if results['enet_compat'] else '❌'}")
                    
        else:
            print("No saved proxies found")
            
    except FileNotFoundError:
        print("No working_proxies.txt file found")
    
    # Demo 4: Show configuration
    print(f"\n4. ⚙️  Configuration")
    print("-" * 30)
    print(f"App Name: {tester.app_name}")
    print(f"Locations: {', '.join(tester.locations)}")
    print(f"Game Version: {tester.GAME_VERSION}")
    print(f"Protocol: {tester.PROTOCOL}")
    print(f"User Agent: {tester.USER_AGENT}")
    
    # Demo 5: Server endpoints
    print(f"\n5. 🌐 Server Endpoints")
    print("-" * 30)
    print("Game Servers:")
    for server in tester.GROWTOPIA_SERVERS:
        print(f"  • {server}")
    
    print("\nServer Data URLs:")
    for url in tester.SERVER_DATA_URLS:
        print(f"  • {url}")
    
    # Demo 6: Test scoring system
    print(f"\n6. 📊 Scoring System")
    print("-" * 30)
    print("Score Breakdown:")
    print("  • SOCKS5 Basic: 20 points")
    print("  • HTTP Website: 25 points")  
    print("  • Server Data: 30 points (Critical)")
    print("  • TCP Game Server: 20 points")
    print("  • ENet Compatible: 5 points")
    print("  • Total: 100 points")
    print("")
    print("Compatibility Requirements:")
    print("  ✅ SOCKS5 Basic (Required)")
    print("  ✅ Server Data Access (Required)")
    print("  ✅ HTTP Website OR TCP Game Server (Required)")
    print("  ❌ No 403 blocks (Required)")
    
    print(f"\n🎯 Demo Complete!")
    print("=" * 60)
    print("\n💡 Usage Examples:")
    print("  ./gt_proxy_tester.py                                    # Find new working proxy")
    print("  ./gt_proxy_tester.py --app my-heroku-app               # Use different Heroku app")
    print("  ./gt_proxy_tester.py --max-attempts 20                 # More attempts")
    print("  ./test_existing_proxy.py --test-latest                 # Test latest saved proxy")
    print("  ./test_existing_proxy.py --from-file working_proxies.txt  # Test all saved proxies")

def demo_test_specific_proxy():
    """Demo testing a specific proxy format"""
    
    print("\n🧪 Testing Specific Proxy Format")
    print("=" * 50)
    
    # Example proxy formats
    test_proxies = [
        "socks5://username:password@proxy.example.com:1080",
        "socks5://testuser:testpass@192.168.1.100:1080", 
        "socks5://user123:pass456@10.0.0.1:8080"
    ]
    
    print("Supported proxy formats:")
    for i, proxy in enumerate(test_proxies, 1):
        print(f"  {i}. {proxy}")
    
    print(f"\n📝 Note: These are example formats only")
    print(f"Replace with actual working proxy credentials to test")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--formats":
        demo_test_specific_proxy()
    else:
        demo_all_features()
