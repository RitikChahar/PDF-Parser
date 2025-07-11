import camelot
import os
import asyncio
import tempfile
import shutil
from pathlib import Path

class TableExtractor:
    def __init__(self, pdf_path: str, output_dir: Path):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.tables_dir = output_dir / "tables"
        self.tables_dir.mkdir(exist_ok=True)
        self.min_rows = 2
        self.min_cols = 2

    def _extract_tables_sync(self):
        tables_data = []
        temp_dir = tempfile.mkdtemp()
        
        try:
            temp_pdf_path = os.path.join(temp_dir, "temp.pdf")
            shutil.copy2(self.pdf_path, temp_pdf_path)

            try:
                tables = camelot.read_pdf(
                    temp_pdf_path,
                    pages='all',
                    flavor='lattice',
                    line_scale=30,
                    split_text=False,
                    flag_size=False,
                    strip_text='\n'
                )
                for i, table in enumerate(tables):
                    if table.df is not None and not table.df.empty:
                        if len(table.df) >= self.min_rows and len(table.df.columns) >= self.min_cols:
                            table_filename = f"table_{i + 1}_lattice.csv"
                            table_path = self.tables_dir / table_filename
                            table.to_csv(str(table_path))
                            tables_data.append({
                                "table_index": i + 1,
                                "page": table.page,
                                "csv_path": str(table_path),
                                "rows": len(table.df),
                                "columns": len(table.df.columns),
                                "extraction_method": "lattice"
                            })
            except Exception:
                tables_data = []

            if not tables_data:
                try:
                    tables = camelot.read_pdf(
                        temp_pdf_path,
                        pages='all',
                        flavor='stream',
                        edge_tol=50,
                        row_tol=5,
                        split_text=False,
                        strip_text='\n'
                    )
                    for i, table in enumerate(tables):
                        if table.df is not None and not table.df.empty:
                            if len(table.df) >= self.min_rows and len(table.df.columns) >= self.min_cols:
                                table_filename = f"table_{i + 1}_stream.csv"
                                table_path = self.tables_dir / table_filename
                                table.to_csv(str(table_path))
                                tables_data.append({
                                    "table_index": i + 1,
                                    "page": table.page,
                                    "csv_path": str(table_path),
                                    "rows": len(table.df),
                                    "columns": len(table.df.columns),
                                    "extraction_method": "stream"
                                })
                except Exception:
                    pass
                    
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            
        return tables_data

    async def extract(self):
        return await asyncio.to_thread(self._extract_tables_sync)