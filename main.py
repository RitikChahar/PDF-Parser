import os
import time
import glob
import asyncio
from pathlib import Path
from utils.logutils import log_info, log_success, log_error
from src.parser import PDFParser


async def process_single_pdf(pdf_path: str, base_output_dir: str):
    pdf_filename = Path(pdf_path).stem
    output_dir = os.path.join(base_output_dir, pdf_filename)
    
    os.makedirs(output_dir, exist_ok=True)
    
    log_info(f"Processing {pdf_filename}")
    
    parser = PDFParser(pdf_path, output_dir)
    
    try:
        results = await parser.extract_all()
        log_success(f"Completed {pdf_filename}")
        return 1
    except Exception as e:
        log_error(f"Failed to process {pdf_filename}: {str(e)}")
        return 0


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
    
    async def process_with_semaphore(pdf_path):
        async with semaphore:
            return await process_single_pdf(pdf_path, base_output_dir)
    
    tasks = [process_with_semaphore(pdf_path) for pdf_path in pdf_files]
    results = await asyncio.gather(*tasks)
    
    processed_count = sum(results)
    
    total_end_time = time.time()
    total_execution_time = total_end_time - total_start_time
    
    log_success(f"Processed {processed_count} PDFs in {total_execution_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())