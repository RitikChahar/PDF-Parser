import asyncio
import aiofiles
from pathlib import Path
from typing import Dict
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Text, NarrativeText, Title, ListItem


class TextExtractor:
    def __init__(self, pdf_path: str, output_dir: Path):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.text_dir = output_dir / "text"
        self.text_dir.mkdir(exist_ok=True)
    
    async def _save_text(self, text: str, file_path: Path) -> None:
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(text)
    
    def _extract_continuous_text(self):
        elements = partition_pdf(
            filename=self.pdf_path
        )
        
        pages_data = {}
        continuous_parts = []
        
        for element in elements:
            if isinstance(element, (Text, NarrativeText, Title, ListItem)):
                text_content = str(element).strip()
                if text_content:
                    page_num = 1
                    if hasattr(element, 'metadata') and hasattr(element.metadata, 'page_number'):
                        page_num = element.metadata.page_number
                    
                    if page_num not in pages_data:
                        pages_data[page_num] = []
                    
                    pages_data[page_num].append(text_content)
        
        total_pages = max(pages_data.keys()) if pages_data else 0
        
        for page_num in sorted(pages_data.keys()):
            page_text = " ".join(pages_data[page_num])
            continuous_parts.append(page_text)
        
        return continuous_parts, total_pages, pages_data
    
    async def extract(self) -> Dict:
        continuous_parts, total_pages, pages_data = await asyncio.to_thread(self._extract_continuous_text)
        
        text_data = {
            "pages": [],
            "total_pages": total_pages
        }
        
        continuous_text_path = self.text_dir / "continuous_text.txt"
        
        for page_num in sorted(pages_data.keys()):
            page_text = " ".join(pages_data[page_num])
            text_data["pages"].append({
                "page_number": page_num,
                "char_count": len(page_text)
            })
        
        full_continuous_text = " ".join(continuous_parts)
        
        await self._save_text(full_continuous_text, continuous_text_path)
        
        text_data["continuous_text_path"] = str(continuous_text_path)
        
        return text_data