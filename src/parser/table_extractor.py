import asyncio
from pathlib import Path
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Table, TableChunk
import pandas as pd

class TableExtractor:
    def __init__(self, pdf_path: str, output_dir: Path):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.tables_dir = output_dir / "tables"
        self.tables_dir.mkdir(exist_ok=True)
        self.min_rows = 2
        self.min_cols = 2
    
    def _extract_tables_sync(self):
        elements = partition_pdf(
            filename=self.pdf_path,
            infer_table_structure=True,
            extract_images_in_pdf=True,
            hi_res_model_name="yolox"
        )
        
        tables_data = []
        table_counter = 0
        
        for element in elements:
            if isinstance(element, (Table, TableChunk)):
                try:
                    table_text = str(element)
                    if not table_text.strip():
                        continue
                    
                    if hasattr(element, 'metadata') and hasattr(element.metadata, 'text_as_html') and element.metadata.text_as_html:
                        html_content = element.metadata.text_as_html
                        try:
                            df = pd.read_html(html_content)[0]
                        except:
                            df = self._parse_table_text(table_text)
                    else:
                        df = self._parse_table_text(table_text)
                    
                    if len(df) >= self.min_rows and len(df.columns) >= self.min_cols:
                        table_counter += 1
                        page_num = getattr(element.metadata, 'page_number', 1) if hasattr(element, 'metadata') else 1
                        
                        table_filename = f"table_{table_counter}_page_{page_num}.csv"
                        table_path = self.tables_dir / table_filename
                        df.to_csv(str(table_path), index=False)
                        
                        tables_data.append({
                            "table_index": table_counter,
                            "page": page_num,
                            "csv_path": str(table_path),
                            "rows": len(df),
                            "columns": len(df.columns),
                            "extraction_method": "unstructured"
                        })
                except Exception:
                    continue
        
        return tables_data
    
    def _parse_table_text(self, table_text):
        lines = table_text.split('\n')
        data = []
        for line in lines:
            if line.strip():
                row = [cell.strip() for cell in line.split() if cell.strip()]
                if row:
                    data.append(row)
        
        if not data:
            return pd.DataFrame()
        
        max_cols = max(len(row) for row in data)
        for row in data:
            while len(row) < max_cols:
                row.append('')
        
        return pd.DataFrame(data)
    
    async def extract(self):
        return await asyncio.to_thread(self._extract_tables_sync)