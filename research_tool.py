import os
import sys
import argparse
from web_scraper import WebScraper
from urllib.parse import urlparse
import time
from tqdm import tqdm

class ResearchTool:
    def __init__(self, output_dir="research_data"):
        self.output_dir = output_dir
        self.scraper = WebScraper()
        os.makedirs(output_dir, exist_ok=True)
        
    def scrape_single_url(self, url, extract_main=True):
        """
        Scrape a single URL and return the path to the saved file
        """
        print(f"Scraping: {url}")
        file_path = self.scraper.scrape_to_text(url, self.output_dir, extract_main)
        if file_path:
            print(f"Content saved to: {file_path}")
            return file_path
        else:
            print(f"Failed to scrape: {url}")
            return None
            
    def scrape_multiple_urls(self, urls, extract_main=True, delay=1):
        """
        Scrape multiple URLs with a delay between requests
        """
        results = []
        
        for url in tqdm(urls, desc="Scraping URLs"):
            file_path = self.scraper.scrape_to_text(url, self.output_dir, extract_main)
            if file_path:
                results.append((url, file_path))
            else:
                results.append((url, None))
                
            # Add delay to avoid overwhelming servers
            if delay > 0 and url != urls[-1]:  # No need to delay after the last URL
                time.sleep(delay)
                
        return results
        
    def crawl_website(self, start_url, max_pages=10, same_domain_only=True, delay=1):
        """
        Crawl a website starting from a URL and following links
        """
        visited_urls = set()
        to_visit = [start_url]
        results = []
        base_domain = urlparse(start_url).netloc
        
        pbar = tqdm(total=max_pages, desc="Crawling website")
        
        while to_visit and len(visited_urls) < max_pages:
            url = to_visit.pop(0)
            
            if url in visited_urls:
                continue
                
            visited_urls.add(url)
            
            response = self.scraper.fetch_url(url)
            if not response:
                continue
                
            # Save the content
            file_path = self.scraper.scrape_to_text(url, self.output_dir)
            if file_path:
                results.append((url, file_path))
                pbar.update(1)
            
            # Extract links and add to queue
            links = self.scraper.extract_links(response.text, url)
            for link in links:
                if link not in visited_urls and link not in to_visit:
                    # If same_domain_only is True, only add links from the same domain
                    if same_domain_only:
                        link_domain = urlparse(link).netloc
                        if link_domain != base_domain:
                            continue
                    to_visit.append(link)
                    
            # Add delay to avoid overwhelming servers
            if delay > 0 and len(visited_urls) < max_pages:
                time.sleep(delay)
                
        pbar.close()
        return results
        
    def generate_summary_file(self, scraped_results):
        """
        Generate a summary file of all scraped content
        """
        summary_path = os.path.join(self.output_dir, "research_summary.txt")
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# RESEARCH SUMMARY\n\n")
            f.write(f"Total sources: {len(scraped_results)}\n\n")
            
            for i, (url, filepath) in enumerate(scraped_results, 1):
                f.write(f"## Source {i}: {url}\n")
                if filepath:
                    try:
                        with open(filepath, 'r', encoding='utf-8') as source_file:
                            # Extract metadata section if it exists
                            content = source_file.read()
                            if "--- METADATA ---" in content:
                                metadata = content.split("--- CONTENT ---")[0]
                                f.write(f"\n{metadata}\n")
                            else:
                                f.write("\nNo metadata available\n")
                    except Exception as e:
                        f.write(f"\nError reading file: {e}\n")
                else:
                    f.write("\nFailed to scrape this URL\n")
                    
                f.write("\n" + "-"*40 + "\n\n")
                
        print(f"Summary file generated at: {summary_path}")
        return summary_path


def main():
    parser = argparse.ArgumentParser(description="Web Research Tool")
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
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    tool = ResearchTool(output_dir=args.output_dir)
    
    if args.command == "scrape":
        extract_main = not args.full_page
        tool.scrape_single_url(args.url, extract_main=extract_main)
        
    elif args.command == "batch":
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


if __name__ == "__main__":
    main() 