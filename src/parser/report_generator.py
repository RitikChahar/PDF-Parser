import aiofiles
from pathlib import Path
from typing import Dict


class ReportGenerator:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
    
    async def generate_summary(self, results: Dict):
        report_path = self.output_dir / "extraction_summary.txt"
        
        async with aiofiles.open(report_path, "w", encoding="utf-8") as f:
            await f.write("PDF EXTRACTION SUMMARY\n")
            await f.write("=" * 50 + "\n\n")
            await f.write(f"PDF File: {results['pdf_path']}\n")
            await f.write(f"Output Directory: {results['output_directory']}\n\n")
            
            await f.write(f"Images Extracted: {len(results['images'])}\n")
            await f.write(f"Tables Extracted: {len(results['tables'])}\n\n")
            
            await f.write("FILES CREATED:\n")
            await f.write("- images/ (PNG files)\n")
            await f.write("- tables/ (CSV files)\n")
            await f.write("- text/ (TXT files with layout preserved and continuous)\n")
            await f.write("- extraction_summary.txt (this file)\n")