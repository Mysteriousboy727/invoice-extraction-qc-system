# Expected Output Format

## CLI Validation Command Output

### When All Invoices Are Valid:

```
Loading invoices from sample_invoice.json...
Validating 2 invoices...

Validation Summary:
  Total Invoices: 2
  Valid: 2
  Invalid: 0

✓ Validation report saved to test_output.json
```

### When There Are Invalid Invoices:

```
Loading invoices from sample_invoice_with_errors.json...
Validating 2 invoices...

Validation Summary:
  Total Invoices: 2
  Valid: 0
  Invalid: 2

Error Counts:
  schema_error: 2

Invalid Invoices:
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Invoice ID ┃ Errors                                                          ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ error-001  │ schema_error: 1 validation error for Invoice                    │
│            │ invoice_number                                                  │
│            │   String should have at least 1 character                       │
└────────────┴─────────────────────────────────────────────────────────────────┘

✓ Validation report saved to error_test.json
```

## JSON Report Format

The report JSON file contains:

```json
{
  "results": [
    {
      "invoice_id": "sample-001",
      "is_valid": true,
      "errors": []
    }
  ],
  "summary": {
    "total_invoices": 2,
    "valid_invoices": 2,
    "invalid_invoices": 0,
    "error_counts": {}
  }
}
```

## Exit Codes

- **Exit code 0**: All invoices are valid
- **Exit code 1**: One or more invoices are invalid

## If Output Doesn't Match

Please specify:
1. What command you ran
2. What output you're seeing
3. What output you expected

