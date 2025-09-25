#!/usr/bin/env python3
"""
Test script for FastAPI endpoints
"""

import sys
import os
import httpx
import asyncio
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# API base URL
BASE_URL = "http://localhost:8000"


class APITester:
    """Test FastAPI endpoints"""

    def __init__(self):
        self.client = httpx.Client(base_url=BASE_URL, timeout=30.0)
        self.test_results = []

    def test_endpoint(self, name: str, method: str, path: str, **kwargs) -> bool:
        """Test a single endpoint"""
        try:
            print(f"\n🧪 Testing: {name}")
            print(f"   {method} {path}")

            response = self.client.request(method, path, **kwargs)

            if response.status_code < 400:
                print(f"   ✅ Success: {response.status_code}")
                self.test_results.append((name, True, None))
                return True
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
                self.test_results.append((name, False, f"Status {response.status_code}"))
                return False

        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results.append((name, False, str(e)))
            return False

    def run_tests(self):
        """Run all API tests"""
        print("\n" + "="*60)
        print("FastAPI Endpoint Tests")
        print("="*60)

        # Test root endpoint
        self.test_endpoint("Root Endpoint", "GET", "/")

        # Test health check
        self.test_endpoint("Health Check", "GET", "/health")

        # Test Connecticut Towns endpoints
        print("\n📍 Connecticut Towns Endpoints")
        self.test_endpoint("List Towns", "GET", "/api/v1/towns/")
        self.test_endpoint("List Counties", "GET", "/api/v1/towns/counties")
        self.test_endpoint("Validate Town", "GET", "/api/v1/towns/validate/Middletown")
        self.test_endpoint("Search Towns", "GET", "/api/v1/towns/search", params={"q": "Hart"})
        self.test_endpoint("Get Towns by County", "GET", "/api/v1/towns/by-county/Hartford")

        # Test Cases endpoints
        print("\n📋 Cases Endpoints")
        self.test_endpoint("List Cases", "GET", "/api/v1/cases/", params={"skip": 0, "limit": 5})
        self.test_endpoint("Search Cases", "GET", "/api/v1/cases/search", params={"q": "test"})
        self.test_endpoint("Get Cases by Town", "GET", "/api/v1/cases/by-town/Middletown")

        # Test Defendants endpoints
        print("\n👥 Defendants Endpoints")
        self.test_endpoint("List Defendants", "GET", "/api/v1/defendants/", params={"skip": 0, "limit": 5})

        # Test Skip Traces endpoints
        print("\n📞 Skip Traces Endpoints")
        self.test_endpoint("Skip Trace History", "GET", "/api/v1/skiptraces/history", params={"skip": 0, "limit": 5})
        self.test_endpoint("Skip Trace Costs", "GET", "/api/v1/skiptraces/costs")

        # Test Scraper endpoints
        print("\n🔍 Scraper Endpoints")
        self.test_endpoint("Scraper History", "GET", "/api/v1/scraper/history")

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)

        passed = sum(1 for _, success, _ in self.test_results if success)
        failed = len(self.test_results) - passed

        print(f"\nTotal Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")

        if failed > 0:
            print("\nFailed Tests:")
            for name, success, error in self.test_results:
                if not success:
                    print(f"  - {name}: {error}")

        success_rate = (passed / len(self.test_results)) * 100 if self.test_results else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")

        if success_rate == 100:
            print("\n🎉 All tests passed!")
        elif success_rate >= 80:
            print("\n⚠️  Most tests passed, but some issues need attention.")
        else:
            print("\n❌ Multiple test failures. Please check the API.")


async def test_async_endpoints():
    """Test async endpoints"""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Test async endpoint
        response = await client.get("/health")
        print(f"Async Health Check: {response.status_code}")


def main():
    """Main test function"""
    print("\n🚀 Starting FastAPI Tests")
    print("   Make sure the API is running on http://localhost:8000")
    print("   Run with: python run_api.py")

    # Check if API is running
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=5.0)
        if response.status_code == 200:
            print("\n✅ API is running!")
        else:
            print(f"\n⚠️  API returned status {response.status_code}")
    except Exception as e:
        print(f"\n❌ Cannot connect to API: {e}")
        print("   Please start the API first with: python run_api.py")
        return

    # Run tests
    tester = APITester()
    tester.run_tests()

    # Run async tests
    print("\n🔄 Testing async endpoints...")
    asyncio.run(test_async_endpoints())

    print("\n✨ Testing complete!")


if __name__ == "__main__":
    main()