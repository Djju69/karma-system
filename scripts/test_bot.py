#!/usr/bin/env python3
"""
Automated testing script for Karma System Bot
"""
import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.database import get_db, init_db
from app.core.services.qr_service import qr_service
from app.core.services.partners_service import partners_service
from app.core.services.catalog_service import catalog_service
from app.core.cache import cache_service

class BotTester:
    def __init__(self):
        self.results = []
        
    def log_test(self, test_name, status, details=""):
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    async def test_database_connection(self):
        """Test database connectivity"""
        try:
            async for db in get_db():
                await db.execute("SELECT 1")
                self.log_test("Database Connection", "PASS")
                break
        except Exception as e:
            self.log_test("Database Connection", "FAIL", str(e))
    
    async def test_redis_connection(self):
        """Test Redis connectivity"""
        try:
            await cache_service.set("test_key", "test_value", 10)
            value = await cache_service.get("test_key")
            if value == "test_value":
                self.log_test("Redis Connection", "PASS")
            else:
                self.log_test("Redis Connection", "FAIL", "Value mismatch")
        except Exception as e:
            self.log_test("Redis Connection", "FAIL", str(e))
    
    async def test_qr_service(self):
        """Test QR code generation and validation"""
        try:
            async for db in get_db():
                # Create test QR
                qr_data = await qr_service.create_qr(db, listing_id=1, user_id=1)
                if qr_data:
                    # Test validation
                    qr_issue = await qr_service.get_qr_by_jti(db, qr_data["jti"])
                    if qr_issue:
                        self.log_test("QR Service", "PASS", f"JTI: {qr_data['jti']}")
                    else:
                        self.log_test("QR Service", "FAIL", "QR validation failed")
                else:
                    self.log_test("QR Service", "FAIL", "QR creation failed")
                break
        except Exception as e:
            self.log_test("QR Service", "FAIL", str(e))
    
    async def test_partner_service(self):
        """Test partner application creation"""
        try:
            async for db in get_db():
                result = await partners_service.create_application(
                    db=db,
                    user_id=1,
                    contact_name="Test Partner",
                    contact_phone="+1234567890",
                    business_name="Test Business",
                    business_address="Test Address",
                    city_id=1,
                    category="restaurants",
                    description="Test description"
                )
                if result and result.get("id"):
                    self.log_test("Partner Service", "PASS", f"Application ID: {result['id']}")
                else:
                    self.log_test("Partner Service", "FAIL", "Application creation failed")
                break
        except Exception as e:
            self.log_test("Partner Service", "FAIL", str(e))
    
    async def test_catalog_service(self):
        """Test catalog listing retrieval"""
        try:
            async for db in get_db():
                result = await catalog_service.get_listings(
                    db=db,
                    city_id=1,
                    category="restaurants",
                    page=1,
                    per_page=5
                )
                if "listings" in result:
                    self.log_test("Catalog Service", "PASS", f"Found {len(result['listings'])} listings")
                else:
                    self.log_test("Catalog Service", "FAIL", "No listings returned")
                break
        except Exception as e:
            self.log_test("Catalog Service", "FAIL", str(e))
    
    def test_environment_variables(self):
        """Test required environment variables"""
        required_vars = [
            "BOT_TOKEN", "DATABASE_URL", "FERNET_KEY_HEX",
            "DEFAULT_LANG", "DEFAULT_CITY_SLUG"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.log_test("Environment Variables", "FAIL", f"Missing: {', '.join(missing_vars)}")
        else:
            self.log_test("Environment Variables", "PASS")
    
    def test_i18n_files(self):
        """Test internationalization files"""
        languages = ["ru", "en", "vi", "ko"]
        i18n_dir = Path(__file__).parent.parent / "app" / "bot" / "i18n"
        
        missing_files = []
        for lang in languages:
            file_path = i18n_dir / f"{lang}.json"
            if not file_path.exists():
                missing_files.append(f"{lang}.json")
        
        if missing_files:
            self.log_test("I18n Files", "FAIL", f"Missing: {', '.join(missing_files)}")
        else:
            self.log_test("I18n Files", "PASS")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting Karma System Bot Tests...")
        print("=" * 50)
        
        # Environment tests
        self.test_environment_variables()
        self.test_i18n_files()
        
        # Service tests
        await self.test_database_connection()
        await self.test_redis_connection()
        await self.test_qr_service()
        await self.test_partner_service()
        await self.test_catalog_service()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Summary:")
        
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])
        warnings = len([r for r in self.results if r["status"] == "WARNING"])
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Warnings: {warnings}")
        print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
        
        # Save results
        results_file = Path(__file__).parent / "test_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Results saved to: {results_file}")
        
        return failed == 0

async def main():
    """Main test runner"""
    tester = BotTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Bot is ready for testing.")
        print("\n📋 Next steps:")
        print("1. Test /start command in Telegram")
        print("2. Test language switching")
        print("3. Test partner registration FSM")
        print("4. Test QR code generation")
        print("5. Test catalog browsing")
    else:
        print("\n⚠️ Some tests failed. Please fix issues before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
