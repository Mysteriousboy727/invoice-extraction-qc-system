"""
Regex Patterns for Invoice Field Extraction

Contains regular expressions for extracting various fields from invoice text.
"""

import re
from typing import Optional, List, Tuple


# Invoice number patterns
INVOICE_NUMBER_PATTERNS = [
    re.compile(r'(?:invoice\s*#?|inv\s*#?|invoice\s*number)\s*:?\s*([A-Z0-9\-/]+)', re.IGNORECASE),
    re.compile(r'#\s*([A-Z0-9\-/]+)', re.IGNORECASE),
    re.compile(r'invoice\s+([A-Z0-9\-/]+)', re.IGNORECASE),
]

# Date patterns
DATE_PATTERNS = [
    re.compile(r'(?:invoice\s*date|date)\s*:?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})', re.IGNORECASE),
    re.compile(r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})', re.IGNORECASE),
    re.compile(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', re.IGNORECASE),
]

# Due date patterns
DUE_DATE_PATTERNS = [
    re.compile(r'(?:due\s*date|payment\s*due)\s*:?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})', re.IGNORECASE),
    re.compile(r'due\s+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})', re.IGNORECASE),
]

# Seller/Buyer name patterns
SELLER_PATTERNS = [
    re.compile(r'(?:from|seller|vendor|supplier|bill\s*from)\s*:?\s*([^\n]+)', re.IGNORECASE),
    re.compile(r'^([A-Z][A-Z\s&,\.]+(?:Inc|LLC|Ltd|Corp|Company)?)', re.MULTILINE),
]

BUYER_PATTERNS = [
    re.compile(r'(?:to|buyer|customer|bill\s*to)\s*:?\s*([^\n]+)', re.IGNORECASE),
    re.compile(r'bill\s+to\s*:?\s*([^\n]+)', re.IGNORECASE),
]

# Address patterns
ADDRESS_PATTERNS = [
    re.compile(r'(?:address)\s*:?\s*([^\n]+(?:\n[^\n]+){0,3})', re.IGNORECASE),
    re.compile(r'(\d+\s+[A-Z][A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Boulevard|Blvd)[^\n]*)', re.IGNORECASE),
]

# Tax ID patterns
TAX_ID_PATTERNS = [
    re.compile(r'(?:tax\s*id|vat\s*id|gstin|ein)\s*:?\s*([A-Z0-9\-]+)', re.IGNORECASE),
    re.compile(r'(?:tax\s*identification|vat\s*number)\s*:?\s*([A-Z0-9\-]+)', re.IGNORECASE),
]

# Currency patterns
CURRENCY_PATTERNS = [
    re.compile(r'(?:currency)\s*:?\s*([A-Z]{3})', re.IGNORECASE),
    re.compile(r'([€$₹]|EUR|USD|INR)', re.IGNORECASE),
]

# Amount patterns
AMOUNT_PATTERNS = [
    re.compile(r'(\d+[,\.]?\d*\.\d{2})', re.IGNORECASE),
    re.compile(r'(\d+[,\.]\d{3}(?:\.\d{2})?)', re.IGNORECASE),
]

# Total patterns
NET_TOTAL_PATTERNS = [
    re.compile(r'(?:subtotal|net\s*total|total\s*before\s*tax)\s*:?\s*([\d,]+\.?\d*)', re.IGNORECASE),
    re.compile(r'subtotal\s+([\d,]+\.?\d*)', re.IGNORECASE),
]

TAX_AMOUNT_PATTERNS = [
    re.compile(r'(?:tax|vat|gst)\s*(?:amount|total)?\s*:?\s*([\d,]+\.?\d*)', re.IGNORECASE),
    re.compile(r'tax\s+([\d,]+\.?\d*)', re.IGNORECASE),
]

GROSS_TOTAL_PATTERNS = [
    re.compile(r'(?:total|grand\s*total|amount\s*due)\s*:?\s*([\d,]+\.?\d*)', re.IGNORECASE),
    re.compile(r'total\s+([\d,]+\.?\d*)', re.IGNORECASE),
    re.compile(r'amount\s+due\s+([\d,]+\.?\d*)', re.IGNORECASE),
]


