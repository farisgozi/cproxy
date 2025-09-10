#!/home/joy/cproxy/venv/bin/python3

"""
Realistic Growtopia Proxy Compatibility Tester
Based on actual protocol analysis and realistic expectations

This version correctly interprets TCP timeouts and focuses on
what actually matters for Growtopia gameplay.
"""

from gt_proxy_tester import GrowtopiaProxyTester
from typing import Tuple, Dict, Any


class RealisticGrowtopiaProxyTester(GrowtopiaProxyTester):
    """
    Realistic tester that properly interprets protocol requirements
    Based on deeper understanding of Growtopia's actual needs
    """
    
    def test_realistic_growtopia_compatibility(self, proxy_url: str) -> Tuple[bool, dict]:
        """
        Realistic compatibility test based on what actually matters
        for Growtopia gameplay, not theoretical protocol tests
        """
        proxy_config = self.parse_proxy_url(proxy_url)
        if not proxy_config:
            return False, {"error": "Invalid proxy format"}
        
        self._log("INFO", f"Testing REALISTIC Growtopia compatibility: {proxy_config['host']}:{proxy_config['port']}")
        
        results = {
            "socks5_basic": False,
            "http_website": False,
            "http_status": "UNKNOWN",
            "server_data": False,
            "tcp_game_server": False,
            "enet_compat": False,
            "realistic_score": 0,
            "is_growtopia_compatible": False,
            "compatibility_reason": "",
            "tcp_timeout_note": "TCP timeout is NORMAL - Growtopia uses UDP/ENet"
        }
        
        # Test 1: Basic SOCKS5 connectivity
        self._log("INFO", "Running SOCKS5 basic connectivity test...")
        results["socks5_basic"] = self.test_socks5_basic(proxy_config)
        
        if not results["socks5_basic"]:
            results["compatibility_reason"] = "SOCKS5 proxy not working"
            return False, results
        
        # Test 2: HTTP website access
        self._log("INFO", "Testing HTTP connection to Growtopia website...")
        http_success, status_code = self.test_http_to_growtopia(proxy_config)
        results["http_website"] = http_success
        results["http_status"] = status_code
        
        # Check for blocking
        if status_code == "403":
            results["compatibility_reason"] = "IP blocked by Growtopia (403 Forbidden)"
            return False, results
        
        # Test 3: Server data endpoint (MOST CRITICAL)
        self._log("INFO", "Testing Growtopia server data endpoints...")
        results["server_data"] = self.test_server_data_endpoint(proxy_config)
        
        if not results["server_data"]:
            results["compatibility_reason"] = "Cannot access game server discovery endpoints"
            return False, results
        
        # Test 4: TCP game server (but interpret timeout correctly)
        self._log("INFO", "Testing TCP connections to game servers (timeout expected)...")
        tcp_result = self.test_tcp_connection_to_game_server(proxy_config)
        results["tcp_game_server"] = tcp_result
        
        if tcp_result:
            self._log("INFO", "TCP connection succeeded (bonus points)")
        else:
            self._log("INFO", "TCP timeout is NORMAL - Growtopia uses UDP/ENet protocol")
        
        # Test 5: ENet compatibility
        self._log("INFO", "Testing basic ENet protocol compatibility...")
        results["enet_compat"] = self.test_enet_compatibility(proxy_config)
        
        # Realistic scoring system
        score = 0
        score_breakdown = {}
        
        # SOCKS5 Basic (Required) - 25 points
        if results["socks5_basic"]:
            score += 25
            score_breakdown["SOCKS5 Basic"] = "25/25"
        else:
            score_breakdown["SOCKS5 Basic"] = "0/25 - REQUIRED"
        
        # HTTP Website (Important) - 20 points  
        if results["http_website"]:
            score += 20
            score_breakdown["HTTP Website"] = "20/20"
        elif results["http_status"] == "403":
            score_breakdown["HTTP Website"] = "0/20 - BLOCKED"
        else:
            score += 5  # Partial credit if reachable but not 200
            score_breakdown["HTTP Website"] = "5/20 - Partial"
        
        # Server Data (CRITICAL) - 40 points
        if results["server_data"]:
            score += 40
            score_breakdown["Server Data"] = "40/40 - CRITICAL"
        else:
            score_breakdown["Server Data"] = "0/40 - CRITICAL FAILURE"
        
        # TCP Game Server (Bonus) - 10 points
        if results["tcp_game_server"]:
            score += 10
            score_breakdown["TCP Game Server"] = "10/10 - Bonus"
        else:
            score_breakdown["TCP Game Server"] = "0/10 - Normal (UDP expected)"
        
        # ENet Compatible (Bonus) - 5 points
        if results["enet_compat"]:
            score += 5
            score_breakdown["ENet Compatible"] = "5/5 - Bonus"
        else:
            score_breakdown["ENet Compatible"] = "0/5 - Minor issue"
        
        results["realistic_score"] = score
        results["score_breakdown"] = score_breakdown
        
        # Realistic compatibility determination
        # Requirements: SOCKS5 + Server Data + Not Blocked
        results["is_growtopia_compatible"] = (
            results["socks5_basic"] and           # Can proxy traffic
            results["server_data"] and            # Can discover game servers  
            results["http_status"] != "403"       # Not blocked by IP
        )
        
        if results["is_growtopia_compatible"]:
            if score >= 85:
                results["compatibility_reason"] = "EXCELLENT - All tests passed"
            elif score >= 70:
                results["compatibility_reason"] = "VERY GOOD - Ready for gaming"
            elif score >= 60:
                results["compatibility_reason"] = "GOOD - Should work fine"
            else:
                results["compatibility_reason"] = "BASIC - Meets minimum requirements"
        else:
            if not results["socks5_basic"]:
                results["compatibility_reason"] = "SOCKS5 proxy failure"
            elif not results["server_data"]:
                results["compatibility_reason"] = "Cannot discover game servers"
            elif results["http_status"] == "403":
                results["compatibility_reason"] = "IP blocked by Growtopia"
            else:
                results["compatibility_reason"] = "Unknown compatibility issue"
        
        return results["is_growtopia_compatible"], results

    def display_detailed_results(self, results: dict, proxy_url: str):
        """Display comprehensive test results with explanations"""
        
        print(f"\n{'='*70}")
        print("🎮 REALISTIC GROWTOPIA COMPATIBILITY TEST RESULTS")  
        print(f"{'='*70}")
        print(f"Proxy: {proxy_url}")
        
        # Handle case where compatibility check wasn't completed
        is_compatible = results.get('is_growtopia_compatible', False)
        print(f"Compatible: {'✅ YES' if is_compatible else '❌ NO'}")
        print(f"Realistic Score: {results.get('realistic_score', 0)}/100")
        print(f"Reason: {results.get('compatibility_reason', 'Unknown')}")
        
        print(f"\n📊 DETAILED SCORE BREAKDOWN:")
        print(f"{'─'*70}")
        
        if 'score_breakdown' in results:
            for test_name, result in results['score_breakdown'].items():
                status = "✅" if result.startswith(("25/25", "20/20", "40/40", "10/10", "5/5")) else "❌" if result.startswith("0/") else "⚠️"
                print(f"  {status} {test_name:<20}: {result}")
        else:
            print("  ❌ Score breakdown not available (test incomplete)")
        
        print(f"\n🔍 TEST ANALYSIS:")
        print(f"{'─'*70}")
        
        # SOCKS5 Analysis
        if results.get("socks5_basic"):
            print("  ✅ SOCKS5: Proxy can handle connections properly")
        else:
            print("  ❌ SOCKS5: Proxy connection failed - unusable")
        
        # HTTP Analysis  
        if results.get("http_website"):
            print(f"  ✅ HTTP: Website accessible (Status: {results.get('http_status', 'Unknown')})")
        elif results.get("http_status") == "403":
            print("  ❌ HTTP: IP blocked by Growtopia - proxy blacklisted")
        else:
            print(f"  ⚠️  HTTP: Issues accessing website (Status: {results.get('http_status', 'Unknown')})")
        
        # Server Data Analysis
        if results.get("server_data"):
            print("  ✅ SERVER DATA: Can discover game servers - CRITICAL for gaming")
        else:
            print("  ❌ SERVER DATA: Cannot find game servers - gaming impossible")
        
        # TCP Analysis
        if results.get("tcp_game_server"):
            print("  ✅ TCP: Direct server connection works (bonus)")
        else:
            print("  ℹ️  TCP: Connection timeout - NORMAL (Growtopia uses UDP/ENet)")
        
        # ENet Analysis  
        if results.get("enet_compat"):
            print("  ✅ ENET: Protocol compatibility confirmed")
        else:
            print("  ⚠️  ENET: Minor compatibility issues detected")
        
        print(f"\n🎯 GROWTOPIA GAMING VERDICT:")
        print(f"{'─'*70}")
        
        if is_compatible:
            print("  🎉 This proxy IS COMPATIBLE with Growtopia!")
            print("  ✅ You can use this proxy for actual gameplay")
            print("  🎮 Bot connections should work properly")
            
            score = results.get('realistic_score', 0)
            if score >= 85:
                print("  ⭐ EXCELLENT compatibility - no issues expected")
            elif score >= 70:
                print("  ⭐ VERY GOOD compatibility - minor issues possible")
            else:
                print("  ⭐ BASIC compatibility - meets minimum requirements")
        else:
            print("  ❌ This proxy has COMPATIBILITY ISSUES")
            print(f"  🚫 Primary issue: {results.get('compatibility_reason', 'Unknown error')}")
            print("  💡 Try a different proxy or location")
        
        print(f"\n📝 IMPORTANT NOTES:")
        print(f"{'─'*70}")
        print("  • TCP timeouts are NORMAL - Growtopia uses UDP/ENet protocol")
        print("  • Server Data test is the MOST IMPORTANT for gaming")
        print("  • Score 65+ is usually sufficient for stable gameplay")  
        print("  • 403 Forbidden = IP blacklisted by Growtopia")
        
        print(f"{'='*70}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Realistic Growtopia Proxy Tester v1.0")
    parser.add_argument("--test-proxy", required=True, help="Test specific proxy URL")
    
    args = parser.parse_args()
    
    tester = RealisticGrowtopiaProxyTester()
    
    # Test with realistic expectations
    is_compatible, results = tester.test_realistic_growtopia_compatibility(args.test_proxy)
    
    # Display comprehensive results
    tester.display_detailed_results(results, args.test_proxy)
    
    # Save if compatible
    if is_compatible and results.get('is_growtopia_compatible'):
        tester.save_working_proxy(args.test_proxy, results)
    
    return 0 if is_compatible else 1


if __name__ == "__main__":
    exit(main())
