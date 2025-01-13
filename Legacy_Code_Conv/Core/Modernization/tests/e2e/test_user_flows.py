"""
End-to-End User Flow Tests
Version: 1.0.0
Last Updated: 2025-01-10
"""
import os
import pytest
from playwright.sync_api import expect, Page

BASE_URL = os.getenv("APP_URL", "http://localhost:8000")
TEST_USER = {
    "email": "test@example.com",
    "password": "Test123!",
    "first_name": "Test",
    "last_name": "User"
}

def test_user_registration_and_login(page: Page):
    """Test complete user registration and login flow."""
    # Navigate to registration page
    page.goto(f"{BASE_URL}/register")
    
    # Fill registration form
    page.fill("#email", TEST_USER["email"])
    page.fill("#password", TEST_USER["password"])
    page.fill("#confirm-password", TEST_USER["password"])
    page.fill("#first-name", TEST_USER["first_name"])
    page.fill("#last-name", TEST_USER["last_name"])
    
    # Submit form and wait for navigation
    with page.expect_navigation():
        page.click("#register-button")
    
    # Verify successful registration
    expect(page).to_have_url(f"{BASE_URL}/login")
    expect(page.locator(".toast-success")).to_be_visible()
    
    # Login with new account
    page.fill("#email", TEST_USER["email"])
    page.fill("#password", TEST_USER["password"])
    
    with page.expect_navigation():
        page.click("#login-button")
    
    # Verify successful login
    expect(page).to_have_url(f"{BASE_URL}/dashboard")
    expect(page.locator("#user-menu")).to_be_visible()


def test_tenant_creation_and_management(page: Page):
    """Test tenant creation and management flow."""
    # Login first
    page.goto(f"{BASE_URL}/login")
    page.fill("#email", TEST_USER["email"])
    page.fill("#password", TEST_USER["password"])
    with page.expect_navigation():
        page.click("#login-button")
    
    # Navigate to tenant creation
    page.click("#create-tenant-button")
    
    # Fill tenant details
    page.fill("#tenant-name", "Test Tenant")
    page.fill("#tenant-slug", "test-tenant")
    page.select_option("#subscription-plan", "premium")
    
    # Create tenant
    with page.expect_navigation():
        page.click("#submit-tenant")
    
    # Verify tenant creation
    expect(page.locator("#tenant-header")).to_contain_text("Test Tenant")
    
    # Update tenant settings
    page.click("#tenant-settings")
    page.fill("#max-users", "20")
    page.click("#save-settings")
    
    # Verify settings update
    expect(page.locator(".toast-success")).to_be_visible()
    expect(page.locator("#max-users")).to_have_value("20")


def test_inventory_management(page: Page):
    """Test inventory management flow."""
    # Login and navigate to inventory
    page.goto(f"{BASE_URL}/login")
    page.fill("#email", TEST_USER["email"])
    page.fill("#password", TEST_USER["password"])
    with page.expect_navigation():
        page.click("#login-button")
    
    # Navigate to inventory
    page.click("#inventory-link")
    
    # Create new item
    page.click("#add-item")
    page.fill("#item-name", "Test Item")
    page.fill("#item-description", "Test Description")
    page.fill("#item-quantity", "10")
    page.fill("#item-price", "99.99")
    page.click("#save-item")
    
    # Verify item creation
    expect(page.locator(".inventory-list")).to_contain_text("Test Item")
    
    # Edit item
    page.click("[data-testid='edit-item']")
    page.fill("#item-quantity", "15")
    page.click("#save-item")
    
    # Verify edit
    expect(page.locator(".inventory-list")).to_contain_text("15")
    
    # Delete item
    page.click("[data-testid='delete-item']")
    page.click("#confirm-delete")
    
    # Verify deletion
    expect(page.locator(".inventory-list")).not_to_contain_text("Test Item")


