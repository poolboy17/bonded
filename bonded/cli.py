#!/usr/bin/env python3
"""
Bonded CLI Tool - Main entry point
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import click
import pandas as pd
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .api.openrouter import OpenRouterClient
from .api.openai_client import OpenAIClient
from .qc.validator import QualityController
from .utils.csv_handler import CSVHandler
from .utils.rate_limiter import RateLimiter

# Load environment variables
load_dotenv()

console = Console()


@click.command()
@click.option(
    "--input", "-i",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Input CSV file with titles and metadata"
)
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    required=True,
    help="Output CSV file for rewritten content"
)
@click.option(
    "--qc-report", "-q",
    type=click.Path(dir_okay=False, path_type=Path),
    default="qc_report.json",
    help="Quality control report output file"
)
@click.option(
    "--max-workers", "-w",
    type=int,
    default=5,
    help="Maximum concurrent workers for parallel processing"
)
@click.option(
    "--rate-limit", "-r",
    type=int,
    default=100,
    help="Requests per minute rate limit"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview operations without making API calls"
)
def main(
    input: Path,
    output: Path,
    qc_report: Path,
    max_workers: int,
    rate_limit: int,
    dry_run: bool
):
    """
    Bonded CLI Tool - Content Generation and Quality Control
    
    Reads a CSV of titles + metadata, generates section outlines via OpenRouter,
    expands outlines and rewrites content using GPT-5, and enforces enterprise-quality QC.
    """
    console.print("[bold green]Bonded CLI Tool[/bold green] - Content Generation & QC")
    console.print(f"Input: {input}")
    console.print(f"Output: {output}")
    console.print(f"QC Report: {qc_report}")
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No API calls will be made[/yellow]")
    
    try:
        # Validate environment variables (skip for dry run)
        if not dry_run:
            _validate_environment()
        
        # Run the main processing pipeline
        asyncio.run(_process_content(
            input, output, qc_report, max_workers, rate_limit, dry_run
        ))
        
        console.print("[bold green]✓ Processing completed successfully![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]✗ Error: {e}[/bold red]")
        sys.exit(1)


def _validate_environment():
    """Validate required environment variables"""
    required_vars = ["OPENROUTER_API_KEY", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        console.print(f"[red]Missing required environment variables: {', '.join(missing_vars)}[/red]")
        console.print("Please check your .env file or set these variables.")
        sys.exit(1)


async def _process_content(
    input_path: Path,
    output_path: Path,
    qc_report_path: Path,
    max_workers: int,
    rate_limit: int,
    dry_run: bool
):
    """Main content processing pipeline"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Step 1: Load CSV data
        task = progress.add_task("Loading CSV data...", total=None)
        csv_handler = CSVHandler()
        df = csv_handler.load_csv(input_path)
        progress.update(task, description=f"Loaded {len(df)} rows from CSV")
        progress.remove_task(task)
        
        if dry_run:
            console.print(f"[cyan]Would process {len(df)} rows[/cyan]")
            console.print("Sample data:")
            console.print(df.head().to_string())
            return
        
        # Step 2: Initialize API clients
        task = progress.add_task("Initializing API clients...", total=None)
        openrouter_client = OpenRouterClient()
        openai_client = OpenAIClient()
        rate_limiter = RateLimiter(rate_limit, max_workers)
        progress.remove_task(task)
        
        # Step 3: Process content in parallel
        task = progress.add_task("Processing content...", total=len(df))
        
        processed_rows = []
        qc_results = []
        
        # Process rows in batches to respect rate limits
        for i in range(0, len(df), max_workers):
            batch = df.iloc[i:i + max_workers]
            
            # Create coroutines for batch processing
            coroutines = [
                _process_row(
                    row,
                    openrouter_client,
                    openai_client,
                    rate_limiter
                )
                for _, row in batch.iterrows()
            ]
            
            # Process batch
            batch_results = await asyncio.gather(*coroutines, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    console.print(f"[red]Error processing row: {result}[/red]")
                    continue
                
                processed_row, qc_result = result
                processed_rows.append(processed_row)
                qc_results.append(qc_result)
                
                progress.advance(task)
        
        progress.remove_task(task)
        
        # Step 4: Generate outputs
        task = progress.add_task("Generating outputs...", total=None)
        
        # Save processed CSV
        output_df = pd.DataFrame(processed_rows)
        csv_handler.save_csv(output_df, output_path)
        
        # Generate QC report
        qc_controller = QualityController()
        qc_controller.generate_report(qc_results, qc_report_path)
        
        progress.remove_task(task)
        
        # Display summary
        console.print(f"\n[green]✓ Processed {len(processed_rows)} rows successfully[/green]")
        console.print(f"[green]✓ Output saved to: {output_path}[/green]")
        console.print(f"[green]✓ QC report saved to: {qc_report_path}[/green]")


async def _process_row(row, openrouter_client, openai_client, rate_limiter):
    """Process a single row of content"""
    async with rate_limiter:
        try:
            # Step 1: Generate outline using OpenRouter
            outline = await openrouter_client.generate_outline(row)
            
            # Step 2: Expand and rewrite content using GPT-5
            content = await openai_client.rewrite_content(row, outline)
            
            # Step 3: Quality control check
            qc_controller = QualityController()
            qc_result = qc_controller.validate_content(content, row)
            
            # Create processed row
            processed_row = row.to_dict()
            processed_row['generated_outline'] = outline
            processed_row['rewritten_content'] = content
            processed_row['word_count'] = len(content.split())
            processed_row['qc_score'] = qc_result['overall_score']
            
            return processed_row, qc_result
            
        except Exception as e:
            raise Exception(f"Failed to process row {row.get('title', 'unknown')}: {e}")


if __name__ == "__main__":
    main()