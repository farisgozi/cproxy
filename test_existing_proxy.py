#!/home/joy/cproxy/venv/bin/python3

import sys
import re
from gt_proxy_tester import GrowtopiaProxyTester

def parse_proxy_from_file_format(line):
    """Parse proxy from working_proxies.txt format"""
    # Format: 2025-09-10 06:27:22 - 104-238-158-103.ip.heroku.ipb.cloud:8040:S3btwK:l46NNap3
    pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (.+)"
    match = re.match(pattern, line.strip())
    
    if match:
        timestamp, proxy_info = match.groups()
        parts = proxy_info.split(':')
        
        if len(parts) == 4:
            host, port, username, password = parts
            return f"socks5://{username}:{password}@{host}:{port}"
    
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ./test_existing_proxy.py 'socks5://user:pass@host:port'")
        print("  ./test_existing_proxy.py --from-file working_proxies.txt")
        print("  ./test_existing_proxy.py --test-latest")
        sys.exit(1)
    
    tester = GrowtopiaProxyTester()
    
    if sys.argv[1] == "--from-file" and len(sys.argv) == 3:
        # Test all proxies from file
        filename = sys.argv[2]
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            print(f"Testing {len(lines)} proxies from {filename}...")
            working_count = 0
            
            for i, line in enumerate(lines, 1):
                proxy_url = parse_proxy_from_file_format(line)
                if proxy_url:
                    print(f"\n[{i}/{len(lines)}] Testing: {proxy_url}")
                    is_compatible, results = tester.test_full_growtopia_compatibility(proxy_url)
                    
                    if is_compatible:
                        print(f"✅ WORKING - Score: {results['overall_score']}/100")
                        working_count += 1
                    else:
                        print(f"❌ NOT WORKING - Score: {results['overall_score']}/100")
                        if results['http_status'] == '403':
                            print("   Reason: Blocked by Growtopia (403)")
                else:
                    print(f"[{i}/{len(lines)}] Invalid format: {line.strip()}")
            
            print(f"\nResults: {working_count}/{len(lines)} proxies still working")
            
        except FileNotFoundError:
            print(f"Error: File {filename} not found")
            sys.exit(1)
            
    elif sys.argv[1] == "--test-latest":
        # Test the latest proxy from working_proxies.txt
        try:
            with open("working_proxies.txt", 'r') as f:
                lines = f.readlines()
            
            if not lines:
                print("No proxies found in working_proxies.txt")
                sys.exit(1)
            
            latest_line = lines[-1]
            proxy_url = parse_proxy_from_file_format(latest_line)
            
            if proxy_url:
                print(f"Testing latest proxy: {proxy_url}")
                is_compatible, results = tester.test_full_growtopia_compatibility(proxy_url)
                
                print(f"\n{'='*50}")
                print("LATEST PROXY TEST RESULTS")
                print(f"{'='*50}")
                print(f"Compatible: {'YES' if is_compatible else 'NO'}")
                print(f"Score: {results['overall_score']}/100")
                
                if is_compatible:
                    print("🎉 Proxy is still working for Growtopia!")
                else:
                    print("❌ Proxy is no longer working")
                    if results['http_status'] == '403':
                        print("Reason: Blocked by Growtopia")
                
                sys.exit(0 if is_compatible else 1)
            else:
                print("Error: Could not parse latest proxy")
                sys.exit(1)
                
        except FileNotFoundError:
            print("Error: working_proxies.txt not found")
            sys.exit(1)
            
    else:
        # Test single proxy URL
        proxy_url = sys.argv[1]
        print(f"Testing proxy: {proxy_url}")
        
        is_compatible, results = tester.test_full_growtopia_compatibility(proxy_url)
        
        print(f"\n{'='*50}")
        print("PROXY TEST RESULTS")
        print(f"{'='*50}")
        print(f"Proxy: {proxy_url}")
        print(f"Compatible: {'YES' if is_compatible else 'NO'}")
        print(f"Score: {results['overall_score']}/100")
        print(f"{'='*50}")
        print("Detailed Results:")
        print(f"  SOCKS5 Basic: {'✓' if results['socks5_basic'] else '✗'}")
        print(f"  HTTP Website: {'✓' if results['http_website'] else '✗'} ({results['http_status']})")
        print(f"  Server Data: {'✓' if results['server_data'] else '✗'}")
        print(f"  TCP Game Server: {'✓' if results['tcp_game_server'] else '✗'}")
        print(f"  ENet Compatible: {'✓' if results['enet_compat'] else '✗'}")
        print(f"{'='*50}")
        
        if is_compatible:
            tester.save_working_proxy(proxy_url, results)
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()
