import asyncio
import aiofiles
import base64
from pathlib import Path
from typing import List, Dict
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Image

class ImageExtractor:
    def __init__(self, pdf_path: str, output_dir: Path):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.images_dir = output_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
    
    async def _save_image(self, img_data: bytes, img_path: Path) -> None:
        async with aiofiles.open(img_path, "wb") as img_file:
            await img_file.write(img_data)
    
    def _extract_images_sync(self):
        elements = partition_pdf(
            filename=self.pdf_path,
            extract_images_in_pdf=True,
            infer_table_structure=True,
            extract_image_block_types=["Image", "Table", "FigureCaption"]
        )
        
        images_data = []
        img_counter = 0
        
        for element in elements:
            if hasattr(element, 'metadata') and element.metadata:
                metadata = element.metadata
                if hasattr(metadata, 'image_base64') and metadata.image_base64:
                    try:
                        img_data = base64.b64decode(metadata.image_base64)
                        
                        if len(img_data) < 100:
                            continue
                        
                        img_counter += 1
                        page_num = getattr(metadata, 'page_number', 1)
                        
                        img_filename = f"page_{page_num}_img_{img_counter}.png"
                        img_path = self.images_dir / img_filename
                        
                        with open(img_path, 'wb') as f:
                            f.write(img_data)
                        
                        images_data.append({
                            "page": page_num,
                            "image_index": img_counter,
                            "filename": img_filename,
                            "path": str(img_path),
                            "width": getattr(metadata, 'image_width', 0),
                            "height": getattr(metadata, 'image_height', 0)
                        })
                    except Exception:
                        continue
        
        return images_data
    
    async def extract(self) -> List[Dict]:
        return await asyncio.to_thread(self._extract_images_sync)