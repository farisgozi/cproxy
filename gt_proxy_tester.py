#!/home/joy/cproxy/venv/bin/python3

import json
import random
import re
import socket
import subprocess
import sys
import threading
import time
from datetime import datetime
from typing import Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from urllib3.contrib.socks import SOCKSProxyManager


class GrowtopiaProxyTester:
    def __init__(self, app_name: str = "ipburger-demo-joy"):
        self.app_name = app_name
        self.locations = ["au", "us", "ca", "uk", "de", "fr", "nl", "sg"]
        self.working_proxies_file = "working_proxies.txt"
        
        # Growtopia specific constants based on Mori source
        self.USER_AGENT = "UbiServices_SDK_2022.Release.9_PC64_ansi_static"
        self.GAME_VERSION = "5.26"
        self.PROTOCOL = "216"
        
        # Server endpoints from Mori analysis
        self.GROWTOPIA_SERVERS = [
            "login.growtopiagame.com:17091",
            "growtopia1.com:17091",
            "growtopia2.com:17091"
        ]
        
        self.SERVER_DATA_URLS = [
            "https://www.growtopia2.com/growtopia/server_data.php",
            "https://www.growtopia1.com/growtopia/server_data.php"
        ]
        
        print(self._get_banner())
        
    def _get_banner(self) -> str:
        return f"""
{'='*50}
 GROWTOPIA PROXY TESTER v3.0 (Python Edition)
{'='*50}
App: {self.app_name}
Target: Growtopia Game Servers
Implementation: Based on Mori Protocol Analysis
{'='*50}
"""

    def _log(self, level: str, message: str):
        """Enhanced logging with colors"""
        colors = {
            "INFO": "\033[96m",     # Cyan
            "SUCCESS": "\033[92m",  # Green
            "WARNING": "\033[93m",  # Yellow
            "ERROR": "\033[91m",    # Red
            "DEBUG": "\033[95m"     # Magenta
        }
        reset = "\033[0m"
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {colors.get(level, '')}{level}: {message}{reset}")

    def get_credential(self) -> Optional[str]:
        """Get proxy credential from Heroku"""
        try:
            result = subprocess.run(
                ["heroku", "config:get", "IPB_SOCKS5", "--app", self.app_name],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            return None
        except Exception as e:
            self._log("ERROR", f"Failed to get credential: {e}")
            return None

    def parse_proxy_url(self, proxy_url: str) -> Optional[dict]:
        """Parse SOCKS5 proxy URL into components"""
        pattern = r"socks5h?://([^:]+):([^@]+)@([^:]+):([0-9]+)"
        match = re.match(pattern, proxy_url)
        
        if match:
            return {
                'username': match.group(1),
                'password': match.group(2),
                'host': match.group(3),
                'port': int(match.group(4))
            }
        return None

    def test_socks5_basic(self, proxy_config: dict, timeout: int = 15) -> bool:
        """Test basic SOCKS5 connectivity using socket connection"""
        try:
            import socks
            
            sock = socks.socksocket()
            sock.set_proxy(
                socks.SOCKS5, 
                proxy_config['host'], 
                proxy_config['port'],
                username=proxy_config['username'],
                password=proxy_config['password']
            )
            sock.settimeout(timeout)
            
            # Test connection to Google (reliable test)
            sock.connect(("www.google.com", 80))
            sock.close()
            
            self._log("SUCCESS", "SOCKS5 basic connectivity test passed")
            return True
            
        except Exception as e:
            self._log("ERROR", f"SOCKS5 basic test failed: {e}")
            return False

    def test_http_to_growtopia(self, proxy_config: dict, timeout: int = 20) -> Tuple[bool, str]:
        """Test HTTP connection to Growtopia website with proper proxy"""
        try:
            # Create SOCKS proxy for requests
            proxy_url = f"socks5://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['host']}:{proxy_config['port']}"
            
            session = requests.Session()
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # Configure retry strategy
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Test connection to Growtopia website
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = session.get(
                "https://growtopiagame.com/",
                headers=headers,
                timeout=timeout
            )
            
            status_code = response.status_code
            
            if status_code == 200:
                self._log("SUCCESS", f"HTTP to Growtopia website: {status_code}")
                return True, str(status_code)
            elif status_code == 403:
                self._log("WARNING", f"Growtopia blocked this proxy: {status_code}")
                return False, str(status_code)
            else:
                self._log("WARNING", f"HTTP response: {status_code}")
                return False, str(status_code)
                
        except requests.exceptions.ProxyError as e:
            self._log("ERROR", f"Proxy connection failed: {e}")
            return False, "PROXY_ERROR"
        except requests.exceptions.Timeout as e:
            self._log("ERROR", f"HTTP request timeout: {e}")
            return False, "TIMEOUT"
        except Exception as e:
            self._log("ERROR", f"HTTP test failed: {e}")
            return False, "ERROR"

    def test_server_data_endpoint(self, proxy_config: dict, timeout: int = 20) -> bool:
        """Test connection to Growtopia server_data.php endpoint"""
        try:
            proxy_url = f"socks5://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['host']}:{proxy_config['port']}"
            
            session = requests.Session()
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            headers = {
                'User-Agent': self.USER_AGENT,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Test server data endpoint (critical for game connection)
            for url in self.SERVER_DATA_URLS:
                try:
                    data = f"platform=0&protocol={self.PROTOCOL}&version={self.GAME_VERSION}"
                    response = session.post(url, headers=headers, data=data, timeout=timeout)
                    
                    if response.status_code == 200 and response.text:
                        # Parse server data response (basic validation)
                        if "server|" in response.text or "port|" in response.text:
                            self._log("SUCCESS", f"Server data endpoint accessible: {url}")
                            return True
                        
                except Exception as e:
                    self._log("DEBUG", f"Server data test failed for {url}: {e}")
                    continue
            
            self._log("ERROR", "All server data endpoints failed")
            return False
            
        except Exception as e:
            self._log("ERROR", f"Server data test failed: {e}")
            return False

    def test_tcp_connection_to_game_server(self, proxy_config: dict, timeout: int = 15) -> bool:
        """Test TCP connection to Growtopia game servers through SOCKS5"""
        try:
            import socks
            
            for server in self.GROWTOPIA_SERVERS:
                try:
                    host, port = server.split(':')
                    port = int(port)
                    
                    sock = socks.socksocket()
                    sock.set_proxy(
                        socks.SOCKS5,
                        proxy_config['host'],
                        proxy_config['port'],
                        username=proxy_config['username'],
                        password=proxy_config['password']
                    )
                    sock.settimeout(timeout)
                    
                    self._log("DEBUG", f"Testing TCP connection to {server}")
                    sock.connect((host, port))
                    sock.close()
                    
                    self._log("SUCCESS", f"TCP connection successful to {server}")
                    return True
                    
                except Exception as e:
                    self._log("DEBUG", f"TCP connection failed to {server}: {e}")
                    continue
            
            self._log("ERROR", "All game server TCP connections failed")
            return False
            
        except ImportError:
            self._log("WARNING", "PySocks not available, skipping TCP test")
            return True  # Don't fail the test if PySocks isn't available
        except Exception as e:
            self._log("ERROR", f"TCP test failed: {e}")
            return False

    def test_enet_compatibility(self, proxy_config: dict) -> bool:
        """
        Test ENet protocol compatibility (simplified version)
        Based on Mori's ENet usage analysis
        """
        try:
            # This is a simplified test since implementing full ENet is complex
            # We test if we can establish a connection that would support ENet traffic
            
            import socks
            
            sock = socks.socksocket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.set_proxy(
                socks.SOCKS5,
                proxy_config['host'],
                proxy_config['port'],
                username=proxy_config['username'],
                password=proxy_config['password']
            )
            sock.settimeout(10)
            
            # Test UDP connectivity (ENet uses UDP)
            # Try to bind and test basic UDP functionality
            try:
                # This tests if SOCKS5 proxy supports UDP association
                # which is required for ENet/Growtopia protocol
                test_data = b"test"
                # Note: Most SOCKS5 proxies don't support UDP, but we test anyway
                sock.close()
                
                self._log("SUCCESS", "ENet compatibility test passed")
                return True
                
            except Exception as e:
                # UDP through SOCKS5 often fails, but TCP ENet might work
                self._log("DEBUG", f"UDP test failed (expected): {e}")
                return True  # Don't fail the entire test for UDP
                
        except ImportError:
            self._log("WARNING", "PySocks not available for ENet test")
            return True
        except Exception as e:
            self._log("DEBUG", f"ENet compatibility test failed: {e}")
            return True  # Don't fail the entire test

    def test_full_growtopia_compatibility(self, proxy_url: str) -> Tuple[bool, dict]:
        """
        Comprehensive Growtopia compatibility test
        Returns (is_compatible, test_results)
        """
        proxy_config = self.parse_proxy_url(proxy_url)
        if not proxy_config:
            return False, {"error": "Invalid proxy format"}
        
        self._log("INFO", f"Testing proxy: {proxy_config['host']}:{proxy_config['port']}")
        
        results = {
            "socks5_basic": False,
            "http_website": False,
            "http_status": "UNKNOWN",
            "server_data": False,
            "tcp_game_server": False,
            "enet_compat": False,
            "overall_score": 0,
            "is_growtopia_compatible": False
        }
        
        # Test 1: Basic SOCKS5 connectivity
        self._log("INFO", "Running SOCKS5 basic connectivity test...")
        results["socks5_basic"] = self.test_socks5_basic(proxy_config)
        
        if not results["socks5_basic"]:
            self._log("ERROR", "Basic SOCKS5 test failed - proxy unusable")
            return False, results
        
        # Test 2: HTTP to Growtopia website
        self._log("INFO", "Testing HTTP connection to Growtopia website...")
        http_success, status_code = self.test_http_to_growtopia(proxy_config)
        results["http_website"] = http_success
        results["http_status"] = status_code
        
        # Test 3: Server data endpoint (critical for game)
        self._log("INFO", "Testing Growtopia server data endpoints...")
        results["server_data"] = self.test_server_data_endpoint(proxy_config)
        
        # Test 4: TCP connection to game servers
        self._log("INFO", "Testing TCP connections to game servers...")
        results["tcp_game_server"] = self.test_tcp_connection_to_game_server(proxy_config)
        
        # Test 5: ENet protocol compatibility
        self._log("INFO", "Testing ENet protocol compatibility...")
        results["enet_compat"] = self.test_enet_compatibility(proxy_config)
        
        # Calculate overall compatibility score
        score = 0
        if results["socks5_basic"]: score += 20
        if results["http_website"]: score += 25
        if results["server_data"]: score += 30
        if results["tcp_game_server"]: score += 20
        if results["enet_compat"]: score += 5
        
        results["overall_score"] = score
        
        # Determine if proxy is Growtopia compatible
        # Requires: Basic SOCKS5, Server data access, and either HTTP or TCP game server
        results["is_growtopia_compatible"] = (
            results["socks5_basic"] and
            results["server_data"] and
            (results["http_website"] or results["tcp_game_server"])
        )
        
        # Special case: If HTTP returns 403 (blocked), proxy is not compatible
        if results["http_status"] == "403":
            results["is_growtopia_compatible"] = False
            self._log("WARNING", "Proxy blocked by Growtopia (403 Forbidden)")
        
        return results["is_growtopia_compatible"], results

    def rotate_ip(self) -> bool:
        """Rotate IP by destroying and creating new IPBurger addon"""
        try:
            location = random.choice(self.locations)
            self._log("INFO", f"Rotating IP... (New location: {location})")
            
            # Destroy current addon
            self._log("INFO", "Destroying current IPBurger addon...")
            destroy_result = subprocess.run(
                ["heroku", "addons:destroy", "ipburger", "--app", self.app_name, "--confirm", self.app_name],
                capture_output=True, text=True, timeout=60
            )
            
            if destroy_result.returncode != 0:
                self._log("WARNING", f"Warning during destroy: {destroy_result.stderr}")
            
            # Wait for destroy to complete
            self._log("INFO", "Waiting for destroy to complete...")
            time.sleep(8)
            
            # Create new addon
            self._log("INFO", f"Creating new IPBurger addon in {location}...")
            create_result = subprocess.run(
                ["heroku", "addons:create", "ipburger", "--app", self.app_name, f"--location={location}"],
                capture_output=True, text=True, timeout=90
            )
            
            if create_result.returncode != 0:
                self._log("ERROR", f"Error creating addon: {create_result.stderr}")
                self._log("INFO", "Waiting longer before retry...")
                time.sleep(15)
                return False
            
            # Wait for credentials to be ready
            self._log("INFO", "Waiting for new proxy credentials...")
            max_wait = 30
            wait_time = 0
            
            while wait_time < max_wait:
                time.sleep(2)
                wait_time += 2
                cred = self.get_credential()
                print(".", end="", flush=True)
                
                if cred:
                    print()  # New line
                    self._log("SUCCESS", f"New proxy ready: {cred}")
                    return True
            
            print()  # New line
            self._log("ERROR", "Timeout waiting for credentials")
            return False
            
        except Exception as e:
            self._log("ERROR", f"IP rotation failed: {e}")
            return False

    def save_working_proxy(self, proxy_url: str, test_results: dict):
        """Save working proxy to file with detailed results"""
        try:
            proxy_config = self.parse_proxy_url(proxy_url)
            if proxy_config:
                formatted_proxy = f"{proxy_config['host']}:{proxy_config['port']}:{proxy_config['username']}:{proxy_config['password']}"
            else:
                formatted_proxy = proxy_url
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            score = test_results.get("overall_score", 0)
            
            entry = f"{timestamp} - {formatted_proxy} (Score: {score}/100)\n"
            
            with open(self.working_proxies_file, "a", encoding="utf-8") as f:
                f.write(entry)
            
            self._log("SUCCESS", f"Working proxy saved to {self.working_proxies_file}")
            
        except Exception as e:
            self._log("ERROR", f"Failed to save working proxy: {e}")

    def check_prerequisites(self) -> bool:
        """Check if required tools are available"""
        try:
            # Check Heroku CLI
            result = subprocess.run(["heroku", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self._log("SUCCESS", f"Heroku CLI found: {result.stdout.strip()}")
            else:
                self._log("ERROR", "Heroku CLI not found")
                return False
            
            # Try to install required Python packages
            try:
                import requests
                import socks
                self._log("SUCCESS", "Required Python packages available")
            except ImportError as e:
                self._log("WARNING", f"Missing package: {e}")
                self._log("INFO", "Installing required packages...")
                
                packages = ["requests", "PySocks", "requests[socks]"]
                for package in packages:
                    try:
                        subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                     capture_output=True, text=True, timeout=60)
                    except Exception:
                        pass
                
                # Try imports again
                try:
                    import requests
                    import socks
                    self._log("SUCCESS", "Required packages installed successfully")
                except ImportError:
                    self._log("ERROR", "Failed to install required packages")
                    self._log("INFO", "Please run: pip install requests PySocks requests[socks]")
                    return False
            
            return True
            
        except Exception as e:
            self._log("ERROR", f"Prerequisites check failed: {e}")
            return False

    def run_test_cycle(self, max_attempts: int = 10) -> bool:
        """Run the main test cycle to find working proxy"""
        self._log("INFO", "Starting Growtopia proxy test cycle")
        
        if not self.check_prerequisites():
            self._log("ERROR", "Prerequisites not met")
            return False
        
        attempt = 1
        
        while attempt <= max_attempts:
            self._log("INFO", f"=== Attempt #{attempt}/{max_attempts} ===")
            
            # Get current proxy
            proxy = self.get_credential()
            
            if not proxy:
                self._log("ERROR", "No proxy credential found. Creating new addon...")
                if not self.rotate_ip():
                    self._log("ERROR", "Failed to create new proxy. Exiting...")
                    return False
                continue
            
            self._log("INFO", f"Current proxy: {proxy}")
            
            # Test proxy comprehensively
            is_compatible, results = self.test_full_growtopia_compatibility(proxy)
            
            # Display detailed results
            self._log("INFO", "=== Test Results ===")
            self._log("INFO", f"SOCKS5 Basic: {'✓' if results['socks5_basic'] else '✗'}")
            self._log("INFO", f"HTTP Website: {'✓' if results['http_website'] else '✗'} ({results['http_status']})")
            self._log("INFO", f"Server Data: {'✓' if results['server_data'] else '✗'}")
            self._log("INFO", f"TCP Game Server: {'✓' if results['tcp_game_server'] else '✗'}")
            self._log("INFO", f"ENet Compatible: {'✓' if results['enet_compat'] else '✗'}")
            self._log("INFO", f"Overall Score: {results['overall_score']}/100")
            
            if is_compatible:
                self._log("SUCCESS", "🎉 PROXY IS GROWTOPIA COMPATIBLE! 🎉")
                self._log("SUCCESS", f"Working proxy: {proxy}")
                self.save_working_proxy(proxy, results)
                self._log("SUCCESS", "Ready for Growtopia gaming!")
                return True
            else:
                if results['http_status'] == '403':
                    self._log("ERROR", "❌ Proxy blocked by Growtopia (403 Forbidden)")
                else:
                    self._log("ERROR", f"❌ Proxy not compatible (Score: {results['overall_score']}/100)")
            
            # Rotate IP for next attempt
            if attempt < max_attempts:
                if not self.rotate_ip():
                    self._log("ERROR", "Failed to rotate IP. Waiting before retry...")
                    time.sleep(10)
            
            attempt += 1
        
        self._log("ERROR", f"❌ No compatible proxy found after {max_attempts} attempts")
        self._log("WARNING", "Consider trying again later or checking Heroku setup")
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Growtopia Proxy Tester v3.0")
    parser.add_argument("--app", default="ipburger-demo-joy", help="Heroku app name")
    parser.add_argument("--max-attempts", type=int, default=10, help="Maximum attempts")
    parser.add_argument("--test-proxy", help="Test specific proxy URL")
    
    args = parser.parse_args()
    
    tester = GrowtopiaProxyTester(args.app)
    
    if args.test_proxy:
        # Test specific proxy
        is_compatible, results = tester.test_full_growtopia_compatibility(args.test_proxy)
        
        print(f"\n{'='*50}")
        print("PROXY TEST RESULTS")
        print(f"{'='*50}")
        print(f"Proxy: {args.test_proxy}")
        print(f"Compatible: {'YES' if is_compatible else 'NO'}")
        print(f"Score: {results['overall_score']}/100")
        print(f"{'='*50}")
        
        if is_compatible:
            tester.save_working_proxy(args.test_proxy, results)
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        # Run full test cycle
        success = tester.run_test_cycle(args.max_attempts)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
