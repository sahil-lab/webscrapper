import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import os
import sys
import queue
import time
from research_tool import ResearchTool
from format_converter import FormatConverter

class RedirectText:
    """Class to redirect stdout to a tkinter Text widget"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.queue = queue.Queue()
        self.updating = True
        threading.Thread(target=self.update_widget_loop, daemon=True).start()

    def write(self, string):
        self.queue.put(string)
        
    def flush(self):
        pass
        
    def update_widget_loop(self):
        while self.updating:
            try:
                while True:
                    string = self.queue.get_nowait()
                    self.text_widget.configure(state="normal")
                    self.text_widget.insert("end", string)
                    self.text_widget.see("end")
                    self.text_widget.configure(state="disabled")
                    self.queue.task_done()
            except queue.Empty:
                time.sleep(0.1)
                
    def close(self):
        self.updating = False


class ResearchToolApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Web Scraping Research Tool")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Create a style
        self.style = ttk.Style(self)
        self.style.theme_use('clam')  # Use a more modern theme
        
        # Configure tab color and style
        self.style.configure('TNotebook.Tab', padding=[12, 8], font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TLabel', font=('Arial', 10))
        self.style.configure('TEntry', font=('Arial', 10))
        
        # Create the tab control
        self.tab_control = ttk.Notebook(self)
        
        # Create tabs
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab3 = ttk.Frame(self.tab_control)
        self.tab4 = ttk.Frame(self.tab_control)
        
        # Add tabs to notebook
        self.tab_control.add(self.tab1, text="Single URL")
        self.tab_control.add(self.tab2, text="Batch URLs")
        self.tab_control.add(self.tab3, text="Web Crawler")
        self.tab_control.add(self.tab4, text="Convert Format")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Setup each tab
        self.setup_single_url_tab()
        self.setup_batch_urls_tab()
        self.setup_crawler_tab()
        self.setup_converter_tab()
        
        # Setup the output console at the bottom
        self.setup_console()
        
        # Store active threads
        self.active_threads = []
        
        # Cleanup on close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_single_url_tab(self):
        # Create a frame for the top controls
        frame = ttk.Frame(self.tab1, padding=10)
        frame.pack(fill="x", expand=False)
        
        # URL input
        ttk.Label(frame, text="URL:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.single_url_entry = ttk.Entry(frame, width=70)
        self.single_url_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        
        # Output directory
        ttk.Label(frame, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        dir_frame = ttk.Frame(frame)
        dir_frame.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        
        self.single_output_dir = ttk.Entry(dir_frame, width=60)
        self.single_output_dir.pack(side="left", fill="x", expand=True)
        self.single_output_dir.insert(0, "research_data")
        
        browse_btn = ttk.Button(dir_frame, text="Browse...", command=lambda: self.browse_directory(self.single_output_dir))
        browse_btn.pack(side="right", padx=5)
        
        # Options
        options_frame = ttk.LabelFrame(self.tab1, text="Options", padding=10)
        options_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        self.single_full_page_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Scrape Full Page (not just main content)", 
                      variable=self.single_full_page_var).pack(anchor="w")
        
        # Action buttons
        action_frame = ttk.Frame(self.tab1, padding=10)
        action_frame.pack(fill="x", expand=False)
        
        ttk.Button(action_frame, text="Scrape URL", 
                 command=self.scrape_single_url).pack(side="left", padx=5)
        
    def setup_batch_urls_tab(self):
        # Create a frame for the top controls
        frame = ttk.Frame(self.tab2, padding=10)
        frame.pack(fill="x", expand=False)
        
        # URL file input
        ttk.Label(frame, text="URLs File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        file_frame = ttk.Frame(frame)
        file_frame.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        
        self.batch_file_entry = ttk.Entry(file_frame, width=60)
        self.batch_file_entry.pack(side="left", fill="x", expand=True)
        
        browse_file_btn = ttk.Button(file_frame, text="Browse...", 
                                    command=lambda: self.browse_file(self.batch_file_entry))
        browse_file_btn.pack(side="right", padx=5)
        
        # Output directory
        ttk.Label(frame, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        dir_frame = ttk.Frame(frame)
        dir_frame.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        
        self.batch_output_dir = ttk.Entry(dir_frame, width=60)
        self.batch_output_dir.pack(side="left", fill="x", expand=True)
        self.batch_output_dir.insert(0, "research_data")
        
        browse_btn = ttk.Button(dir_frame, text="Browse...", 
                              command=lambda: self.browse_directory(self.batch_output_dir))
        browse_btn.pack(side="right", padx=5)
        
        # Options
        options_frame = ttk.LabelFrame(self.tab2, text="Options", padding=10)
        options_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        self.batch_full_page_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Scrape Full Page (not just main content)", 
                      variable=self.batch_full_page_var).pack(anchor="w")
        
        delay_frame = ttk.Frame(options_frame)
        delay_frame.pack(fill="x", expand=True, pady=5)
        
        ttk.Label(delay_frame, text="Delay between requests (seconds):").pack(side="left", padx=5)
        self.batch_delay_var = tk.DoubleVar(value=1.0)
        delay_spinner = ttk.Spinbox(delay_frame, from_=0.0, to=10.0, increment=0.5, 
                                  textvariable=self.batch_delay_var, width=5)
        delay_spinner.pack(side="left", padx=5)
        
        # Action buttons
        action_frame = ttk.Frame(self.tab2, padding=10)
        action_frame.pack(fill="x", expand=False)
        
        ttk.Button(action_frame, text="Process Batch", 
                 command=self.process_batch).pack(side="left", padx=5)
                 
        # Format conversion option
        convert_frame = ttk.LabelFrame(self.tab2, text="Auto Convert Results", padding=10)
        convert_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        self.batch_convert_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(convert_frame, text="Convert results to format:", 
                      variable=self.batch_convert_var).pack(side="left", padx=5)
        
        self.batch_format_var = tk.StringVar(value="json")
        format_combo = ttk.Combobox(convert_frame, textvariable=self.batch_format_var, 
                                  width=10, state="readonly")
        format_combo['values'] = ('json', 'csv', 'markdown')
        format_combo.pack(side="left", padx=5)
        
    def setup_crawler_tab(self):
        # Create a frame for the top controls
        frame = ttk.Frame(self.tab3, padding=10)
        frame.pack(fill="x", expand=False)
        
        # Start URL
        ttk.Label(frame, text="Start URL:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.crawler_url_entry = ttk.Entry(frame, width=70)
        self.crawler_url_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        
        # Output directory
        ttk.Label(frame, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        dir_frame = ttk.Frame(frame)
        dir_frame.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        
        self.crawler_output_dir = ttk.Entry(dir_frame, width=60)
        self.crawler_output_dir.pack(side="left", fill="x", expand=True)
        self.crawler_output_dir.insert(0, "research_data")
        
        browse_btn = ttk.Button(dir_frame, text="Browse...", 
                              command=lambda: self.browse_directory(self.crawler_output_dir))
        browse_btn.pack(side="right", padx=5)
        
        # Options
        options_frame = ttk.LabelFrame(self.tab3, text="Options", padding=10)
        options_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        max_pages_frame = ttk.Frame(options_frame)
        max_pages_frame.pack(fill="x", expand=True, pady=5)
        
        ttk.Label(max_pages_frame, text="Maximum pages to crawl:").pack(side="left", padx=5)
        self.max_pages_var = tk.IntVar(value=10)
        max_pages_spinner = ttk.Spinbox(max_pages_frame, from_=1, to=100, increment=1, 
                                      textvariable=self.max_pages_var, width=5)
        max_pages_spinner.pack(side="left", padx=5)
        
        delay_frame = ttk.Frame(options_frame)
        delay_frame.pack(fill="x", expand=True, pady=5)
        
        ttk.Label(delay_frame, text="Delay between requests (seconds):").pack(side="left", padx=5)
        self.crawler_delay_var = tk.DoubleVar(value=1.0)
        delay_spinner = ttk.Spinbox(delay_frame, from_=0.0, to=10.0, increment=0.5, 
                                  textvariable=self.crawler_delay_var, width=5)
        delay_spinner.pack(side="left", padx=5)
        
        self.all_domains_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Follow links to all domains (not just starting domain)", 
                      variable=self.all_domains_var).pack(anchor="w")
        
        # Action buttons
        action_frame = ttk.Frame(self.tab3, padding=10)
        action_frame.pack(fill="x", expand=False)
        
        ttk.Button(action_frame, text="Start Crawling", 
                 command=self.start_crawling).pack(side="left", padx=5)
                 
        # Format conversion option
        convert_frame = ttk.LabelFrame(self.tab3, text="Auto Convert Results", padding=10)
        convert_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        self.crawler_convert_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(convert_frame, text="Convert results to format:", 
                      variable=self.crawler_convert_var).pack(side="left", padx=5)
        
        self.crawler_format_var = tk.StringVar(value="json")
        format_combo = ttk.Combobox(convert_frame, textvariable=self.crawler_format_var, 
                                  width=10, state="readonly")
        format_combo['values'] = ('json', 'csv', 'markdown')
        format_combo.pack(side="left", padx=5)
        
    def setup_converter_tab(self):
        # Create a frame for the top controls
        frame = ttk.Frame(self.tab4, padding=10)
        frame.pack(fill="x", expand=False)
        
        # Input directory
        ttk.Label(frame, text="Input Directory:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        dir_frame = ttk.Frame(frame)
        dir_frame.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        
        self.converter_input_dir = ttk.Entry(dir_frame, width=60)
        self.converter_input_dir.pack(side="left", fill="x", expand=True)
        self.converter_input_dir.insert(0, "research_data")
        
        browse_btn = ttk.Button(dir_frame, text="Browse...", 
                             command=lambda: self.browse_directory(self.converter_input_dir))
        browse_btn.pack(side="right", padx=5)
        
        # Output file
        ttk.Label(frame, text="Output File:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        file_frame = ttk.Frame(frame)
        file_frame.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        
        self.converter_output_file = ttk.Entry(file_frame, width=60)
        self.converter_output_file.pack(side="left", fill="x", expand=True)
        
        browse_btn = ttk.Button(file_frame, text="Browse...", 
                             command=lambda: self.save_file(self.converter_output_file))
        browse_btn.pack(side="right", padx=5)
        
        # Format options
        format_frame = ttk.LabelFrame(self.tab4, text="Format", padding=10)
        format_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        self.converter_format_var = tk.StringVar(value="json")
        
        ttk.Radiobutton(format_frame, text="JSON", value="json", 
                       variable=self.converter_format_var).pack(anchor="w")
        ttk.Radiobutton(format_frame, text="CSV", value="csv", 
                       variable=self.converter_format_var).pack(anchor="w")
        ttk.Radiobutton(format_frame, text="Markdown", value="markdown", 
                       variable=self.converter_format_var).pack(anchor="w")
        
        # Action buttons
        action_frame = ttk.Frame(self.tab4, padding=10)
        action_frame.pack(fill="x", expand=False)
        
        ttk.Button(action_frame, text="Convert", 
                 command=self.convert_data).pack(side="left", padx=5)
    
    def setup_console(self):
        # Console frame
        console_frame = ttk.LabelFrame(self, text="Console Output", padding=10)
        console_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Console output
        self.console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, state="disabled")
        self.console.pack(fill="both", expand=True)
        
        # Redirect stdout to the console
        self.redirect = RedirectText(self.console)
        sys.stdout = self.redirect
        
    def browse_directory(self, entry_widget):
        directory = filedialog.askdirectory()
        if directory:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, directory)
            
    def browse_file(self, entry_widget):
        file_path = filedialog.askopenfilename()
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)
            
    def save_file(self, entry_widget):
        file_format = self.converter_format_var.get()
        filetypes = [("All Files", "*.*")]
        
        if file_format == "json":
            filetypes = [("JSON Files", "*.json"), ("All Files", "*.*")]
            default_ext = ".json"
        elif file_format == "csv":
            filetypes = [("CSV Files", "*.csv"), ("All Files", "*.*")]
            default_ext = ".csv"
        elif file_format == "markdown":
            filetypes = [("Markdown Files", "*.md"), ("All Files", "*.*")]
            default_ext = ".md"
            
        file_path = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=default_ext)
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)
    
    def scrape_single_url(self):
        url = self.single_url_entry.get().strip()
        output_dir = self.single_output_dir.get().strip()
        extract_main = not self.single_full_page_var.get()
        
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
            
        thread = threading.Thread(target=self._scrape_single_url_thread, 
                                args=(url, output_dir, extract_main))
        thread.daemon = True
        thread.start()
        
        self.active_threads.append(thread)
        
    def _scrape_single_url_thread(self, url, output_dir, extract_main):
        try:
            print(f"Scraping URL: {url}")
            tool = ResearchTool(output_dir=output_dir)
            file_path = tool.scrape_single_url(url, extract_main=extract_main)
            
            if file_path:
                print(f"Successfully scraped URL. Content saved to: {file_path}")
            else:
                print("Failed to scrape URL.")
        except Exception as e:
            print(f"Error: {e}")
    
    def process_batch(self):
        file_path = self.batch_file_entry.get().strip()
        output_dir = self.batch_output_dir.get().strip()
        extract_main = not self.batch_full_page_var.get()
        delay = self.batch_delay_var.get()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a file containing URLs")
            return
            
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File not found: {file_path}")
            return
            
        thread = threading.Thread(target=self._process_batch_thread, 
                                args=(file_path, output_dir, extract_main, delay))
        thread.daemon = True
        thread.start()
        
        self.active_threads.append(thread)
        
    def _process_batch_thread(self, file_path, output_dir, extract_main, delay):
        try:
            with open(file_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
                
            if not urls:
                print("No URLs found in the file.")
                return
                
            print(f"Processing {len(urls)} URLs...")
            tool = ResearchTool(output_dir=output_dir)
            
            results = tool.scrape_multiple_urls(urls, extract_main=extract_main, delay=delay)
            
            success_count = sum(1 for _, filepath in results if filepath)
            print(f"Successfully scraped {success_count} out of {len(urls)} URLs.")
            
            # Generate summary
            summary_path = tool.generate_summary_file(results)
            print(f"Summary file generated at: {summary_path}")
            
            # Convert if requested
            if self.batch_convert_var.get():
                format_type = self.batch_format_var.get()
                print(f"Converting results to {format_type} format...")
                
                converter = FormatConverter(input_dir=output_dir)
                
                if format_type == "json":
                    output_file = converter.convert_to_json()
                elif format_type == "csv":
                    output_file = converter.convert_to_csv()
                elif format_type == "markdown":
                    output_file = converter.convert_to_markdown()
                    
                print(f"Conversion complete. Output file: {output_file}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    def start_crawling(self):
        start_url = self.crawler_url_entry.get().strip()
        output_dir = self.crawler_output_dir.get().strip()
        max_pages = self.max_pages_var.get()
        delay = self.crawler_delay_var.get()
        same_domain_only = not self.all_domains_var.get()
        
        if not start_url:
            messagebox.showerror("Error", "Please enter a start URL")
            return
            
        thread = threading.Thread(target=self._start_crawling_thread, 
                                args=(start_url, output_dir, max_pages, delay, same_domain_only))
        thread.daemon = True
        thread.start()
        
        self.active_threads.append(thread)
        
    def _start_crawling_thread(self, start_url, output_dir, max_pages, delay, same_domain_only):
        try:
            print(f"Starting crawl from: {start_url}")
            print(f"Maximum pages: {max_pages}")
            
            tool = ResearchTool(output_dir=output_dir)
            results = tool.crawl_website(
                start_url=start_url,
                max_pages=max_pages,
                same_domain_only=same_domain_only,
                delay=delay
            )
            
            success_count = sum(1 for _, filepath in results if filepath)
            print(f"Successfully crawled and scraped {success_count} pages.")
            
            # Generate summary
            summary_path = tool.generate_summary_file(results)
            print(f"Summary file generated at: {summary_path}")
            
            # Convert if requested
            if self.crawler_convert_var.get():
                format_type = self.crawler_format_var.get()
                print(f"Converting results to {format_type} format...")
                
                converter = FormatConverter(input_dir=output_dir)
                
                if format_type == "json":
                    output_file = converter.convert_to_json()
                elif format_type == "csv":
                    output_file = converter.convert_to_csv()
                elif format_type == "markdown":
                    output_file = converter.convert_to_markdown()
                    
                print(f"Conversion complete. Output file: {output_file}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    def convert_data(self):
        input_dir = self.converter_input_dir.get().strip()
        output_file = self.converter_output_file.get().strip()
        format_type = self.converter_format_var.get()
        
        if not os.path.exists(input_dir):
            messagebox.showerror("Error", f"Input directory not found: {input_dir}")
            return
            
        thread = threading.Thread(target=self._convert_data_thread, 
                                args=(input_dir, output_file, format_type))
        thread.daemon = True
        thread.start()
        
        self.active_threads.append(thread)
        
    def _convert_data_thread(self, input_dir, output_file, format_type):
        try:
            print(f"Converting data from {input_dir} to {format_type} format...")
            
            converter = FormatConverter(input_dir=input_dir)
            
            if format_type == "json":
                result = converter.convert_to_json(output_file=output_file)
            elif format_type == "csv":
                result = converter.convert_to_csv(output_file=output_file)
            elif format_type == "markdown":
                result = converter.convert_to_markdown(output_file=output_file)
                
            if result:
                print(f"Conversion successful. Output file: {result}")
            else:
                print("Conversion failed.")
                
        except Exception as e:
            print(f"Error: {e}")
    
    def on_closing(self):
        # Restore stdout
        if hasattr(self, 'redirect'):
            sys.stdout = sys.__stdout__
            self.redirect.close()
        
        # Destroy the window
        self.destroy()


if __name__ == "__main__":
    app = ResearchToolApp()
    app.mainloop() 