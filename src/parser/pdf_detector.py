import fitz


class PDFTypeDetector:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
    
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