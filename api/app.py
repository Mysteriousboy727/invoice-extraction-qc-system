"""
FastAPI Application for Invoice QC Service

Provides REST API endpoints for invoice extraction and validation.
"""

import json
from typing import List, Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from invoice_qc.extractor import extract_invoice_from_text, extract_invoices_from_directory
from invoice_qc.validator import InvoiceValidator
from invoice_qc.utils.pdf_reader import extract_text_from_pdf
import tempfile
from pathlib import Path

app = FastAPI(
    title="Invoice QC Service API",
    description="API for extracting and validating invoices",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

validator = InvoiceValidator()


class InvoiceList(BaseModel):
    """Request model for invoice validation."""
    invoices: List[Dict[str, Any]]


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Status information
    """
    return {"status": "ok"}


@app.post("/validate-json")
async def validate_json(invoice_list: InvoiceList):
    """
    Validate a list of invoices from JSON.
    
    Args:
        invoice_list: List of invoice dictionaries
        
    Returns:
        Validation results with per-invoice results and summary
    """
    try:
        results = validator.validate_batch(invoice_list.invoices)
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")


@app.post("/extract-and-validate-pdfs")
async def extract_and_validate_pdfs(files: List[UploadFile] = File(...)):
    """
    Extract invoices from uploaded PDF files and validate them.
    
    Args:
        files: List of uploaded PDF files
        
    Returns:
        Dictionary containing extracted JSON and validation report
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    extracted_invoices = []
    
    # Process each uploaded PDF
    for file in files:
        if not file.filename.endswith('.pdf'):
            continue
        
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            # Extract invoice from PDF
            invoice_id = Path(file.filename).stem
            invoice_data = extract_invoice_from_text(
                extract_text_from_pdf(tmp_path),
                invoice_id
            )
            extracted_invoices.append(invoice_data)
            
            # Clean up temp file
            Path(tmp_path).unlink()
            
        except Exception as e:
            print(f"Error processing {file.filename}: {e}")
            continue
    
    if not extracted_invoices:
        raise HTTPException(status_code=400, detail="No valid invoices extracted from PDFs")
    
    # Validate extracted invoices
    validator.reset_duplicate_tracking()
    validation_results = validator.validate_batch(extracted_invoices)
    
    return JSONResponse(content={
        "extracted_invoices": extracted_invoices,
        "validation_report": validation_results
    })


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Invoice QC Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "validate_json": "/validate-json",
            "extract_and_validate_pdfs": "/extract-and-validate-pdfs"
        }
    }

