"""
CLI Tool for Invoice QC Service

Provides command-line interface for extracting and validating invoices.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from invoice_qc.extractor import (
    extract_invoices_from_directory,
    save_invoices_to_json,
    load_invoices_from_json,
)
from invoice_qc.validator import InvoiceValidator

app = typer.Typer(help="Invoice Quality Control Service CLI")
console = Console()


@app.command()
def extract(
    pdf_dir: str = typer.Option(..., "--pdf-dir", "-d", help="Directory containing PDF files"),
    output: str = typer.Option(..., "--output", "-o", help="Output JSON file path"),
):
    """
    Extract invoice data from PDF files in a directory.
    
    Example:
        python -m invoice_qc.cli extract --pdf-dir pdfs --output extracted.json
    """
    try:
        pdf_path = Path(pdf_dir)
        if not pdf_path.exists():
            console.print(f"[red]Error: Directory not found: {pdf_dir}[/red]")
            sys.exit(1)
        
        console.print(f"[cyan]Extracting invoices from {pdf_dir}...[/cyan]")
        invoices = extract_invoices_from_directory(pdf_path)
        
        if not invoices:
            console.print("[yellow]Warning: No invoices extracted.[/yellow]")
            sys.exit(1)
        
        save_invoices_to_json(invoices, output)
        console.print(f"[green]✓ Extracted {len(invoices)} invoices to {output}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error during extraction: {e}[/red]")
        sys.exit(1)


@app.command()
def validate(
    input: str = typer.Option(..., "--input", "-i", help="Input JSON file with invoices"),
    report: str = typer.Option(..., "--report", "-r", help="Output validation report JSON file"),
):
    """
    Validate invoices from a JSON file.
    
    Example:
        python -m invoice_qc.cli validate --input extracted.json --report report.json
    """
    try:
        console.print(f"[cyan]Loading invoices from {input}...[/cyan]")
        invoices = load_invoices_from_json(input)
        
        if not invoices:
            console.print("[yellow]Warning: No invoices found in input file.[/yellow]")
            sys.exit(1)
        
        console.print(f"[cyan]Validating {len(invoices)} invoices...[/cyan]")
        validator = InvoiceValidator()
        results = validator.validate_batch(invoices)
        
        # Save report
        report_path = Path(report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        # Print summary to stdout
        summary = results["summary"]
        console.print("\n[bold]Validation Summary:[/bold]")
        console.print(f"  Total Invoices: {summary['total_invoices']}")
        console.print(f"  [green]Valid: {summary['valid_invoices']}[/green]")
        console.print(f"  [red]Invalid: {summary['invalid_invoices']}[/red]")
        
        if summary['error_counts']:
            console.print("\n[bold]Error Counts:[/bold]")
            for error_type, count in summary['error_counts'].items():
                console.print(f"  {error_type}: {count}")
        
        # Print invalid invoices
        invalid_results = [r for r in results["results"] if not r["is_valid"]]
        if invalid_results:
            console.print("\n[bold red]Invalid Invoices:[/bold red]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Invoice ID")
            table.add_column("Errors")
            
            for result in invalid_results[:10]:  # Show first 10
                errors_str = "; ".join(result["errors"][:3])  # Show first 3 errors
                if len(result["errors"]) > 3:
                    errors_str += f" ... (+{len(result['errors']) - 3} more)"
                table.add_row(result["invoice_id"], errors_str)
            
            console.print(table)
            
            if len(invalid_results) > 10:
                console.print(f"\n[yellow]... and {len(invalid_results) - 10} more invalid invoices[/yellow]")
        
        console.print(f"\n[green]✓ Validation report saved to {report}[/green]")
        
        # Exit with code 1 if invalid invoices exist
        if summary['invalid_invoices'] > 0:
            sys.exit(1)
        
    except FileNotFoundError as e:
        console.print(f"[red]Error: File not found: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error during validation: {e}[/red]")
        sys.exit(1)


@app.command()
def full_run(
    pdf_dir: str = typer.Option(..., "--pdf-dir", "-d", help="Directory containing PDF files"),
    report: str = typer.Option(..., "--report", "-r", help="Output validation report JSON file"),
):
    """
    Extract invoices from PDFs and validate them in one step.
    
    Example:
        python -m invoice_qc.cli full-run --pdf-dir pdfs --report report.json
    """
    try:
        # Step 1: Extract
        pdf_path = Path(pdf_dir)
        if not pdf_path.exists():
            console.print(f"[red]Error: Directory not found: {pdf_dir}[/red]")
            sys.exit(1)
        
        console.print(f"[cyan]Step 1: Extracting invoices from {pdf_dir}...[/cyan]")
        invoices = extract_invoices_from_directory(pdf_path)
        
        if not invoices:
            console.print("[yellow]Warning: No invoices extracted.[/yellow]")
            sys.exit(1)
        
        console.print(f"[green]✓ Extracted {len(invoices)} invoices[/green]")
        
        # Step 2: Validate
        console.print(f"[cyan]Step 2: Validating {len(invoices)} invoices...[/cyan]")
        validator = InvoiceValidator()
        results = validator.validate_batch(invoices)
        
        # Save report
        report_path = Path(report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        # Print summary
        summary = results["summary"]
        console.print("\n[bold]Validation Summary:[/bold]")
        console.print(f"  Total Invoices: {summary['total_invoices']}")
        console.print(f"  [green]Valid: {summary['valid_invoices']}[/green]")
        console.print(f"  [red]Invalid: {summary['invalid_invoices']}[/red]")
        
        if summary['error_counts']:
            console.print("\n[bold]Error Counts:[/bold]")
            for error_type, count in summary['error_counts'].items():
                console.print(f"  {error_type}: {count}")
        
        console.print(f"\n[green]✓ Full run completed. Report saved to {report}[/green]")
        
        # Exit with code 1 if invalid invoices exist
        if summary['invalid_invoices'] > 0:
            sys.exit(1)
        
    except Exception as e:
        console.print(f"[red]Error during full run: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    app()

