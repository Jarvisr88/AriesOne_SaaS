import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import asyncio
from datetime import datetime
from integration.billing_system import BillingSystemIntegration
from integration.reporting_system import ReportingSystemIntegration

class TestEndToEnd:
    """End-to-end tests for Controls module"""

    @pytest.fixture
    async def setup(self):
        """Setup test environment and dependencies"""
        # Initialize services
        self.billing = BillingSystemIntegration(
            db_url="postgresql://test:test@localhost/test_db",
            api_base_url="https://test.billing.com/v1",
            api_key="test-api-key"
        )
        self.reporting = ReportingSystemIntegration(
            db_url="postgresql://test:test@localhost/test_db",
            report_engine_url="https://test.reporting.com/v1",
            api_key="test-api-key"
        )
        
        # Setup webdriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        
        yield
        
        # Cleanup
        self.driver.quit()

    async def test_complete_billing_workflow(self, setup):
        """Test complete billing workflow from UI to backend"""
        # 1. Login to system
        self.driver.get("https://test.app.com/login")
        self.driver.find_element(By.ID, "username").send_keys("test_user")
        self.driver.find_element(By.ID, "password").send_keys("test_pass")
        self.driver.find_element(By.ID, "login-button").click()

        # 2. Navigate to billing section
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "billing-section"))
        ).click()

        # 3. Create new transaction
        self.driver.find_element(By.ID, "new-transaction").click()
        self.driver.find_element(By.ID, "amount").send_keys("150.00")
        self.driver.find_element(By.ID, "description").send_keys("Test payment")
        self.driver.find_element(By.ID, "submit-transaction").click()

        # 4. Verify transaction in backend
        transaction_id = self.driver.find_element(By.CLASS_NAME, "transaction-id").text
        transaction = await self.billing.get_transaction(transaction_id)
        assert transaction["amount"] == "150.00"
        assert transaction["status"] == "completed"

        # 5. Generate report
        self.driver.find_element(By.ID, "generate-report").click()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "report-ready"))
        )

        # 6. Verify report in backend
        report_id = self.driver.find_element(By.CLASS_NAME, "report-id").text
        report_status = await self.reporting.get_report_status(report_id)
        assert report_status["status"] == "completed"

    async def test_validation_workflow(self, setup):
        """Test address and name validation workflow"""
        # 1. Navigate to validation section
        self.driver.get("https://test.app.com/validation")

        # 2. Test address validation
        address_fields = {
            "street": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94105"
        }
        
        for field, value in address_fields.items():
            self.driver.find_element(By.ID, f"address-{field}").send_keys(value)

        self.driver.find_element(By.ID, "validate-address").click()

        # 3. Verify address validation
        try:
            success_message = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "validation-success"))
            )
            assert "Address validated successfully" in success_message.text
        except TimeoutException:
            pytest.fail("Address validation timed out")

        # 4. Test name validation
        name_fields = {
            "first": "John",
            "middle": "Robert",
            "last": "Smith"
        }
        
        for field, value in name_fields.items():
            self.driver.find_element(By.ID, f"name-{field}").send_keys(value)

        self.driver.find_element(By.ID, "validate-name").click()

        # 5. Verify name validation
        try:
            success_message = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "validation-success"))
            )
            assert "Name validated successfully" in success_message.text
        except TimeoutException:
            pytest.fail("Name validation timed out")

    async def test_reporting_workflow(self, setup):
        """Test complete reporting workflow"""
        # 1. Navigate to reports section
        self.driver.get("https://test.app.com/reports")

        # 2. Configure report
        self.driver.find_element(By.ID, "report-type").click()
        self.driver.find_element(By.XPATH, "//option[text()='Billing Summary']").click()
        
        # Set date range
        start_date = (datetime.now()).strftime("%Y-%m-%d")
        end_date = (datetime.now()).strftime("%Y-%m-%d")
        self.driver.find_element(By.ID, "start-date").send_keys(start_date)
        self.driver.find_element(By.ID, "end-date").send_keys(end_date)

        # 3. Generate report
        self.driver.find_element(By.ID, "generate-report").click()

        # 4. Wait for report generation
        try:
            download_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.ID, "download-report"))
            )
            download_button.click()
        except TimeoutException:
            pytest.fail("Report generation timed out")

        # 5. Verify report in backend
        report_id = self.driver.find_element(By.CLASS_NAME, "report-id").text
        report_status = await self.reporting.get_report_status(report_id)
        assert report_status["status"] == "completed"
        assert report_status["format"] == "PDF"

    async def test_error_handling(self, setup):
        """Test error handling in UI and backend integration"""
        # 1. Test invalid address
        self.driver.get("https://test.app.com/validation")
        
        # Enter invalid address
        self.driver.find_element(By.ID, "address-street").send_keys("123")
        self.driver.find_element(By.ID, "validate-address").click()

        # Verify error message
        error_message = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "validation-error"))
        )
        assert "Invalid address" in error_message.text

        # 2. Test invalid transaction
        self.driver.get("https://test.app.com/billing")
        self.driver.find_element(By.ID, "new-transaction").click()
        self.driver.find_element(By.ID, "amount").send_keys("-50.00")
        self.driver.find_element(By.ID, "submit-transaction").click()

        # Verify error handling
        error_message = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "transaction-error"))
        )
        assert "Invalid amount" in error_message.text

    async def test_performance_requirements(self, setup):
        """Test performance requirements in real-world scenarios"""
        # 1. Measure page load time
        start_time = datetime.now()
        self.driver.get("https://test.app.com/dashboard")
        load_time = (datetime.now() - start_time).total_seconds()
        assert load_time < 2.0  # Page should load within 2 seconds

        # 2. Measure validation response time
        self.driver.get("https://test.app.com/validation")
        self.driver.find_element(By.ID, "address-street").send_keys("123 Main St")
        self.driver.find_element(By.ID, "address-city").send_keys("San Francisco")
        
        start_time = datetime.now()
        self.driver.find_element(By.ID, "validate-address").click()
        
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "validation-success"))
        )
        validation_time = (datetime.now() - start_time).total_seconds()
        assert validation_time < 1.0  # Validation should complete within 1 second

if __name__ == "__main__":
    pytest.main([__file__])
