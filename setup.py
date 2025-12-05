"""
Setup script for invoice-qc-service
"""

from setuptools import setup, find_packages

setup(
    name="invoice-qc-service",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pdfplumber>=0.10.0",
        "PyPDF2>=3.0.0",
        "pydantic>=2.5.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "typer>=0.9.0",
        "python-dateutil>=2.8.2",
        "regex>=2023.10.3",
        "rich>=13.7.0",
    ],
    entry_points={
        "console_scripts": [
            "invoice-qc=invoice_qc.cli.main:app",
        ],
    },
)

