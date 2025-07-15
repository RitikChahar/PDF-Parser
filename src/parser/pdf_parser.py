import fitz
from pathlib import Path
from typing import Dict
from utils.logutils import log_info, log_success, log_error

from .image_extractor import ImageExtractor
from .camelot_table_extractor import CamelotTableExtractor
from .docling_table_extractor import DoclingTableExtractor
from .text_extractor import TextExtractor


class PDFParser:
    def __init__(self, pdf_path: str, output_dir: str = "pdf_output"):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.doc = None
    
    def is_scanned_pdf(self) -> bool:
        try:
            doc = fitz.open(self.pdf_path)
            pages_to_check = min(2, len(doc))
            
            for page_num in range(pages_to_check):
                page = doc[page_num]
                
                text = page.get_text()
                if not text.strip():
                    doc.close()
                    return True
                
                text_area = 0
                text_blocks = page.get_text("dict")["blocks"]
                for block in text_blocks:
                    if "lines" in block:
                        bbox = block["bbox"]
                        text_area += (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                
                image_area = 0
                images = page.get_images()
                for img in images:
                    img_rect = page.get_image_bbox(img)
                    image_area += img_rect.width * img_rect.height
                
                if text_area > 0:
                    image_to_text_ratio = image_area / text_area
                    if image_to_text_ratio > 5:
                        doc.close()
                        return True
            
            doc.close()
            return False
            
        except Exception:
            return True
    
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
                is_scanned = self.is_scanned_pdf()
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