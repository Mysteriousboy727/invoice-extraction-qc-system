"""
Invoice Schema Definitions

Defines the data structures for invoices and line items using Pydantic models
for validation and type safety.
"""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic import ConfigDict


class LineItem(BaseModel):
    """
    Represents a single line item in an invoice.
    
    Attributes:
        description: Description of the item or service
        quantity: Quantity of items
        unit_price: Price per unit
        line_total: Total price for this line item
    """
    
    description: str = Field(..., description="Item description")
    quantity: float = Field(..., ge=0, description="Quantity (must be >= 0)")
    unit_price: float = Field(..., ge=0, description="Unit price (must be >= 0)")
    line_total: float = Field(..., ge=0, description="Line total (must be >= 0)")
    
    @model_validator(mode='after')
    def validate_line_total(self):
        """Validate that line_total equals quantity * unit_price (with tolerance)."""
        expected = self.quantity * self.unit_price
        if abs(self.line_total - expected) > 0.01:  # Allow small floating point differences
            raise ValueError(f"line_total {self.line_total} does not match quantity * unit_price ({expected})")
        return self


class Invoice(BaseModel):
    """
    Represents a complete invoice with all required and optional fields.
    
    Attributes:
        invoice_number: Unique invoice identifier
        invoice_date: Date when invoice was issued
        due_date: Payment due date (optional)
        seller_name: Name of the seller/issuer
        seller_address: Seller's address (optional)
        seller_tax_id: Seller's tax identification number (optional)
        buyer_name: Name of the buyer/recipient
        buyer_address: Buyer's address (optional)
        buyer_tax_id: Buyer's tax identification number (optional)
        currency: Currency code (EUR, USD, or INR)
        net_total: Total amount before tax
        tax_amount: Tax amount
        gross_total: Total amount including tax
        line_items: List of line items in the invoice
    """
    
    invoice_number: str = Field(..., min_length=1, description="Invoice number")
    invoice_date: date = Field(..., description="Invoice date")
    due_date: Optional[date] = Field(None, description="Payment due date")
    seller_name: str = Field(..., min_length=1, description="Seller name")
    seller_address: Optional[str] = Field(None, description="Seller address")
    seller_tax_id: Optional[str] = Field(None, description="Seller tax ID")
    buyer_name: str = Field(..., min_length=1, description="Buyer name")
    buyer_address: Optional[str] = Field(None, description="Buyer address")
    buyer_tax_id: Optional[str] = Field(None, description="Buyer tax ID")
    currency: str = Field(..., description="Currency code")
    net_total: float = Field(..., ge=0, description="Net total (must be >= 0)")
    tax_amount: float = Field(..., ge=0, description="Tax amount (must be >= 0)")
    gross_total: float = Field(..., ge=0, description="Gross total (must be >= 0)")
    line_items: List[LineItem] = Field(default_factory=list, description="List of line items")
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency is one of the supported currencies."""
        allowed = {"EUR", "USD", "INR"}
        if v.upper() not in allowed:
            raise ValueError(f"Currency must be one of {allowed}, got {v}")
        return v.upper()
    
    @model_validator(mode='after')
    def validate_due_date(self):
        """Validate that due_date is after invoice_date."""
        if self.due_date is not None and self.invoice_date is not None:
            if self.due_date < self.invoice_date:
                raise ValueError(f"due_date {self.due_date} must be >= invoice_date {self.invoice_date}")
        return self
    
    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.isoformat()
        }
    )

