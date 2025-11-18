from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime
import json

# Import custom modules
from ml_analysis import TourismAnalyzer
from data_processor import DataProcessor
from chart_generator import ChartGenerator
from utils import setup_logging, create_response, validate_year
from config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['DATABASE'] = Config.DATABASE
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Initialize modules
data_processor = DataProcessor(Config.DATABASE)
ml_analyzer = TourismAnalyzer(Config.DATABASE)
chart_generator = ChartGenerator()

# Setup logging
setup_logging()

# Buat folder uploads jika belum ada
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tourism_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            month TEXT,
            value INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploaded_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            year INTEGER,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def process_csv_file_simple(filepath, year):
    """Process CSV file dengan approach SANGAT SEDERHANA"""
    try:
        # Baca CSV biasa
        df = pd.read_csv(filepath)
        print(f"DEBUG: File shape: {df.shape}")
        print(f"DEBUG: Columns: {list(df.columns)}")
        
        # Cari baris Palembang
        palembang_data = None
        for index, row in df.iterrows():
            for i, cell in enumerate(row):
                if 'Palembang' in str(cell):
                    palembang_data = row
                    print(f"DEBUG: Found Palembang at index {index}")
                    break
            if palembang_data is not None:
                break
        
        if palembang_data is None:
            return False, "Data Palembang tidak ditemukan"
        
        # Extract data bulanan - ambil 12 kolom setelah kolom pertama
        months = ['January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        monthly_data = {}
        
        # Ambil 12 nilai setelah kolom pertama (asumsi urutan bulan)
        for i, month in enumerate(months):
            if i + 1 < len(palembang_data):  # +1 karena kolom 0 adalah nama daerah
                value = palembang_data.iloc[i + 1]
                try:
                    value_int = int(value) if pd.notna(value) else 0
                except (ValueError, TypeError):
                    value_int = 0
                monthly_data[month] = value_int
                print(f"DEBUG: {month}: {value_int}")
            else:
                monthly_data[month] = 0
        
        # Simpan ke database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Hapus data tahun yang sama jika sudah ada
        cursor.execute('DELETE FROM tourism_data WHERE year = ?', (year,))
        
        # Simpan data bulanan
        for month, value in monthly_data.items():
            cursor.execute(
                'INSERT INTO tourism_data (year, month, value) VALUES (?, ?, ?)',
                (year, month, value)
            )
        
        conn.commit()
        conn.close()
        
        total = sum(monthly_data.values())
        return True, f"Data berhasil diproses. Total pengunjung: {total:,}"
        
    except Exception as e:
        return False, f"Error processing CSV: {str(e)}"

def analyze_data():
    """Analyze data and generate insights"""
    conn = get_db_connection()
    
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
    
    if df.empty:
        return {
            'monthly_data': [],
            'yearly_data': [],
            'suggestions': ["Belum ada data untuk dianalisis"],
            'charts_data': {
                'monthly_labels': [],
                'monthly_values': [],
                'yearly_labels': [], 
                'yearly_values': []
            }
        }
    
    # Data untuk chart
    monthly_data = []
    yearly_data = []
    
    # Group by year untuk data tahunan
    yearly_stats = df.groupby('year')['value'].sum().reset_index()
    for _, row in yearly_stats.iterrows():
        yearly_data.append({
            'year': int(row['year']),
            'total': int(row['value'])
        })
    
    # Data bulanan untuk chart
    months_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    for month in months_order:
        month_data = df[df['month'] == month]
        if not month_data.empty:
            avg_value = month_data['value'].mean()
            monthly_data.append({
                'month': month,
                'average': int(avg_value)
            })
    
    # Analisis sederhana
    suggestions = generate_suggestions(df)
    
    # Data untuk chart
    charts_data = {
        'monthly_labels': [d['month'] for d in monthly_data],
        'monthly_values': [d['average'] for d in monthly_data],
        'yearly_labels': [str(d['year']) for d in yearly_data],
        'yearly_values': [d['total'] for d in yearly_data]
    }
    
    return {
        'monthly_data': monthly_data,
        'yearly_data': yearly_data,
        'suggestions': suggestions,
        'charts_data': charts_data
    }

def generate_suggestions(df):
    """Generate suggestions using simple analysis"""
    suggestions = []
    
    if len(df['year'].unique()) < 2:
        suggestions.append("Data masih terbatas. Upload lebih banyak data tahun untuk analisis yang lebih akurat.")
        return suggestions
    
    # Analisis trend tahunan
    yearly_totals = df.groupby('year')['value'].sum()
    years = sorted(yearly_totals.index)
    
    if len(years) >= 2:
        current_year = years[-1]
        prev_year = years[-2]
        current_total = yearly_totals[current_year]
        prev_total = yearly_totals[prev_year]
        
        growth_rate = ((current_total - prev_total) / prev_total) * 100
        
        if growth_rate < -10:
            suggestions.append(f"⚠️ Penurunan signifikan ({growth_rate:.1f}%) dari tahun {prev_year} ke {current_year}.")
        elif growth_rate < 0:
            suggestions.append(f"📉 Penurunan ({growth_rate:.1f}%) dari tahun sebelumnya.")
        elif growth_rate > 20:
            suggestions.append(f"🚀 Pertumbuhan excellent ({growth_rate:.1f}%)!")
        elif growth_rate > 0:
            suggestions.append(f"📈 Pertumbuhan positif ({growth_rate:.1f}%).")
        else:
            suggestions.append("➡️ Pertumbuhan stagnan.")
    
    # Analisis bulanan
    monthly_avg = df.groupby('month')['value'].mean()
    high_season = monthly_avg.nlargest(3)
    low_season = monthly_avg.nsmallest(3)
    
    if not high_season.empty:
        suggestions.append(f"🎯 High season: {', '.join(high_season.index)}")
    
    if not low_season.empty:
        suggestions.append(f"💡 Low season: {', '.join(low_season.index)}")
    
    return suggestions

@app.route('/')
def homepage():
    """Homepage"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload CSV file - VALIDASI SEDERHANA"""
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('Tidak ada file yang dipilih', 'error')
            return redirect(request.url)
        
        file = request.files['csv_file']
        year = request.form.get('year')
        
        if file.filename == '':
            flash('Tidak ada file yang dipilih', 'error')
            return redirect(request.url)
        
        if not year:
            flash('Tahun harus diisi', 'error')
            return redirect(request.url)
        
        if file.filename and not file.filename.lower().endswith('.csv'):
            flash('File harus berformat CSV', 'error')
            return redirect(request.url)
        
        if not validate_year(year):
            flash('Tahun harus antara 2000 dan tahun depan', 'error')
            return redirect(request.url)
        
        try:
            year = int(year)
        except ValueError:
            flash('Tahun harus berupa angka', 'error')
            return redirect(request.url)
        
        # Simpan file
        filename = f"tourism_{year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # VALIDASI SEDERHANA: Cek hanya apakah file bisa dibaca dan ada Palembang
        try:
            df = pd.read_csv(filepath)
            palembang_found = False
            for index, row in df.iterrows():
                for cell in row:
                    if 'Palembang' in str(cell):
                        palembang_found = True
                        break
                if palembang_found:
                    break
            
            if not palembang_found:
                os.remove(filepath)
                flash('Data Palembang tidak ditemukan dalam file', 'error')
                return redirect(request.url)
                
        except Exception as e:
            os.remove(filepath)
            flash(f'File tidak bisa dibaca: {str(e)}', 'error')
            return redirect(request.url)
        
        # Proses file CSV dengan fungsi simple
        success, message = process_csv_file_simple(filepath, year)
        
        if success:
            # Simpan info file ke database
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO uploaded_files (filename, year) VALUES (?, ?)',
                (filename, year)
            )
            conn.commit()
            conn.close()
            
            flash(f'File berhasil diupload: {message}', 'success')
        else:
            flash(f'Error: {message}', 'error')
            if os.path.exists(filepath):
                os.remove(filepath)
        
        return redirect(url_for('upload'))
    
    # GET request
    db_stats = data_processor.get_database_stats()
    uploaded_files = data_processor.get_uploaded_files_info()
    
    return render_template('upload.html', 
                         db_stats=db_stats, 
                         uploaded_files=uploaded_files)

