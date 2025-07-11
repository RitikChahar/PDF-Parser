import fitz
import asyncio
import time
from pathlib import Path
from typing import List, Dict
from utils.logutils import log_info, log_success, log_error

from .image_extractor import ImageExtractor
from .table_extractor import TableExtractor
from .text_extractor import TextExtractor
from .report_generator import ReportGenerator


class PDFParser:
    def __init__(self, pdf_path: str, output_dir: str = "pdf_output"):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.doc = None
        
        self.table_extractor = TableExtractor(pdf_path, self.output_dir)
        self.report_generator = ReportGenerator(self.output_dir)
    
    def _open_document(self):
        if self.doc is None:
            self.doc = fitz.open(self.pdf_path)
    
    def _close_document(self):
        if self.doc:
            self.doc.close()
            self.doc = None
    
    async def extract_images(self) -> tuple[List[Dict], float]:
        start_time = time.time()
        image_extractor = ImageExtractor(self.doc, self.output_dir)
        result = await image_extractor.extract()
        end_time = time.time()
        return result, end_time - start_time
    
    async def extract_tables(self) -> tuple[List[Dict], float]:
        start_time = time.time()
        result = await self.table_extractor.extract()
        end_time = time.time()
        return result, end_time - start_time
    
    async def extract_text(self) -> tuple[Dict, float]:
        start_time = time.time()
        text_extractor = TextExtractor(self.doc, self.output_dir)
        result = await text_extractor.extract()
        end_time = time.time()
        return result, end_time - start_time
    
    async def extract_all(self) -> Dict:
        log_info("Starting PDF extraction")
        
        try:
            self._open_document()
            
            results = {
                "pdf_path": self.pdf_path,
                "output_directory": str(self.output_dir),
                "images": [],
                "tables": [],
                "text": {},
                "execution_times": {
                    "image_extraction": 0.0,
                    "table_extraction": 0.0,
                    "text_extraction": 0.0
                }
            }
            
            async def safe_extract_images():
                try:
                    return await self.extract_images()
                except Exception as e:
                    log_error(f"Image extraction failed: {str(e)}")
                    return [], 0.0
            
            async def safe_extract_tables():
                try:
                    return await self.extract_tables()
                except Exception as e:
                    log_error(f"Table extraction failed: {str(e)}")
                    return [], 0.0
            
            async def safe_extract_text():
                try:
                    return await self.extract_text()
                except Exception as e:
                    log_error(f"Text extraction failed: {str(e)}")
                    return {}, 0.0
            
            tasks = [
                safe_extract_images(),
                safe_extract_tables(),
                safe_extract_text()
            ]
            
            extraction_results = await asyncio.gather(*tasks)
            
            results["images"] = extraction_results[0][0]
            results["tables"] = extraction_results[1][0]
            results["text"] = extraction_results[2][0]
            
            results["execution_times"]["image_extraction"] = extraction_results[0][1]
            results["execution_times"]["table_extraction"] = extraction_results[1][1]
            results["execution_times"]["text_extraction"] = extraction_results[2][1]
            
            await self.report_generator.generate_summary(results)
            
            log_success("PDF extraction completed")
            return results
            
        finally:
            self._close_document()
    
    def close(self):
        self._close_document()