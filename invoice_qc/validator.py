"""
Invoice Validator Module

Validates invoices against completeness, format, business, and anomaly rules.
"""

from datetime import date
from typing import List, Dict, Any, Optional, Set
from collections import Counter

from invoice_qc.schema import Invoice, LineItem


class ValidationError:
    """Represents a validation error."""
    
    def __init__(self, error_type: str, message: str):
        self.error_type = error_type
        self.message = message
    
    def __str__(self) -> str:
        return f"{self.error_type}: {self.message}"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {
            "error_type": self.error_type,
            "message": self.message
        }


class InvoiceValidator:
    """Validates invoices against various rules."""
    
    def __init__(self):
        self.seen_invoices: Set[tuple] = set()  # For duplicate detection
    
    def validate(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single invoice.
        
        Args:
            invoice_data: Invoice data dictionary
            
        Returns:
            Validation result dictionary with invoice_id, is_valid, and errors
        """
        invoice_id = invoice_data.get("invoice_id", invoice_data.get("invoice_number", "unknown"))
        errors: List[str] = []
        
        # Try to create Pydantic model (this will catch format errors)
        try:
            invoice = Invoice(**invoice_data)
        except Exception as e:
            errors.append(f"schema_error: {str(e)}")
            return {
                "invoice_id": invoice_id,
                "is_valid": False,
                "errors": errors
            }
        
        # Completeness rules
        errors.extend(self._validate_completeness(invoice))
        
        # Format rules
        errors.extend(self._validate_format(invoice))
        
        # Business rules
        errors.extend(self._validate_business_rules(invoice))
        
        # Anomaly rules
        errors.extend(self._validate_anomalies(invoice, invoice_id))
        
        is_valid = len(errors) == 0
        
        return {
            "invoice_id": invoice_id,
            "is_valid": is_valid,
            "errors": errors
        }
    
    def _validate_completeness(self, invoice: Invoice) -> List[str]:
        """Validate completeness rules."""
        errors = []
        
        if not invoice.invoice_number or len(invoice.invoice_number.strip()) == 0:
            errors.append("missing_field: invoice_number")
        
        if invoice.invoice_date is None:
            errors.append("missing_field: invoice_date")
        
        if not invoice.seller_name or len(invoice.seller_name.strip()) == 0:
            errors.append("missing_field: seller_name")
        
        if not invoice.buyer_name or len(invoice.buyer_name.strip()) == 0:
            errors.append("missing_field: buyer_name")
        
        return errors
    
    def _validate_format(self, invoice: Invoice) -> List[str]:
        """Validate format rules."""
        errors = []
        
        # Currency validation is handled by Pydantic
        # But we can add additional checks here
        
        if invoice.net_total < 0:
            errors.append("format_error: net_total must be >= 0")
        
        if invoice.tax_amount < 0:
            errors.append("format_error: tax_amount must be >= 0")
        
        if invoice.gross_total < 0:
            errors.append("format_error: gross_total must be >= 0")
        
        return errors
    
    def _validate_business_rules(self, invoice: Invoice) -> List[str]:
        """Validate business rules."""
        errors = []
        
        # Check line items sum matches net_total
        line_items_sum = sum(item.line_total for item in invoice.line_items)
        tolerance = 0.01  # Allow small floating point differences
        
        if abs(line_items_sum - invoice.net_total) > tolerance:
            errors.append(
                f"business_rule_failed: totals_mismatch "
                f"(line_items_sum={line_items_sum:.2f}, net_total={invoice.net_total:.2f})"
            )
        
        # Check net_total + tax_amount ≈ gross_total
        expected_gross = invoice.net_total + invoice.tax_amount
        if abs(expected_gross - invoice.gross_total) > tolerance:
            errors.append(
                f"business_rule_failed: gross_total_mismatch "
                f"(expected={expected_gross:.2f}, actual={invoice.gross_total:.2f})"
            )
        
        # Check due_date >= invoice_date
        if invoice.due_date is not None and invoice.invoice_date is not None:
            if invoice.due_date < invoice.invoice_date:
                errors.append(
                    f"business_rule_failed: due_date_before_invoice_date "
                    f"(due_date={invoice.due_date}, invoice_date={invoice.invoice_date})"
                )
        
        return errors
    
    def _validate_anomalies(self, invoice: Invoice, invoice_id: str) -> List[str]:
        """Validate anomaly rules (e.g., duplicates)."""
        errors = []
        
        # Detect duplicates: (invoice_number + seller_name + invoice_date)
        duplicate_key = (
            invoice.invoice_number,
            invoice.seller_name,
            str(invoice.invoice_date) if invoice.invoice_date else None
        )
        
        if duplicate_key in self.seen_invoices:
            errors.append(
                f"anomaly_detected: duplicate_invoice "
                f"(invoice_number={invoice.invoice_number}, "
                f"seller={invoice.seller_name}, date={invoice.invoice_date})"
            )
        else:
            self.seen_invoices.add(duplicate_key)
        
        return errors
    
    def validate_batch(self, invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a batch of invoices.
        
        Args:
            invoices: List of invoice dictionaries
            
        Returns:
            Dictionary with validation results and summary
        """
        results = []
        error_counts = Counter()
        
        # Reset seen invoices for batch validation
        self.seen_invoices.clear()
        
        for invoice_data in invoices:
            result = self.validate(invoice_data)
            results.append(result)
            
            # Count errors by type
            for error in result["errors"]:
                error_type = error.split(":")[0] if ":" in error else "unknown"
                error_counts[error_type] += 1
        
        valid_count = sum(1 for r in results if r["is_valid"])
        invalid_count = len(results) - valid_count
        
        return {
            "results": results,
            "summary": {
                "total_invoices": len(invoices),
                "valid_invoices": valid_count,
                "invalid_invoices": invalid_count,
                "error_counts": dict(error_counts)
            }
        }
    
    def reset_duplicate_tracking(self) -> None:
        """Reset the duplicate invoice tracking set."""
        self.seen_invoices.clear()

