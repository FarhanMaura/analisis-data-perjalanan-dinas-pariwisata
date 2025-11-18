import os
import logging
from datetime import datetime
from functools import wraps
import json

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('tourism_analysis.log'),
            logging.StreamHandler()
        ]
    )

def format_number(num):
    """Format number dengan separator"""
    try:
        return f"{int(num):,}"
    except (ValueError, TypeError):
        return "0"

def calculate_percentage_change(old_value, new_value):
    """Hitung persentase perubahan"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

def get_month_name(month_number):
    """Dapatkan nama bulan dari angka"""
    months = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    return months.get(month_number, 'Unknown')

def get_current_season():
    """Dapatkan musim current berdasarkan bulan"""
    current_month = datetime.now().month
    seasons = {
        'High': [6, 7, 8, 12, 1],  # Juni, Juli, Agustus, Desember, Januari
        'Medium': [2, 3, 9, 10, 11],  # Februari, Maret, September, Oktober, November
        'Low': [4, 5]  # April, Mei
    }
    
    for season, months in seasons.items():
        if current_month in months:
            return season
    
    return 'Unknown'

def validate_year(year):
    """Validasi tahun"""
    try:
        year_int = int(year)
        current_year = datetime.now().year
        return 2000 <= year_int <= current_year + 1
    except (ValueError, TypeError):
        return False

def create_response(success=True, message="", data=None, error_code=None):
    """Buat response standar"""
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if error_code is not None:
        response['error_code'] = error_code
    
    return response

def save_backup(data, backup_type='analysis'):
    """Simpan backup data"""
    try:
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{backup_type}_backup_{timestamp}.json"
        filepath = os.path.join(backup_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True, filename
    except Exception as e:
        return False, str(e)

def load_latest_backup(backup_type='analysis'):
    """Load backup terbaru"""
    try:
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            return None
        
        backup_files = [f for f in os.listdir(backup_dir) 
                       if f.startswith(f"{backup_type}_backup_") and f.endswith('.json')]
        
        if not backup_files:
            return None
        
        latest_file = sorted(backup_files)[-1]
        filepath = os.path.join(backup_dir, latest_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    except Exception:
        return None

class PerformanceTimer:
    """Class untuk mengukur performance"""
    def __init__(self, operation_name=""):
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            logging.info(f"Operation '{self.operation_name}' completed in {duration:.2f} seconds")