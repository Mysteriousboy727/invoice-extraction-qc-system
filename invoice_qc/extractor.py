"""
Invoice Extractor Module

Extracts invoice data from PDF files and converts them to structured JSON format.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dateutil import parser as date_parser

from invoice_qc.schema import Invoice, LineItem
from invoice_qc.utils.pdf_reader import extract_text_from_pdf, extract_text_from_pdfs
from invoice_qc.utils.patterns import (
    extract_invoice_number,
    extract_date,
    extract_due_date,
    extract_seller_name,
    extract_buyer_name,
    extract_address,
    extract_tax_id,
    extract_currency,
    extract_net_total,
    extract_tax_amount,
    extract_gross_total,
    extract_line_items,
)


def parse_date(date_str: str) -> Optional[str]:
    """
    Parse date string to ISO format.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        ISO format date string (YYYY-MM-DD) or None if parsing fails
    """
    if not date_str:
        return None
    
    try:
        # Try common date formats
        date_obj = date_parser.parse(date_str, dayfirst=True, fuzzy=True)
        return date_obj.date().isoformat()
    except (ValueError, TypeError):
        return None


def extract_invoice_from_text(text: str, invoice_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract invoice data from text content.
    
    Args:
        text: Text content from PDF
        invoice_id: Optional invoice ID to assign
        
    Returns:
        Dictionary containing extracted invoice data
    """
    # Extract basic fields
    invoice_number = extract_invoice_number(text) or "UNKNOWN"
    invoice_date_str = extract_date(text)
    due_date_str = extract_due_date(text)
    seller_name = extract_seller_name(text)
    buyer_name = extract_buyer_name(text)
    
    # Extract addresses (try to find seller and buyer addresses separately)
    seller_address = extract_address(text)  # Simplified - would need better logic
    buyer_address = None  # Would need better extraction logic
    
    # Extract tax IDs
    seller_tax_id = extract_tax_id(text)  # Simplified
    buyer_tax_id = None
    
    # Extract currency
    currency = extract_currency(text) or "USD"
    
    # Extract totals
    net_total = extract_net_total(text) or 0.0
    tax_amount = extract_tax_amount(text) or 0.0
    gross_total = extract_gross_total(text) or 0.0
    
    # Extract line items
    line_items_data = extract_line_items(text)
    line_items = []
    for item in line_items_data:
        line_items.append({
            "description": item.get("description", ""),
            "quantity": item.get("quantity", 0.0),
            "unit_price": item.get("unit_price", 0.0),
            "line_total": item.get("line_total", 0.0),
        })
    
    # Build invoice dictionary
    invoice_data = {
        "invoice_number": invoice_number,
        "invoice_date": parse_date(invoice_date_str) if invoice_date_str else None,
        "due_date": parse_date(due_date_str) if due_date_str else None,
        "seller_name": seller_name or "",
        "seller_address": seller_address,
        "seller_tax_id": seller_tax_id,
        "buyer_name": buyer_name or "",
        "buyer_address": buyer_address,
        "buyer_tax_id": buyer_tax_id,
        "currency": currency,
        "net_total": net_total,
        "tax_amount": tax_amount,
        "gross_total": gross_total,
        "line_items": line_items,
    }
    
    # Add invoice_id if provided
    if invoice_id:
        invoice_data["invoice_id"] = invoice_id
    
    return invoice_data


def extract_invoice_from_pdf(pdf_path: str | Path, invoice_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract invoice data from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        invoice_id: Optional invoice ID to assign
        
    Returns:
        Dictionary containing extracted invoice data
    """
    text = extract_text_from_pdf(pdf_path)
    
    if not invoice_id:
        invoice_id = Path(pdf_path).stem
    
    return extract_invoice_from_text(text, invoice_id)


def extract_invoices_from_directory(pdf_dir: str | Path) -> List[Dict[str, Any]]:
    """
    Extract invoices from all PDF files in a directory.
    
    Args:
        pdf_dir: Directory containing PDF files
        
    Returns:
        List of invoice dictionaries
    """
    pdf_texts = extract_text_from_pdfs(pdf_dir)
    invoices = []
    
    for filename, text in pdf_texts:
        invoice_id = Path(filename).stem
        try:
            invoice_data = extract_invoice_from_text(text, invoice_id)
            invoices.append(invoice_data)
        except Exception as e:
            print(f"Error extracting invoice from {filename}: {e}")
            continue
    
    return invoices


def save_invoices_to_json(invoices: List[Dict[str, Any]], output_path: str | Path) -> None:
    """
    Save extracted invoices to a JSON file.
    
    Args:
        invoices: List of invoice dictionaries
        output_path: Path to output JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(invoices, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"Saved {len(invoices)} invoices to {output_path}")


def load_invoices_from_json(json_path: str | Path) -> List[Dict[str, Any]]:
    """
    Load invoices from a JSON file.
    
    Args:
        json_path: Path to JSON file
        
    Returns:
        List of invoice dictionaries
    """
    json_path = Path(json_path)
    
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        invoices = json.load(f)
    
    return invoices

