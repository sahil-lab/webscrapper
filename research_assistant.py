#!/usr/bin/env python3
import argparse
import sys
import os
import time
from research_tool import ResearchTool
from format_converter import FormatConverter


def main():
    parser = argparse.ArgumentParser(
        description="Research Assistant - A tool for web scraping research",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape a single URL
  python research_assistant.py scrape https://example.com
  
  # Batch process multiple URLs from a file
  python research_assistant.py batch urls.txt
  
  # Crawl a website following links
  python research_assistant.py crawl https://example.com --max-pages 20
  
  # Convert scraped data to JSON
  python research_assistant.py convert --format json
  
  # Full research workflow (scrape and convert)
  python research_assistant.py workflow urls.txt --format markdown
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape a single URL")
    scrape_parser.add_argument("url", help="URL to scrape")
    scrape_parser.add_argument("--output-dir", "-o", default="research_data", 
                              help="Directory to save scraped data")
    scrape_parser.add_argument("--full-page", "-f", action="store_true", 
                              help="Scrape the full page instead of just the main content")
    
    # Batch scrape command
    batch_parser = subparsers.add_parser("batch", help="Scrape multiple URLs from a file")
    batch_parser.add_argument("file", help="File containing URLs (one per line)")
    batch_parser.add_argument("--output-dir", "-o", default="research_data", 
                             help="Directory to save scraped data")
    batch_parser.add_argument("--delay", "-d", type=float, default=1.0, 
                             help="Delay between requests in seconds")
    batch_parser.add_argument("--full-page", "-f", action="store_true", 
                             help="Scrape the full page instead of just the main content")
    
    # Crawl command
    crawl_parser = subparsers.add_parser("crawl", help="Crawl a website")
    crawl_parser.add_argument("url", help="Starting URL to crawl")
    crawl_parser.add_argument("--output-dir", "-o", default="research_data", 
                             help="Directory to save scraped data")
    crawl_parser.add_argument("--max-pages", "-m", type=int, default=10, 
                             help="Maximum number of pages to crawl")
    crawl_parser.add_argument("--all-domains", "-a", action="store_true", 
                             help="Crawl links from all domains, not just the starting domain")
    crawl_parser.add_argument("--delay", "-d", type=float, default=1.0, 
                             help="Delay between requests in seconds")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert scraped data to different formats")
    convert_parser.add_argument("--input-dir", "-i", default="research_data", 
                             help="Directory containing scraped text files")
    convert_parser.add_argument("--output", "-o", 
                             help="Output file path (default is based on format and input directory)")
    convert_parser.add_argument("--format", "-f", choices=["json", "csv", "markdown", "md"], required=True,
                             help="Output format")
    
    # Workflow command (combines scraping and conversion)
    workflow_parser = subparsers.add_parser("workflow", help="Run a complete research workflow")
    workflow_parser.add_argument("file", help="File containing URLs (one per line)")
    workflow_parser.add_argument("--output-dir", "-o", default="research_data", 
                              help="Directory to save scraped data")
    workflow_parser.add_argument("--delay", "-d", type=float, default=1.0, 
                              help="Delay between requests in seconds")
    workflow_parser.add_argument("--format", "-f", choices=["json", "csv", "markdown", "md"], required=True,
                              help="Output format for conversion")
    workflow_parser.add_argument("--full-page", action="store_true", 
                              help="Scrape the full page instead of just the main content")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "scrape":
        tool = ResearchTool(output_dir=args.output_dir)
        extract_main = not args.full_page
        tool.scrape_single_url(args.url, extract_main=extract_main)
        
    elif args.command == "batch":
        tool = ResearchTool(output_dir=args.output_dir)
        try:
            with open(args.file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
                
            if not urls:
                print("No URLs found in the file.")
                return
                
            print(f"Scraping {len(urls)} URLs...")
            extract_main = not args.full_page
            results = tool.scrape_multiple_urls(urls, extract_main=extract_main, delay=args.delay)
            
            # Generate summary
            success_count = sum(1 for _, filepath in results if filepath)
            print(f"Successfully scraped {success_count} out of {len(urls)} URLs.")
            
            # Create summary file
            tool.generate_summary_file(results)
            
        except FileNotFoundError:
            print(f"File not found: {args.file}")
            
    elif args.command == "crawl":
        tool = ResearchTool(output_dir=args.output_dir)
        same_domain_only = not args.all_domains
        results = tool.crawl_website(
            args.url, 
            max_pages=args.max_pages, 
            same_domain_only=same_domain_only, 
            delay=args.delay
        )
        
        # Generate summary
        success_count = sum(1 for _, filepath in results if filepath)
        print(f"Successfully crawled and scraped {success_count} pages.")
        
        # Create summary file
        tool.generate_summary_file(results)
        
    elif args.command == "convert":
        converter = FormatConverter(input_dir=args.input_dir)
        
        if args.format == "json":
            converter.convert_to_json(output_file=args.output)
        elif args.format == "csv":
            converter.convert_to_csv(output_file=args.output)
        elif args.format in ["markdown", "md"]:
            converter.convert_to_markdown(output_file=args.output)
            
    elif args.command == "workflow":
        # Step 1: Scrape URLs
        print("=== STEP 1: SCRAPING URLs ===")
        tool = ResearchTool(output_dir=args.output_dir)
        
        try:
            with open(args.file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
                
            if not urls:
                print("No URLs found in the file.")
                return
                
            print(f"Scraping {len(urls)} URLs...")
            extract_main = not args.full_page
            results = tool.scrape_multiple_urls(urls, extract_main=extract_main, delay=args.delay)
            
            # Generate summary
            success_count = sum(1 for _, filepath in results if filepath)
            print(f"Successfully scraped {success_count} out of {len(urls)} URLs.")
            
            # Create summary file
            tool.generate_summary_file(results)
            
            # Step 2: Convert to the specified format
            print("\n=== STEP 2: CONVERTING DATA ===")
            converter = FormatConverter(input_dir=args.output_dir)
            
            if args.format == "json":
                converter.convert_to_json()
            elif args.format == "csv":
                converter.convert_to_csv()
            elif args.format in ["markdown", "md"]:
                converter.convert_to_markdown()
                
            print("\n=== WORKFLOW COMPLETE ===")
            print(f"Results are available in the '{args.output_dir}' directory.")
            
        except FileNotFoundError:
            print(f"File not found: {args.file}")


if __name__ == "__main__":
    main() 