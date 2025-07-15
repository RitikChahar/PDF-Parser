import fitz
from pathlib import Path
from typing import Dict
from utils.logutils import log_info, log_success, log_error

from .image_extractor import ImageExtractor
from .camelot_table_extractor import CamelotTableExtractor
from .docling_table_extractor import DoclingTableExtractor
from .text_extractor import TextExtractor
from .pdf_detector import PDFTypeDetector


class PDFParser:
    def __init__(self, pdf_path: str, output_dir: str = "pdf_output"):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.doc = None
        self.detector = PDFTypeDetector(pdf_path)
    
    async def extract_all(self) -> Dict:
        log_info("Starting PDF extraction")
        
        try:
            self.doc = fitz.open(self.pdf_path)
            
            results = {
                "pdf_path": self.pdf_path,
                "output_directory": str(self.output_dir),
                "images": [],
                "tables": [],
                "text": {}
            }
            
            try:
                image_extractor = ImageExtractor(self.doc, self.output_dir)
                results["images"] = await image_extractor.extract()
            except Exception as e:
                log_error(f"Image extraction failed: {str(e)}")
            
            try:
                is_scanned = self.detector.is_scanned_pdf()
                if is_scanned:
                    table_extractor = DoclingTableExtractor(self.pdf_path, self.output_dir)
                else:
                    table_extractor = CamelotTableExtractor(self.pdf_path, self.output_dir)
                results["tables"] = await table_extractor.extract()
            except Exception as e:
                log_error(f"Table extraction failed: {str(e)}")
            
            try:
                text_extractor = TextExtractor(self.doc, self.output_dir)
                results["text"] = await text_extractor.extract()
            except Exception as e:
                log_error(f"Text extraction failed: {str(e)}")
            
            log_success("PDF extraction completed")
            return results
            
        finally:
            if self.doc:
                self.doc.close()