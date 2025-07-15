import fitz


class PDFTypeDetector:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
    
    def is_scanned_pdf(self) -> dict:
        confidence = self.get_confidence_score()
        return {
            "is_scanned": confidence > 0.7,
            "confidence": confidence
        }
    
    def get_confidence_score(self) -> float:
        try:
            doc = fitz.open(self.pdf_path)
            pages_to_check = min(2, len(doc))
            total_confidence = 0
            
            for page_num in range(pages_to_check):
                page = doc[page_num]
                page_confidence = 0
                
                text = page.get_text()
                if not text.strip():
                    page_confidence = 0.95
                else:
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
                    
                    page_width = page.rect.width
                    page_height = page.rect.height
                    page_area = page_width * page_height
                    
                    text_density = text_area / page_area if page_area > 0 else 0
                    image_coverage = image_area / page_area if page_area > 0 else 0
                    
                    text_confidence = max(0, 1 - (text_density * 10))
                    image_confidence = min(1, image_coverage * 2)
                    
                    image_to_text_ratio = image_area / text_area if text_area > 0 else 10
                    ratio_confidence = min(1, image_to_text_ratio / 5)
                    
                    page_confidence = (text_confidence * 0.3 + image_confidence * 0.4 + ratio_confidence * 0.3)
                
                total_confidence += page_confidence
            
            doc.close()
            return total_confidence / pages_to_check
            
        except Exception:
            return 0.9