def extract_invoice_number(text: str) -> Optional[str]:
    """Extract invoice number from text."""
    for pattern in INVOICE_NUMBER_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def extract_date(text: str, patterns: List[re.Pattern] = None) -> Optional[str]:
    """Extract date from text using provided patterns."""
    if patterns is None:
        patterns = DATE_PATTERNS
    
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def extract_due_date(text: str) -> Optional[str]:
    """Extract due date from text."""
    return extract_date(text, DUE_DATE_PATTERNS)


def extract_seller_name(text: str) -> Optional[str]:
    """Extract seller name from text."""
    for pattern in SELLER_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def extract_buyer_name(text: str) -> Optional[str]:
    """Extract buyer name from text."""
    for pattern in BUYER_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def extract_address(text: str) -> Optional[str]:
    """Extract address from text."""
    for pattern in ADDRESS_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def extract_tax_id(text: str) -> Optional[str]:
    """Extract tax ID from text."""
    for pattern in TAX_ID_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def extract_currency(text: str) -> Optional[str]:
    """Extract currency code from text."""
    for pattern in CURRENCY_PATTERNS:
        match = pattern.search(text)
        if match:
            currency = match.group(1).strip()
            # Map symbols to codes
            if currency == '€':
                return 'EUR'
            elif currency == '$':
                return 'USD'
            elif currency == '₹':
                return 'INR'
            return currency.upper()
    return None


def extract_amount(text: str, patterns: List[re.Pattern] = None) -> Optional[float]:
    """Extract amount from text using provided patterns."""
    if patterns is None:
        patterns = AMOUNT_PATTERNS
    
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                return float(amount_str)
            except ValueError:
                continue
    return None


def extract_net_total(text: str) -> Optional[float]:
    """Extract net total from text."""
    return extract_amount(text, NET_TOTAL_PATTERNS)


def extract_tax_amount(text: str) -> Optional[float]:
    """Extract tax amount from text."""
    return extract_amount(text, TAX_AMOUNT_PATTERNS)


def extract_gross_total(text: str) -> Optional[float]:
    """Extract gross total from text."""
    return extract_amount(text, GROSS_TOTAL_PATTERNS)


def extract_line_items(text: str) -> List[dict]:
    """
    Extract line items from invoice text.
    
    Looks for table-like structures with description, quantity, unit_price, and line_total.
    """
    line_items = []
    
    # Pattern for table rows with line items
    # Matches: description, quantity, unit_price, total
    line_item_pattern = re.compile(
        r'([A-Za-z0-9\s\-\.]+?)\s+(\d+\.?\d*)\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)',
        re.IGNORECASE
    )
    
    # Alternative pattern for more structured tables
    table_pattern = re.compile(
        r'(?:description|item|product).*?(?:qty|quantity).*?(?:price|unit).*?(?:total|amount)',
        re.IGNORECASE | re.DOTALL
    )
    
    # Try to find table section
    table_match = table_pattern.search(text)
    if table_match:
        table_text = text[table_match.end():]
        # Extract rows from table
        rows = re.findall(
            r'([A-Za-z0-9\s\-\.]+?)\s+(\d+\.?\d*)\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)',
            table_text,
            re.IGNORECASE
        )
        for row in rows[:10]:  # Limit to 10 items
            try:
                description = row[0].strip()
                quantity = float(row[1].replace(',', ''))
                unit_price = float(row[2].replace(',', ''))
                line_total = float(row[3].replace(',', ''))
                
                if description and quantity > 0:
                    line_items.append({
                        'description': description,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'line_total': line_total
                    })
            except (ValueError, IndexError):
                continue
    
    # Fallback: try simple pattern matching
    if not line_items:
        matches = line_item_pattern.findall(text)
        for match in matches[:10]:
            try:
                description = match[0].strip()
                quantity = float(match[1].replace(',', ''))
                unit_price = float(match[2].replace(',', ''))
                line_total = float(match[3].replace(',', ''))
                
                if description and len(description) > 2 and quantity > 0:
                    line_items.append({
                        'description': description,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'line_total': line_total
                    })
            except (ValueError, IndexError):
                continue
    
    return line_items

