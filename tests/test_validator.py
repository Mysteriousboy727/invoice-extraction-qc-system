"""
Tests for the invoice validator module.
"""

import pytest
from datetime import date, timedelta
from invoice_qc.validator import InvoiceValidator
from invoice_qc.schema import Invoice, LineItem


def test_completeness_validation():
    """Test completeness validation rules."""
    validator = InvoiceValidator()
    
    # Missing invoice_number
    invoice_data = {
        "invoice_number": "",
        "invoice_date": "2024-01-15",
        "seller_name": "Seller",
        "buyer_name": "Buyer",
        "currency": "USD",
        "net_total": 100.0,
        "tax_amount": 10.0,
        "gross_total": 110.0,
        "line_items": []
    }
    
    result = validator.validate(invoice_data)
    assert not result["is_valid"]
    assert any("missing_field: invoice_number" in error for error in result["errors"])


def test_format_validation():
    """Test format validation rules."""
    validator = InvoiceValidator()
    
    # Invalid currency
    invoice_data = {
        "invoice_number": "INV-001",
        "invoice_date": "2024-01-15",
        "seller_name": "Seller",
        "buyer_name": "Buyer",
        "currency": "XYZ",  # Invalid currency
        "net_total": 100.0,
        "tax_amount": 10.0,
        "gross_total": 110.0,
        "line_items": []
    }
    
    result = validator.validate(invoice_data)
    # Should fail schema validation due to invalid currency
    assert not result["is_valid"]


def test_business_rules_validation():
    """Test business rules validation."""
    validator = InvoiceValidator()
    
    # Line items sum doesn't match net_total
    invoice_data = {
        "invoice_number": "INV-001",
        "invoice_date": "2024-01-15",
        "seller_name": "Seller",
        "buyer_name": "Buyer",
        "currency": "USD",
        "net_total": 100.0,
        "tax_amount": 10.0,
        "gross_total": 110.0,
        "line_items": [
            {
                "description": "Item 1",
                "quantity": 1.0,
                "unit_price": 20.0,
                "line_total": 20.0
            },
            {
                "description": "Item 2",
                "quantity": 1.0,
                "unit_price": 30.0,
                "line_total": 30.0
            }
        ]
    }
    
    result = validator.validate(invoice_data)
    assert not result["is_valid"]
    assert any("totals_mismatch" in error for error in result["errors"])
    
    # Fix: net_total should be 50.0
    invoice_data["net_total"] = 50.0
    invoice_data["gross_total"] = 60.0
    result = validator.validate(invoice_data)
    # Should pass business rules now
    assert result["is_valid"] or not any("totals_mismatch" in error for error in result["errors"])


def test_gross_total_validation():
    """Test that gross_total = net_total + tax_amount."""
    validator = InvoiceValidator()
    
    invoice_data = {
        "invoice_number": "INV-001",
        "invoice_date": "2024-01-15",
        "seller_name": "Seller",
        "buyer_name": "Buyer",
        "currency": "USD",
        "net_total": 100.0,
        "tax_amount": 10.0,
        "gross_total": 120.0,  # Should be 110.0
        "line_items": [
            {
                "description": "Item 1",
                "quantity": 1.0,
                "unit_price": 100.0,
                "line_total": 100.0
            }
        ]
    }
    
    result = validator.validate(invoice_data)
    assert not result["is_valid"]
    assert any("gross_total_mismatch" in error for error in result["errors"])


def test_due_date_validation():
    """Test that due_date >= invoice_date."""
    validator = InvoiceValidator()
    
    invoice_data = {
        "invoice_number": "INV-001",
        "invoice_date": "2024-01-15",
        "due_date": "2024-01-10",  # Before invoice_date
        "seller_name": "Seller",
        "buyer_name": "Buyer",
        "currency": "USD",
        "net_total": 100.0,
        "tax_amount": 10.0,
        "gross_total": 110.0,
        "line_items": []
    }
    
    result = validator.validate(invoice_data)
    # Should fail due to due_date validation
    assert not result["is_valid"]


def test_duplicate_detection():
    """Test duplicate invoice detection."""
    validator = InvoiceValidator()
    
    invoice_data = {
        "invoice_number": "INV-001",
        "invoice_date": "2024-01-15",
        "seller_name": "Seller",
        "buyer_name": "Buyer",
        "currency": "USD",
        "net_total": 100.0,
        "tax_amount": 10.0,
        "gross_total": 110.0,
        "line_items": []
    }
    
    # First invoice should be valid
    result1 = validator.validate(invoice_data)
    # May have other errors, but shouldn't have duplicate error
    
    # Second invoice with same number, seller, and date should be detected as duplicate
    result2 = validator.validate(invoice_data)
    assert any("duplicate_invoice" in error for error in result2["errors"])


def test_batch_validation():
    """Test batch validation functionality."""
    validator = InvoiceValidator()
    
    invoices = [
        {
            "invoice_number": "INV-001",
            "invoice_date": "2024-01-15",
            "seller_name": "Seller",
            "buyer_name": "Buyer",
            "currency": "USD",
            "net_total": 100.0,
            "tax_amount": 10.0,
            "gross_total": 110.0,
            "line_items": [
                {
                    "description": "Item 1",
                    "quantity": 1.0,
                    "unit_price": 100.0,
                    "line_total": 100.0
                }
            ]
        },
        {
            "invoice_number": "INV-002",
            "invoice_date": "2024-01-16",
            "seller_name": "Seller",
            "buyer_name": "Buyer",
            "currency": "USD",
            "net_total": 200.0,
            "tax_amount": 20.0,
            "gross_total": 220.0,
            "line_items": [
                {
                    "description": "Item 2",
                    "quantity": 2.0,
                    "unit_price": 100.0,
                    "line_total": 200.0
                }
            ]
        }
    ]
    
    results = validator.validate_batch(invoices)
    
    assert "results" in results
    assert "summary" in results
    assert results["summary"]["total_invoices"] == 2
    assert len(results["results"]) == 2

