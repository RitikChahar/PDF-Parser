import asyncio
import aiofiles
import os
import time
import glob
from pathlib import Path
from utils.logutils import log_info, log_success, log_error
from src.parser import PDFParser


async def process_single_pdf(pdf_path: str, base_output_dir: str, semaphore: asyncio.Semaphore):
    async with semaphore:
        pdf_filename = Path(pdf_path).stem
        output_dir = os.path.join(base_output_dir, pdf_filename)
        
        os.makedirs(output_dir, exist_ok=True)
        
        log_info(f"Processing {pdf_filename}")
        
        pdf_start_time = time.time()
        parser = PDFParser(pdf_path, output_dir)
        
        try:
            results = await parser.extract_all()
            pdf_end_time = time.time()
            pdf_execution_time = pdf_end_time - pdf_start_time
            
            total_pages = results["text"]["total_pages"] if results["text"] else 0
            
            summary_file = os.path.join(base_output_dir, "processing_summary.txt")
            
            file_exists = os.path.exists(summary_file)
            async with aiofiles.open(summary_file, "a", encoding="utf-8") as f:
                if not file_exists:
                    await f.write("PDF PROCESSING SUMMARY\n")
                    await f.write("=" * 50 + "\n")
                await f.write(f"{pdf_filename} - {total_pages} pages - {pdf_execution_time:.2f} seconds\n")
                await f.write(f"  Image Extraction: {results['execution_times']['image_extraction']:.2f}s\n")
                await f.write(f"  Table Extraction: {results['execution_times']['table_extraction']:.2f}s\n")
                await f.write(f"  Text Extraction: {results['execution_times']['text_extraction']:.2f}s\n")
                await f.write(f"  Images Found: {len(results['images'])}\n")
                await f.write(f"  Tables Found: {len(results['tables'])}\n")
                await f.write("-" * 30 + "\n")
            
            log_success(f"Completed {pdf_filename} in {pdf_execution_time:.2f} seconds")
            return 1
            
        except Exception as e:
            log_error(f"Failed to process {pdf_filename}: {str(e)}")
            return 0
        finally:
            parser.close()


async def main():
    test_pdfs_dir = "data/test_pdfs"
    base_output_dir = "data/pdf_output"
    
    if not os.path.exists(test_pdfs_dir):
        log_error("test_pdfs directory not found")
        return
    
    pdf_files = glob.glob(os.path.join(test_pdfs_dir, "*.pdf"))
    
    if not pdf_files:
        log_error("No PDF files found in test_pdfs directory")
        return
    
    total_start_time = time.time()
    
    os.makedirs(base_output_dir, exist_ok=True)
    
    semaphore = asyncio.Semaphore(3)
    
    tasks = [
        process_single_pdf(pdf_path, base_output_dir, semaphore)
        for pdf_path in pdf_files
    ]
    
    results = await asyncio.gather(*tasks)
    processed_count = sum(results)
    
    total_end_time = time.time()
    total_execution_time = total_end_time - total_start_time
    
    log_success(f"Processed {processed_count} PDFs in {total_execution_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())