# Web Scraping Research Tool

A powerful research tool that can scrape web content from URLs and convert it to text format. This tool is designed to help with deep research by extracting and organizing content from various web sources.

## Features

- Extract and clean text content from web pages
- Focus on main content or scrape the entire page
- Process single URLs or batch process multiple URLs
- Crawl websites by following links from a starting URL
- Extract metadata from web pages
- Generate research summaries
- Convert scraped data to various formats (JSON, CSV, Markdown)
- Unified workflow combining scraping and conversion
- User-friendly graphical interface

## Requirements

- Python 3.7+
- Required packages (install via `pip install -r requirements.txt`):
  - requests
  - beautifulsoup4
  - lxml
  - chardet
  - tqdm
  - tkinter (usually included with Python)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Graphical User Interface

For most users, the graphical interface provides the easiest way to use the tool:

```bash
python ui_app.py
```

The GUI includes tabs for:
- **Single URL**: Scrape content from a single web page
- **Batch URLs**: Process multiple URLs from a text file
- **Web Crawler**: Crawl a website by following links
- **Convert Format**: Convert previously scraped data to different formats

Each tab includes the appropriate options and a console output area for viewing progress.

### Command Line Interface

The tool also provides both individual component scripts and a unified command-line interface through `research_assistant.py`. 

#### Using the Unified Interface

```bash
python research_assistant.py [command] [options]
```

Available commands:
- `scrape`: Scrape a single URL
- `batch`: Scrape multiple URLs from a file
- `crawl`: Crawl a website following links
- `convert`: Convert scraped data to different formats
- `workflow`: Run a complete research workflow (scrape + convert)

#### Examples

```bash
# Scrape a single URL
python research_assistant.py scrape https://example.com

# Batch process multiple URLs from a file
python research_assistant.py batch urls.txt --delay 2

# Crawl a website following links
python research_assistant.py crawl https://example.com --max-pages 20

# Convert scraped data to JSON
python research_assistant.py convert --format json

# Full research workflow (scrape URLs from file and convert to markdown)
python research_assistant.py workflow urls.txt --format markdown
```

### Individual Components

You can also use the individual component scripts directly:

#### Scraping a Single URL

```bash
python research_tool.py scrape https://example.com
```

Options:
- `--output-dir, -o`: Directory to save scraped data (default: "research_data")
- `--full-page, -f`: Scrape the full page instead of just the main content

#### Batch Processing Multiple URLs

```bash
python research_tool.py batch urls.txt
```

Options:
- `--output-dir, -o`: Directory to save scraped data (default: "research_data")
- `--delay, -d`: Delay between requests in seconds (default: 1.0)
- `--full-page, -f`: Scrape the full page instead of just the main content

#### Crawling a Website

```bash
python research_tool.py crawl https://example.com
```

Options:
- `--output-dir, -o`: Directory to save scraped data (default: "research_data")
- `--max-pages, -m`: Maximum number of pages to crawl (default: 10)
- `--all-domains, -a`: Crawl links from all domains, not just the starting domain
- `--delay, -d`: Delay between requests in seconds (default: 1.0)

#### Converting Scraped Data to Other Formats

```bash
python format_converter.py --format json
```

Available formats:
- `json`: Convert to a structured JSON file
- `csv`: Convert to a CSV file for spreadsheet applications
- `markdown` or `md`: Convert to a Markdown file

Options:
- `--input-dir, -i`: Directory containing scraped text files (default: "research_data")
- `--output, -o`: Output file path (default is based on format and input directory)

### Programmatic Usage

The tool can also be used programmatically in your own Python scripts. See `example_usage.py` for demonstration.

## Output Format

The tool saves scraped content as text files in the specified output directory. Each file includes:

1. Metadata section (when available):
   - Page title
   - Description
   - Author information
   - Open Graph metadata

2. Main content in clean text format

For batch processing and website crawling, a summary file is also generated that includes information about all scraped sources.

When using the conversion features, the following output formats are available:
- **JSON**: Structured data format that preserves all metadata and content
- **CSV**: Tabular format that can be opened in spreadsheet applications
- **Markdown**: Readable text format with formatting for easy viewing in markdown-compatible applications

## Notes

- Be mindful of website terms of service when scraping content.
- Use appropriate delays between requests to avoid overwhelming servers.
- Some websites may block automated scraping tools.

## License

MIT 