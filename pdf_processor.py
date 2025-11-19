import pandas as pd
import pdfplumber
import re
import os
from datetime import datetime
import sqlite3

class PDFProcessor:
    def __init__(self):
        self.month_mapping = {
            'januari': 'January', 'februari': 'February', 'maret': 'March',
            'april': 'April', 'mei': 'May', 'juni': 'June',
            'juli': 'July', 'agustus': 'August', 'september': 'September',
            'oktober': 'October', 'november': 'November', 'desember': 'December'
        }
    
    def extract_year_from_pdf(self, text):
        year_pattern = r'TAHUN\s+(\d{4})'
        match = re.search(year_pattern, text)
        if match:
            return int(match.group(1))
        
        year_patterns = [
            r'Tahun\s+(\d{4})',
            r'(\d{4})',
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return int(matches[0])
        
        return datetime.now().year
    
    def clean_numeric_value(self, value):
        if pd.isna(value) or value == '':
            return 0
        
        if isinstance(value, (int, float)):
            return int(value)
        
        if isinstance(value, str):
            cleaned = re.sub(r'[^\d]', '', str(value).replace('.', ''))
            return int(cleaned) if cleaned else 0
        
        return 0
    
    def extract_table_data(self, pdf_path):
        all_data = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                year = self.extract_year_from_pdf(text)
                
                tables = page.extract_tables()
                for table in tables:
                    processed_data = self.process_table(table, year, text)
                    if processed_data:
                        all_data.extend(processed_data)
        
        return all_data
    
    def process_table(self, table, year, page_text):
        data_rows = []
        
        header_found = False
        nusantara_col = -1
        manca_col = -1
        total_col = -1
        bulan_col = -1
        
        for i, row in enumerate(table):
            if not row or all(cell is None or cell == '' for cell in row):
                continue
            
            row_text = ' '.join([str(cell) for cell in row if cell])
            if any(keyword in row_text.lower() for keyword in ['bulan', 'nusantara', 'manca', 'jumlah']):
                header_found = True
                for j, cell in enumerate(row):
                    if cell:
                        cell_lower = str(cell).lower()
                        if 'bulan' in cell_lower:
                            bulan_col = j
                        elif 'nusantara' in cell_lower:
                            nusantara_col = j
                        elif 'manca' in cell_lower:
                            manca_col = j
                        elif 'jumlah' in cell_lower and 'total' not in cell_lower:
                            total_col = j
                continue
            
            if header_found and row[0] and any(str(cell).strip() for cell in row if cell):
                bulan = None
                nusantara = 0
                manca = 0
                total = 0
                
                for j, cell in enumerate(row):
                    if cell and str(cell).strip():
                        cell_lower = str(cell).strip().lower()
                        if cell_lower in self.month_mapping:
                            bulan = self.month_mapping[cell_lower]
                            break
                
                if not bulan:
                    continue
                
                if nusantara_col != -1 and nusantara_col < len(row) and row[nusantara_col]:
                    nusantara = self.clean_numeric_value(row[nusantara_col])
                
                if manca_col != -1 and manca_col < len(row) and row[manca_col]:
                    manca = self.clean_numeric_value(row[manca_col])
                
                if total_col != -1 and total_col < len(row) and row[total_col]:
                    total = self.clean_numeric_value(row[total_col])
                else:
                    total = nusantara + manca
                
                data_rows.append({
                    'year': year,
                    'month': bulan,
                    'nusantara': nusantara,
                    'manca_negara': manca,
                    'total': total
                })
        
        return data_rows
    
    def pdf_to_csv(self, pdf_path, output_csv_path):
        try:
            data = self.extract_table_data(pdf_path)
            
            if not data:
                return False, "Tidak ada data yang berhasil diekstrak dari PDF"
            
            df = pd.DataFrame(data)
            df.to_csv(output_csv_path, index=False)
            
            return True, f"Berhasil konversi PDF ke CSV. {len(data)} records diproses."
            
        except Exception as e:
            return False, f"Error konversi PDF: {str(e)}"
    
    def process_pdf_for_database(self, pdf_path, year=None):
        try:
            data = self.extract_table_data(pdf_path)
            
            if not data:
                return False, "Tidak ada data yang berhasil diekstrak dari PDF"
            
            conn = sqlite3.connect('tourism.db')
            cursor = conn.cursor()
            
            for record in data:
                use_year = year if year else record['year']
                
                cursor.execute(
                    'DELETE FROM tourism_data WHERE year = ? AND month = ?',
                    (use_year, record['month'])
                )
                
                cursor.execute(
                    'INSERT INTO tourism_data (year, month, value) VALUES (?, ?, ?)',
                    (use_year, record['month'], record['total'])
                )
            
            conn.commit()
            conn.close()
            
            return True, f"Berhasil memproses PDF. {len(data)} records disimpan ke database."
            
        except Exception as e:
            return False, f"Error processing PDF: {str(e)}"