@app.route('/dashboard')
def dashboard():
    """Dashboard dengan analisis data"""
    conn = get_db_connection()
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
    
    analysis_results = analyze_data()
    
    try:
        ml_analysis = ml_analyzer.get_detailed_analysis()
    except Exception as e:
        ml_analysis = {
            'suggestions': ["ML Analysis sedang dalam perbaikan"],
            'seasonal_patterns': {},
            'clustering_info': {},
            'trend_analysis': {},
            'anomalies': []
        }
    
    try:
        charts_data_advanced = chart_generator.generate_all_charts_data(df)
    except Exception as e:
        charts_data_advanced = {}
    
    db_stats = data_processor.get_database_stats()
    
    return render_template('dashboard.html',
                         **analysis_results,
                         ml_analysis=ml_analysis,
                         charts_data_advanced=charts_data_advanced,
                         db_stats=db_stats,
                         df_empty=df.empty)

@app.route('/delete-data', methods=['POST'])
def delete_data():
    """Hapus semua data"""
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM tourism_data')
        conn.execute('DELETE FROM uploaded_files')
        conn.commit()
        conn.close()
        
        # Hapus file upload
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        
        flash('Semua data berhasil dihapus', 'success')
    except Exception as e:
        flash(f'Error menghapus data: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/api/chart-data')
def chart_data():
    """API untuk data chart"""
    analysis_results = analyze_data()
    return jsonify(analysis_results['charts_data'])

@app.route('/api/advanced-chart-data')
def advanced_chart_data():
    """API untuk data chart advanced"""
    conn = get_db_connection()
    query = 'SELECT year, month, value FROM tourism_data'
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    try:
        charts_data = chart_generator.generate_all_charts_data(df)
        return jsonify(charts_data)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/analysis-data')
def analysis_data():
    """API untuk data analisis ML"""
    try:
        analysis_results = ml_analyzer.get_detailed_analysis()
        return jsonify(analysis_results)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/db-stats')
def db_stats_api():
    """API untuk statistik database"""
    stats = data_processor.get_database_stats()
    return jsonify(stats)

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash('File terlalu besar. Maksimal 16MB', 'error')
    return redirect(url_for('upload'))

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server error"""
    flash('Terjadi error internal server. Silakan coba lagi.', 'error')
    return redirect(url_for('homepage'))

@app.errorhandler(404)
def not_found(error):
    """Handle page not found"""
    return render_template('404.html'), 404

if __name__ == '__main__':
    init_db()
    print("=== Tourism Data Management System ===")
    print("Server running on: http://127.0.0.1:5000")
    print("Routes available:")
    print("  /              - Homepage")
    print("  /upload        - Upload CSV data")
    print("  /dashboard     - Analytics dashboard")
    print("  /api/*         - Various API endpoints")
    app.run(debug=True, host='127.0.0.1', port=5000)