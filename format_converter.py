import os
import json
import csv
import argparse
import glob
from pathlib import Path


class FormatConverter:
    def __init__(self, input_dir="research_data"):
        self.input_dir = input_dir
        
    def _read_text_file(self, filepath):
        """Read a text file and parse its metadata and content sections"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            metadata = {}
            main_content = content
            
            # Extract metadata if it exists
            if "--- METADATA ---" in content and "--- CONTENT ---" in content:
                metadata_text = content.split("--- METADATA ---")[1].split("--- CONTENT ---")[0].strip()
                main_content = content.split("--- CONTENT ---")[1].strip()
                
                # Parse metadata
                for line in metadata_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
            
            # Extract filename from path
            filename = os.path.basename(filepath)
            
            result = {
                "filename": filename,
                "filepath": filepath,
                "metadata": metadata,
                "content": main_content
            }
            
            return result
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return None
    
    def convert_to_json(self, output_file=None, pretty=True):
        """Convert all text files in the input directory to a single JSON file"""
        if output_file is None:
            output_file = os.path.join(self.input_dir, "research_data.json")
            
        # Get all text files
        filepaths = glob.glob(os.path.join(self.input_dir, "*.txt"))
        
        # Skip the summary file
        filepaths = [fp for fp in filepaths if os.path.basename(fp) != "research_summary.txt"]
        
        if not filepaths:
            print(f"No text files found in {self.input_dir}")
            return None
            
        # Read and parse all files
        data = []
        for filepath in filepaths:
            file_data = self._read_text_file(filepath)
            if file_data:
                data.append(file_data)
                
        # Write to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f)
                
        print(f"Converted {len(data)} files to JSON: {output_file}")
        return output_file
        
    def convert_to_csv(self, output_file=None):
        """Convert all text files in the input directory to a single CSV file"""
        if output_file is None:
            output_file = os.path.join(self.input_dir, "research_data.csv")
            
        # Get all text files
        filepaths = glob.glob(os.path.join(self.input_dir, "*.txt"))
        
        # Skip the summary file
        filepaths = [fp for fp in filepaths if os.path.basename(fp) != "research_summary.txt"]
        
        if not filepaths:
            print(f"No text files found in {self.input_dir}")
            return None
            
        # Read and parse all files
        data = []
        for filepath in filepaths:
            file_data = self._read_text_file(filepath)
            if file_data:
                # Flatten the metadata
                flat_data = {
                    "filename": file_data["filename"],
                    "filepath": file_data["filepath"],
                }
                
                # Add metadata with prefixes
                for key, value in file_data["metadata"].items():
                    flat_data[f"meta_{key}"] = value
                    
                # Add content
                flat_data["content"] = file_data["content"]
                
                data.append(flat_data)
                
        if not data:
            print("No data to convert")
            return None
            
        # Get all unique keys
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
            
        fieldnames = sorted(list(fieldnames))
        
        # Write to CSV
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            
        print(f"Converted {len(data)} files to CSV: {output_file}")
        return output_file
        
    def convert_to_markdown(self, output_file=None):
        """Convert all text files in the input directory to a single Markdown file"""
        if output_file is None:
            output_file = os.path.join(self.input_dir, "research_data.md")
            
        # Get all text files
        filepaths = glob.glob(os.path.join(self.input_dir, "*.txt"))
        
        # Skip the summary file
        filepaths = [fp for fp in filepaths if os.path.basename(fp) != "research_summary.txt"]
        
        if not filepaths:
            print(f"No text files found in {self.input_dir}")
            return None
            
        # Read and parse all files
        with open(output_file, 'w', encoding='utf-8') as out_file:
            out_file.write("# Research Data\n\n")
            
            for i, filepath in enumerate(filepaths, 1):
                file_data = self._read_text_file(filepath)
                if file_data:
                    # Write file header
                    title = file_data["metadata"].get("title", file_data["filename"])
                    out_file.write(f"## {i}. {title}\n\n")
                    
                    # Write metadata
                    if file_data["metadata"]:
                        out_file.write("### Metadata\n\n")
                        for key, value in file_data["metadata"].items():
                            out_file.write(f"- **{key}**: {value}\n")
                        out_file.write("\n")
                        
                    # Write content
                    out_file.write("### Content\n\n")
                    out_file.write(file_data["content"])
                    out_file.write("\n\n---\n\n")
                    
        print(f"Converted {len(filepaths)} files to Markdown: {output_file}")
        return output_file


def main():
    parser = argparse.ArgumentParser(description="Convert scraped data to different formats")
    parser.add_argument("--input-dir", "-i", default="research_data", 
                        help="Directory containing scraped text files")
    parser.add_argument("--output", "-o", 
                        help="Output file path (default is based on format and input directory)")
    parser.add_argument("--format", "-f", choices=["json", "csv", "markdown", "md"], required=True,
                        help="Output format")
    
    args = parser.parse_args()
    
    converter = FormatConverter(input_dir=args.input_dir)
    
    if args.format == "json":
        converter.convert_to_json(output_file=args.output)
    elif args.format == "csv":
        converter.convert_to_csv(output_file=args.output)
    elif args.format in ["markdown", "md"]:
        converter.convert_to_markdown(output_file=args.output)


if __name__ == "__main__":
    main() 