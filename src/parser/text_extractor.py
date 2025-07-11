import asyncio
import aiofiles
from pathlib import Path
from typing import Dict, List


class TextExtractor:
    def __init__(self, doc, output_dir: Path):
        self.doc = doc
        self.output_dir = output_dir
        self.text_dir = output_dir / "text"
        self.text_dir.mkdir(exist_ok=True)
    
    async def _save_text(self, text: str, file_path: Path) -> None:
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(text)
    
    def _extract_column_text(self, page):
        page_dict = page.get_text("dict")
        page_width = page.rect.width
        text_blocks = []
        
        for block in page_dict.get("blocks", []):
            if "lines" not in block:
                continue
                
            bbox = block["bbox"]
            block_text = ""
            for line in block["lines"]:
                for span in line["spans"]:
                    block_text += span["text"]
            
            if block_text.strip():
                text_blocks.append({
                    "x0": bbox[0],
                    "y0": bbox[1],
                    "text": block_text.strip()
                })
        
        if not text_blocks:
            return "", ""
        
        text_blocks.sort(key=lambda b: (b["x0"], b["y0"]))
        
        tolerance = page_width * 0.05
        columns = []
        current_column = []
        
        for block in text_blocks:
            if not current_column:
                current_column.append(block)
                continue
                
            last_block = current_column[-1]
            gap = block["x0"] - last_block["x0"]
            if gap <= tolerance:
                current_column.append(block)
            else:
                columns.append(current_column)
                current_column = [block]
        
        if current_column:
            columns.append(current_column)
        
        columns.sort(key=lambda col: min(b["x0"] for b in col))
        
        layout_lines = []
        continuous_lines = []
        
        for idx, column in enumerate(columns):
            column.sort(key=lambda b: b["y0"])
            layout_lines.append(f"=== Column {idx + 1} ===")
            col_texts = [b["text"] for b in column]
            layout_lines.extend(col_texts)
            layout_lines.append("")
            continuous_lines.extend(col_texts)
        
        return "\n".join(layout_lines), " ".join(continuous_lines)
    
    async def extract(self) -> Dict:
        text_data = {
            "pages": [],
            "total_pages": len(self.doc)
        }
        
        layout_preserved_path = self.text_dir / "layout_preserved.txt"
        continuous_text_path = self.text_dir / "continuous_text.txt"
        
        all_layout_parts = []
        all_continuous_parts = []
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            layout_text, continuous_text = self._extract_column_text(page)
            
            all_layout_parts.append(f"--- Page {page_num + 1} ---\n{layout_text}\n")
            all_continuous_parts.append(continuous_text)
            
            text_data["pages"].append({
                "page_number": page_num + 1,
                "char_count": len(continuous_text)
            })
        
        full_layout_text = "\n".join(all_layout_parts)
        full_continuous_text = " ".join(all_continuous_parts)
        
        await self._save_text(full_layout_text, layout_preserved_path)
        await self._save_text(full_continuous_text, continuous_text_path)
        
        text_data["layout_preserved_path"] = str(layout_preserved_path)
        text_data["continuous_text_path"] = str(continuous_text_path)
        
        return text_data