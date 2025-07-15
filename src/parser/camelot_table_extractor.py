import camelot
import asyncio
import io
from pathlib import Path

class CamelotTableExtractor:
    def __init__(self, pdf_path: str, output_dir: Path):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.tables_dir = output_dir / "tables"
        self.tables_dir.mkdir(exist_ok=True)
        self.min_rows = 2
        self.min_cols = 2

    def _is_empty_table(self, df):
        cleaned_df = df.astype(str).replace('', None).replace(' ', None)
        return cleaned_df.isnull().all().all()

    def _extract_tables_sync(self):
        tables_data = []
        
        try:
            with open(self.pdf_path, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
            
            pdf_stream = io.BytesIO(pdf_data)
            
            tables = camelot.read_pdf(
                pdf_stream,
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
                        if not self._is_empty_table(table.df):
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
            pass
            
        return tables_data

    async def extract(self):
        return await asyncio.to_thread(self._extract_tables_sync)