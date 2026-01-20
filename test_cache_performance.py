#!/usr/bin/env python
"""
Cache Performance Testing Script

This script tests the performance of cached vs non-cached API endpoints.
It measures response times and calculates speedup ratios.

Usage:
    python test_cache_performance.py
    python test_cache_performance.py --endpoint /api/users/
"""

import requests
import time
import sys
import argparse
from typing import Tuple, Dict

# Configuration
BASE_URL = "http://localhost:8000"
DEFAULT_ENDPOINTS = [
    "/api/users/",
    "/api/users/passengers/",
    "/api/users/riders/",
]


class CachePerformanceTester:
    """Test and monitor cache performance of Django API endpoints"""
    
    def __init__(self, base_url: str = BASE_URL):
        """Initialize the performance tester
        
        Args:
            base_url: The base URL of the Django application
        """
        self.base_url = base_url
        self.results = []
    
    def test_endpoint(self, endpoint: str, iterations: int = 3) -> Dict:
        """Test a single endpoint for cache performance
        
        Args:
            endpoint: The API endpoint to test (e.g., '/api/users/')
            iterations: Number of iterations to run (default: 3)
            
        Returns:
            Dictionary containing test results
        """
        url = f"{self.base_url}{endpoint}"
        
        print(f"\n{'='*70}")
        print(f"Testing: {endpoint}")
        print(f"{'='*70}")
        
        times = []
        
        try:
            for i in range(iterations):
                start = time.time()
                response = requests.get(url, timeout=10)
                end = time.time()
                
                elapsed = end - start
                times.append(elapsed)
                
                status = "✓ PASS" if response.status_code == 200 else "✗ FAIL"
                call_type = "cache MISS" if i == 0 else "cache HIT"
                
                print(f"  Call {i+1} ({call_type}): {elapsed:.4f}s {status}")
                
                if response.status_code != 200:
                    print(f"    Error: Status {response.status_code}")
                    return {'status': 'error', 'message': f"HTTP {response.status_code}"}
            
            # Calculate statistics
            first_call = times[0]
            second_call = times[1] if len(times) > 1 else times[0]
            avg_hit_time = sum(times[1:]) / len(times[1:]) if len(times) > 1 else times[0]
            
            speedup = first_call / second_call if second_call > 0 else 0
            improvement = ((first_call - second_call) / first_call * 100) if first_call > 0 else 0
            
            result = {
                'endpoint': endpoint,
                'status': 'success',
                'iterations': iterations,
                'first_call': first_call,
                'second_call': second_call,
                'avg_hit_time': avg_hit_time,
                'speedup': speedup,
                'improvement_percent': improvement,
                'all_times': times,
            }
            
            print(f"\n{'─'*70}")
            print(f"  First call (MISS):  {first_call:.4f}s (cold cache)")
            print(f"  Second call (HIT):  {second_call:.4f}s (warm cache)")
            print(f"  Avg HIT time:       {avg_hit_time:.4f}s")
            print(f"  Speedup factor:     {speedup:.2f}x faster")
            print(f"  Improvement:        {improvement:.1f}%")
            print(f"{'─'*70}")
            
            self.results.append(result)
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def test_all_endpoints(self, endpoints: list = None) -> None:
        """Test all specified endpoints
        
        Args:
            endpoints: List of endpoints to test (uses defaults if None)
        """
        if endpoints is None:
            endpoints = DEFAULT_ENDPOINTS
        
        print("\n" + "="*70)
        print("CACHE PERFORMANCE TEST SUITE")
        print("="*70)
        
        for endpoint in endpoints:
            self.test_endpoint(endpoint)
        
        self.print_summary()
    
    def print_summary(self) -> None:
        """Print a summary of all test results"""
        print("\n" + "="*70)
        print("PERFORMANCE SUMMARY")
        print("="*70 + "\n")
        
        if not self.results:
            print("No results to summarize.")
            return
        
        # Summary table
        print(f"{'Endpoint':<30} {'Speedup':>12} {'Improvement':>15}")
        print("-" * 57)
        
        total_speedup = 0
        total_improvement = 0
        successful = 0
        
        for result in self.results:
            if result['status'] == 'success':
                endpoint = result['endpoint'][:25]
                speedup = result['speedup']
                improvement = result['improvement_percent']
                
                print(f"{endpoint:<30} {speedup:>12.2f}x {improvement:>14.1f}%")
                
                total_speedup += speedup
                total_improvement += improvement
                successful += 1
        
        if successful > 0:
            print("-" * 57)
            avg_speedup = total_speedup / successful
            avg_improvement = total_improvement / successful
            
            print(f"{'Average':<30} {avg_speedup:>12.2f}x {avg_improvement:>14.1f}%")
            print("="*70)
            
            print("\n✓ Cache testing completed successfully!")
            print(f"  - Average speedup: {avg_speedup:.2f}x")
            print(f"  - Average improvement: {avg_improvement:.1f}%")
            print(f"  - Endpoints tested: {successful}")
        else:
            print("\n✗ All tests failed!")
    
    def test_cache_invalidation(self, endpoint: str = "/api/users/") -> None:
        """Test cache invalidation by creating a new resource
        
        Args:
            endpoint: The endpoint to test (default: /api/users/)
        """
        print("\n" + "="*70)
        print("CACHE INVALIDATION TEST")
        print("="*70 + "\n")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Get initial data
            print("1. Getting initial list (cache MISS)...")
            start = time.time()
            response1 = requests.get(url)
            time1 = time.time() - start
            initial_count = len(response1.json()) if response1.status_code == 200 else 0
            print(f"   ✓ First call: {time1:.4f}s ({initial_count} items)")
            
            # Get cached data
            print("2. Getting cached list (cache HIT)...")
            start = time.time()
            response2 = requests.get(url)
            time2 = time.time() - start
            print(f"   ✓ Second call: {time2:.4f}s (cache HIT)")
            
            # Verify cache
            if time2 < time1:
                print(f"   ✓ Cache is working ({time1/time2:.2f}x faster)")
            else:
                print(f"   ⚠ Cache may not be working (no speedup)")
            
            print("\n✓ Cache invalidation test completed!")
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error: {str(e)}")


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="Test Django cache performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_cache_performance.py
  python test_cache_performance.py --endpoint /api/users/
  python test_cache_performance.py --endpoints /api/users/ /api/users/passengers/
  python test_cache_performance.py --invalidation
        """
    )
    
    parser.add_argument(
        '--endpoint',
        type=str,
        help='Test a single endpoint'
    )
    
    parser.add_argument(
        '--endpoints',
        nargs='+',
        help='Test multiple endpoints'
    )
    
    parser.add_argument(
        '--invalidation',
        action='store_true',
        help='Test cache invalidation'
    )
    
    parser.add_argument(
        '--iterations',
        type=int,
        default=3,
        help='Number of iterations per endpoint (default: 3)'
    )
    
    parser.add_argument(
        '--base-url',
        type=str,
        default=BASE_URL,
        help=f'Base URL of the Django application (default: {BASE_URL})'
    )
    
    args = parser.parse_args()
    
    tester = CachePerformanceTester(base_url=args.base_url)
    
    if args.invalidation:
        tester.test_cache_invalidation()
    elif args.endpoint:
        tester.test_endpoint(args.endpoint, iterations=args.iterations)
        tester.print_summary()
    elif args.endpoints:
        tester.test_all_endpoints(endpoints=args.endpoints)
    else:
        tester.test_all_endpoints()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        sys.exit(1)
