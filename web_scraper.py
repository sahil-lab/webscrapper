import os
import requests
from bs4 import BeautifulSoup
import chardet
from tqdm import tqdm
import time
import re
from urllib.parse import urlparse, urljoin

class WebScraper:
    def __init__(self, headers=None, timeout=30):
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.timeout = timeout
        self.session = requests.Session()
        
    def fetch_url(self, url):
        """
        Fetch content from a URL with error handling
        """
        try:
            response = self.session.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Detect encoding
            if response.encoding == 'ISO-8859-1':
                encoding = chardet.detect(response.content)['encoding']
                if encoding:
                    response.encoding = encoding
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
            
    def extract_text_from_html(self, html_content):
        """
        Extract clean text from HTML content
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
            
        # Get text and clean it
        text = soup.get_text(separator='\n')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
        
    def extract_main_content(self, html_content):
        """
        Attempt to extract the main content from a page
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Try to find main content containers
        main_content = None
        for selector in ['main', 'article', '[role="main"]', '#content', '.content', '#main', '.main']:
            content = soup.select(selector)
            if content:
                main_content = content[0]
                break
                
        if main_content:
            # Clean the content
            for element in main_content(["script", "style"]):
                element.decompose()
                
            text = main_content.get_text(separator='\n')
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text
        else:
            # If no main content identified, return the full text
            return self.extract_text_from_html(html_content)
            
    def extract_links(self, html_content, base_url):
        """
        Extract all links from the HTML content
        """
        soup = BeautifulSoup(html_content, 'lxml')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Convert relative URLs to absolute
            if not bool(urlparse(href).netloc):
                href = urljoin(base_url, href)
            links.append(href)
            
        return links
        
    def extract_metadata(self, html_content):
        """
        Extract metadata from the HTML content
        """
        soup = BeautifulSoup(html_content, 'lxml')
        metadata = {}
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.string.strip()
            
        # Extract meta description
        description = soup.find('meta', attrs={'name': 'description'})
        if description:
            metadata['description'] = description.get('content', '')
            
        # Extract author
        author = soup.find('meta', attrs={'name': 'author'})
        if author:
            metadata['author'] = author.get('content', '')
            
        # Open Graph metadata
        for meta in soup.find_all('meta', property=re.compile(r'^og:')):
            property_name = meta.get('property', '').replace('og:', 'og_')
            metadata[property_name] = meta.get('content', '')
            
        return metadata
        
    def scrape_to_text(self, url, output_dir="output", extract_main=True, include_metadata=True):
        """
        Scrape a URL and save its content as text
        """
        response = self.fetch_url(url)
        if not response:
            return None
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare filename from URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path.strip('/').replace('/', '_')
        if not path:
            path = 'index'
        filename = f"{domain}_{path}.txt"
        filepath = os.path.join(output_dir, filename)
        
        # Extract content
        if extract_main:
            text_content = self.extract_main_content(response.text)
        else:
            text_content = self.extract_text_from_html(response.text)
            
        # Extract metadata if requested
        metadata_text = ""
        if include_metadata:
            metadata = self.extract_metadata(response.text)
            metadata_text = "--- METADATA ---\n"
            for key, value in metadata.items():
                metadata_text += f"{key}: {value}\n"
            metadata_text += "\n--- CONTENT ---\n"
            
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(metadata_text + text_content)
            
        return filepath 