def test_order_processing(page: Page):
    """Test complete order processing flow."""
    # Login and create inventory item first
    page.goto(f"{BASE_URL}/login")
    page.fill("#email", TEST_USER["email"])
    page.fill("#password", TEST_USER["password"])
    with page.expect_navigation():
        page.click("#login-button")
    
    # Create inventory item
    page.click("#inventory-link")
    page.click("#add-item")
    page.fill("#item-name", "Order Item")
    page.fill("#item-quantity", "20")
    page.fill("#item-price", "49.99")
    page.click("#save-item")
    
    # Create new order
    page.click("#orders-link")
    page.click("#create-order")
    
    # Fill order details
    page.fill("#customer-name", "John Doe")
    page.fill("#customer-email", "john@example.com")
    page.fill("#shipping-address", "123 Main St")
    
    # Add item to order
    page.click("#add-item-to-order")
    page.click("[data-testid='select-item']")
    page.fill("#order-quantity", "2")
    page.click("#add-to-order")
    
    # Submit order
    page.click("#submit-order")
    
    # Verify order creation
    expect(page.locator(".order-list")).to_contain_text("John Doe")
    expect(page.locator(".order-status")).to_contain_text("Pending")
    
    # Process order
    page.click("[data-testid='process-order']")
    page.click("#confirm-processing")
    
    # Verify status change
    expect(page.locator(".order-status")).to_contain_text("Processing")
    
    # Complete order
    page.click("[data-testid='complete-order']")
    page.click("#confirm-completion")
    
    # Verify completion
    expect(page.locator(".order-status")).to_contain_text("Completed")
    
    # Verify inventory update
    page.click("#inventory-link")
    expect(page.locator(".inventory-list")).to_contain_text("18")  # 20 - 2


def test_error_scenarios(page: Page):
    """Test various error scenarios and edge cases."""
    # Login
    page.goto(f"{BASE_URL}/login")
    page.fill("#email", TEST_USER["email"])
    page.fill("#password", TEST_USER["password"])
    with page.expect_navigation():
        page.click("#login-button")
    
    # Test invalid inventory quantity
    page.click("#inventory-link")
    page.click("#add-item")
    page.fill("#item-name", "Error Test Item")
    page.fill("#item-quantity", "-1")  # Invalid quantity
    page.click("#save-item")
    
    # Verify error message
    expect(page.locator(".error-message")).to_contain_text("Quantity must be positive")
    
    # Test duplicate tenant slug
    page.click("#create-tenant-button")
    page.fill("#tenant-name", "Duplicate Tenant")
    page.fill("#tenant-slug", "test-tenant")  # Already exists
    page.click("#submit-tenant")
    
    # Verify error message
    expect(page.locator(".error-message")).to_contain_text("Slug already exists")
    
    # Test insufficient inventory
    page.click("#orders-link")
    page.click("#create-order")
    page.fill("#customer-name", "Error Test")
    page.click("#add-item-to-order")
    page.click("[data-testid='select-item']")
    page.fill("#order-quantity", "1000")  # More than available
    page.click("#add-to-order")
    
    # Verify error message
    expect(page.locator(".error-message")).to_contain_text("Insufficient inventory")


def test_concurrent_operations(page: Page, browser):
    """Test concurrent operations and race conditions."""
    # Create second browser context
    context2 = browser.new_context()
    page2 = context2.new_page()
    
    # Login on both browsers
    for p in [page, page2]:
        p.goto(f"{BASE_URL}/login")
        p.fill("#email", TEST_USER["email"])
        p.fill("#password", TEST_USER["password"])
        with p.expect_navigation():
            p.click("#login-button")
    
    # Create inventory item
    page.click("#inventory-link")
    page.click("#add-item")
    page.fill("#item-name", "Concurrent Item")
    page.fill("#item-quantity", "10")
    page.click("#save-item")
    
    # Try to edit same item concurrently
    page.click("[data-testid='edit-item']")
    page2.click("#inventory-link")
    page2.click("[data-testid='edit-item']")
    
    # Edit in first browser
    page.fill("#item-quantity", "5")
    page.click("#save-item")
    
    # Edit in second browser
    page2.fill("#item-quantity", "3")
    page2.click("#save-item")
    
    # Verify proper concurrency handling
    expect(page.locator(".error-message")).to_be_visible()
    
    # Clean up
    context2.close()
