#!/usr/bin/env python3
"""
Example script demonstrating how to use the web scraping research tool programmatically.
This shows how you can integrate the tool into your own Python scripts.
"""

from research_tool import ResearchTool
from format_converter import FormatConverter
import os


def basic_example():
    """Basic example of scraping a single URL and converting to JSON"""
    print("=== BASIC EXAMPLE ===")
    
    # Create a research tool instance with a custom output directory
    output_dir = "example_output"
    tool = ResearchTool(output_dir=output_dir)
    
    # Scrape a single URL
    url = "https://en.wikipedia.org/wiki/Web_scraping"
    print(f"Scraping: {url}")
    file_path = tool.scrape_single_url(url)
    
    if file_path:
        # Convert to JSON
        converter = FormatConverter(input_dir=output_dir)
        json_path = converter.convert_to_json()
        print(f"Data converted to JSON: {json_path}")
    
    print()


def batch_example(urls=None):
    """Example of batch processing multiple URLs"""
    print("=== BATCH PROCESSING EXAMPLE ===")
    
    if urls is None:
        urls = [
            "https://en.wikipedia.org/wiki/Web_scraping",
            "https://en.wikipedia.org/wiki/Python_(programming_language)",
            "https://en.wikipedia.org/wiki/Data_mining"
        ]
    
    # Create a research tool instance
    output_dir = "batch_example_output"
    tool = ResearchTool(output_dir=output_dir)
    
    # Scrape multiple URLs
    print(f"Scraping {len(urls)} URLs...")
    results = tool.scrape_multiple_urls(urls, delay=1.5)
    
    # Generate a summary
    summary_path = tool.generate_summary_file(results)
    print(f"Summary generated: {summary_path}")
    
    # Convert to multiple formats
    converter = FormatConverter(input_dir=output_dir)
    
    # Convert to JSON
    json_path = converter.convert_to_json()
    print(f"Data converted to JSON: {json_path}")
    
    # Convert to CSV
    csv_path = converter.convert_to_csv()
    print(f"Data converted to CSV: {csv_path}")
    
    # Convert to Markdown
    md_path = converter.convert_to_markdown()
    print(f"Data converted to Markdown: {md_path}")
    
    print()


def crawl_example():
    """Example of crawling a website"""
    print("=== WEBSITE CRAWLING EXAMPLE ===")
    
    # Create a research tool instance
    output_dir = "crawl_example_output"
    tool = ResearchTool(output_dir=output_dir)
    
    # Crawl a website
    start_url = "https://en.wikipedia.org/wiki/Web_crawler"
    max_pages = 5
    print(f"Crawling from {start_url} (max {max_pages} pages)...")
    
    results = tool.crawl_website(
        start_url=start_url,
        max_pages=max_pages,
        same_domain_only=True,
        delay=1.5
    )
    
    # Generate a summary
    summary_path = tool.generate_summary_file(results)
    print(f"Summary generated: {summary_path}")
    
    # Convert to Markdown
    converter = FormatConverter(input_dir=output_dir)
    md_path = converter.convert_to_markdown()
    print(f"Data converted to Markdown: {md_path}")
    
    print()


def custom_processing_example():
    """Example showing how to do custom processing with the extracted data"""
    print("=== CUSTOM PROCESSING EXAMPLE ===")
    
    # Create a research tool instance
    output_dir = "custom_example_output"
    os.makedirs(output_dir, exist_ok=True)
    tool = ResearchTool(output_dir=output_dir)
    
    # Scrape a URL
    url = "https://en.wikipedia.org/wiki/Natural_language_processing"
    print(f"Scraping: {url}")
    file_path = tool.scrape_single_url(url)
    
    if file_path:
        # Do custom processing on the scraped content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Example: Count words
        words = content.split()
        word_count = len(words)
        print(f"Word count: {word_count}")
        
        # Example: Find most common words (excluding common stop words)
        stop_words = {'the', 'and', 'is', 'in', 'to', 'of', 'a', 'for', 'with', 'as', 'that', 'on', 'by', 'this', 'are'}
        word_freq = {}
        for word in words:
            word = word.lower().strip('.,()[]{}:;"\'')
            if word and word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top 10 words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print("\nTop 10 words:")
        for word, count in top_words:
            print(f"- {word}: {count}")
        
        # Save custom analysis
        analysis_path = os.path.join(output_dir, "word_analysis.txt")
        with open(analysis_path, 'w', encoding='utf-8') as f:
            f.write(f"Word count: {word_count}\n\n")
            f.write("Top 50 words:\n")
            for word, count in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:50]:
                f.write(f"{word}: {count}\n")
                
        print(f"\nCustom analysis saved to: {analysis_path}")
    
    print()


if __name__ == "__main__":
    # Run all examples
    basic_example()
    batch_example()
    crawl_example()
    custom_processing_example()
    
    print("All examples completed successfully!") 