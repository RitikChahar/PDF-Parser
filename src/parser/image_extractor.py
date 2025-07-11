import asyncio
import aiofiles
from pathlib import Path
from typing import List, Dict


class ImageExtractor:
    def __init__(self, doc, output_dir: Path):
        self.doc = doc
        self.output_dir = output_dir
        self.images_dir = output_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
    
    async def _save_image(self, img_data: bytes, img_path: Path) -> None:
        async with aiofiles.open(img_path, "wb") as img_file:
            await img_file.write(img_data)
    
    async def extract(self) -> List[Dict]:
        images_data = []
        save_tasks = []
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = self.doc.extract_image(xref)
                img_data = base_image["image"]
                
                if base_image["width"] < 50 or base_image["height"] < 50:
                    continue
                
                img_filename = f"page_{page_num + 1}_img_{img_index + 1}.{base_image['ext']}"
                img_path = self.images_dir / img_filename
                
                save_tasks.append(self._save_image(img_data, img_path))
                
                images_data.append({
                    "page": page_num + 1,
                    "image_index": img_index + 1,
                    "filename": img_filename,
                    "path": str(img_path),
                    "width": base_image["width"],
                    "height": base_image["height"]
                })
        
        if save_tasks:
            await asyncio.gather(*save_tasks)
        
        return images_data