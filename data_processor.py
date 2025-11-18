import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime
import re

class DataProcessor:
    def __init__(self, db_path='tourism.db'):
        self.db_path = db_path
    
    def validate_csv_structure(self, filepath):
        """Validasi struktur file CSV - DIPERBAIKI"""
        try:
            # Coba baca CSV dengan berbagai cara
            df = None
            
            # Coba baca dengan multi-header
            try:
                df = pd.read_csv(filepath, header=[0,1,2])
            except:
                # Jika gagal, coba baca dengan header biasa
                try:
                    df = pd.read_csv(filepath)
                except Exception as e:
                    return False, f"Tidak bisa membaca file CSV: {str(e)}"
            
            if df is None or df.empty:
                return False, "File CSV kosong atau tidak bisa dibaca"
            
            # Validasi header bulan - DIPERBAIKI
            expected_months = ['January', 'February', 'March', 'April', 'May', 'June',
                             'July', 'August', 'September', 'October', 'November', 'December']
            
            # Cek apakah ada data Palembang
            palembang_found = False
            for index, row in df.iterrows():
                # Cek di semua kolom pertama untuk string "Palembang"
                first_col_value = str(row.iloc[0]) if len(row) > 0 else ""
                if 'Palembang' in first_col_value:
                    palembang_found = True
                    break
            
            if not palembang_found:
                return False, "Data untuk Palembang tidak ditemukan dalam file CSV"
            
            # Cek struktur kolom bulan - lebih fleksibel
            month_columns_found = 0
            for col in df.columns:
                col_str = str(col).lower()
                for month in expected_months:
                    if month.lower() in col_str:
                        month_columns_found += 1
                        break
            
            if month_columns_found >= 10:  # Minimal 10 bulan terdeteksi
                return True, "Struktur CSV valid"
            else:
                return False, f"Hanya {month_columns_found} bulan yang terdeteksi. Pastikan ada kolom Jan-Des"
            
        except Exception as e:
            return False, f"Error validasi CSV: {str(e)}"
    
    def extract_year_from_filename(self, filename):
        """Extract tahun dari filename"""
        try:
            # Pattern: tourism_2023_20231125_143022.csv
            match = re.search(r'tourism_(\d{4})_', filename)
            if match:
                return int(match.group(1))
            
            # Pattern lain: 2023_data.csv, data_2023.csv, dll
            matches = re.findall(r'\b(20\d{2})\b', filename)
            if matches:
                return int(matches[0])
                
            return None
        except:
            return None
    
    def clean_numeric_value(self, value):
        """Bersihkan nilai numerik dari string"""
        if pd.isna(value) or value == '':
            return 0
        
        if isinstance(value, (int, float)):
            return int(value)
        
        if isinstance(value, str):
            # Hapus karakter non-numeric
            cleaned = re.sub(r'[^\d]', '', str(value))
            return int(cleaned) if cleaned else 0
        
        return 0
    
    def process_csv_data(self, filepath, year):
        """Process data CSV dan simpan ke database - DIPERBAIKI"""
        try:
            # Coba baca dengan multi-header, jika gagal coba header biasa
            try:
                df = pd.read_csv(filepath, header=[0,1,2])
            except:
                df = pd.read_csv(filepath)
            
            # Cari baris Palembang
            palembang_data = None
            palembang_index = -1
            
            for index, row in df.iterrows():
                first_col_value = str(row.iloc[0]) if len(row) > 0 else ""
                if 'Palembang' in first_col_value:
                    palembang_data = row
                    palembang_index = index
                    break
            
            if palembang_data is None:
                return False, "Data Palembang tidak ditemukan"
            
            # Extract data bulanan - DIPERBAIKI untuk handle berbagai format
            months = ['January', 'February', 'March', 'April', 'May', 'June', 
                     'July', 'August', 'September', 'October', 'November', 'December']
            
            monthly_data = {}
            
            for i, month in enumerate(months):
                # Cari kolom yang mengandung nama bulan
                col_index = -1
                for j, col in enumerate(df.columns):
                    col_str = str(col).lower()
                    if month.lower() in col_str:
                        col_index = j
                        break
                
                if col_index != -1 and col_index < len(palembang_data):
                    value = palembang_data.iloc[col_index]
                    cleaned_value = self.clean_numeric_value(value)
                    monthly_data[month] = cleaned_value
                else:
                    monthly_data[month] = 0  # Default value jika kolom tidak ditemukan
            
            # Simpan ke database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Hapus data existing untuk tahun yang sama
            cursor.execute('DELETE FROM tourism_data WHERE year = ?', (year,))
            
            # Insert data baru
            for month, value in monthly_data.items():
                cursor.execute(
                    'INSERT INTO tourism_data (year, month, value) VALUES (?, ?, ?)',
                    (year, month, value)
                )
            
            conn.commit()
            conn.close()
            
            total_visitors = sum(monthly_data.values())
            return True, f"Data Palembang tahun {year} berhasil diproses. Total visitors: {total_visitors:,}"
            
        except Exception as e:
            return False, f"Error processing CSV: {str(e)}"
    
    def get_uploaded_files_info(self):
        """Dapatkan informasi file yang sudah diupload"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT filename, year, upload_date 
            FROM uploaded_files 
            ORDER BY upload_date DESC
        ''')
        
        files = cursor.fetchall()
        conn.close()
        
        result = []
        for file in files:
            result.append({
                'filename': file[0],
                'year': file[1],
                'upload_date': file[2]
            })
        
        return result
    
    def get_database_stats(self):
        """Dapatkan statistik database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total records
        cursor.execute('SELECT COUNT(*) FROM tourism_data')
        total_records = cursor.fetchone()[0]
        
        # Years available
        cursor.execute('SELECT DISTINCT year FROM tourism_data ORDER BY year')
        years = [row[0] for row in cursor.fetchall()]
        
        # Total files uploaded
        cursor.execute('SELECT COUNT(*) FROM uploaded_files')
        total_files = cursor.fetchone()[0]
        
        # Latest update
        cursor.execute('SELECT MAX(upload_date) FROM uploaded_files')
        latest_update = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_records': total_records,
            'years_available': years,
            'total_files': total_files,
            'latest_update': latest_update,
            'data_available': total_records > 0
        }
    
    def export_analysis_data(self, format='json'):
        """Export data untuk analisis external"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT year, month, value 
            FROM tourism_data 
            ORDER BY year, 
            CASE month
                WHEN 'January' THEN 1
                WHEN 'February' THEN 2
                WHEN 'March' THEN 3
                WHEN 'April' THEN 4
                WHEN 'May' THEN 5
                WHEN 'June' THEN 6
                WHEN 'July' THEN 7
                WHEN 'August' THEN 8
                WHEN 'September' THEN 9
                WHEN 'October' THEN 10
                WHEN 'November' THEN 11
                WHEN 'December' THEN 12
            END
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if format == 'json':
            return df.to_json(orient='records', indent=2)
        elif format == 'csv':
            return df.to_csv(index=False)
        else:
            return df.to_dict(orient='records')