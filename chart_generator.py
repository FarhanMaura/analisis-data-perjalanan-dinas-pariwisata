import pandas as pd
import numpy as np
import json
from datetime import datetime

class ChartGenerator:
    def __init__(self):
        self.color_scheme = {
            'primary': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'],
            'secondary': ['#FFA07A', '#20B2AA', '#778899', '#DEB887', '#98FB98', '#FFB6C1'],
            'pastel': ['#FFD1DC', '#C4E1FF', '#D1FFBD', '#FFF4BD', '#E1C4FF', '#FFD8C9']
        }
        self.months_order = ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December']
    
    def _convert_to_json_serializable(self, obj):
        """Convert numpy/pandas types to JSON serializable Python types"""
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        elif hasattr(obj, 'tolist'):  # Handle pandas Series and numpy arrays
            return [self._convert_to_json_serializable(x) for x in obj.tolist()]
        elif isinstance(obj, pd.DataFrame):
            return obj.astype(object).to_dict()
        elif isinstance(obj, dict):
            return {key: self._convert_to_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, (bool, str, type(None))):
            return obj
        else:
            return obj

    def generate_monthly_chart_data(self, df):
        """Generate data untuk chart bulanan - REAL DATA"""
        if df.empty:
            return self._get_empty_chart_data("Bulanan")
        
        monthly_avg = df.groupby('month')['value'].mean().reset_index()
        
        # Urutkan bulan
        monthly_avg['month'] = pd.Categorical(monthly_avg['month'], categories=self.months_order, ordered=True)
        monthly_avg = monthly_avg.sort_values('month')
        
        chart_data = {
            'type': 'bar',
            'data': {
                'labels': monthly_avg['month'].tolist(),
                'datasets': [{
                    'label': 'Rata-rata Pengunjung per Bulan',
                    'data': [int(x) for x in monthly_avg['value'].tolist()],
                    'backgroundColor': self.color_scheme['primary'],
                    'borderColor': '#2C3E50',
                    'borderWidth': 1
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Distribusi Pengunjung Wisata Palembang per Bulan'
                    },
                    'legend': {
                        'display': True
                    }
                }
            }
        }
        
        return self._convert_to_json_serializable(chart_data)
    
    def generate_yearly_chart_data(self, df):
        """Generate data untuk chart tahunan - REAL DATA"""
        if df.empty:
            return self._get_empty_chart_data("Tahunan")
        
        yearly_totals = df.groupby('year')['value'].sum().reset_index()
        yearly_totals = yearly_totals.sort_values('year')
        
        chart_data = {
            'type': 'line',
            'data': {
                'labels': [str(x) for x in yearly_totals['year'].tolist()],
                'datasets': [{
                    'label': 'Total Pengunjung per Tahun',
                    'data': [int(x) for x in yearly_totals['value'].tolist()],
                    'backgroundColor': 'rgba(78, 205, 196, 0.2)',
                    'borderColor': '#4ECDC4',
                    'borderWidth': 3,
                    'fill': True,
                    'tension': 0.4
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Trend Kunjungan Wisata Tahunan Palembang'
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True
                    }
                }
            }
        }
        
        return self._convert_to_json_serializable(chart_data)
    
    def generate_seasonal_pie_data(self, df):
        """Generate data untuk pie chart musiman - REAL DATA"""
        if df.empty:
            return self._get_empty_chart_data("Pie")
        
        seasonal_data = self._categorize_seasons(df)
        
        # Konversi ke format yang sesuai untuk chart
        labels = list(seasonal_data.keys())
        values = [int(x) for x in seasonal_data.values()]
        
        chart_data = {
            'type': 'pie',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': values,
                    'backgroundColor': self.color_scheme['pastel'],
                    'borderColor': '#FFFFFF',
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Distribusi Musim Wisata Palembang'
                    },
                    'legend': {
                        'position': 'bottom'
                    }
                }
            }
        }
        
        return self._convert_to_json_serializable(chart_data)
    
    def generate_comparison_chart_data(self, df):
        """Generate data untuk chart perbandingan tahun terakhir - REAL DATA"""
        if df.empty:
            return self._get_empty_chart_data("Perbandingan")
        
        # Ambil 2 tahun terakhir
        years = sorted(df['year'].unique())
        if len(years) < 2:
            return self._get_empty_chart_data("Perbandingan - Data Minimal 2 Tahun")
        
        recent_years = years[-2:]
        
        chart_datasets = []
        colors = self.color_scheme['primary']
        
        for i, year in enumerate(recent_years):
            year_data = df[df['year'] == year]
            
            # Urutkan data berdasarkan bulan
            monthly_data = []
            for month in self.months_order:
                month_data = year_data[year_data['month'] == month]
                if not month_data.empty:
                    monthly_data.append(int(month_data['value'].iloc[0]))
                else:
                    monthly_data.append(0)
            
            chart_datasets.append({
                'label': f'Tahun {int(year)}',
                'data': monthly_data,
                'backgroundColor': colors[i % len(colors)] + '80',
                'borderColor': colors[i % len(colors)],
                'borderWidth': 2,
                'fill': False
            })
        
        chart_data = {
            'type': 'bar',
            'data': {
                'labels': [month[:3] for month in self.months_order],
                'datasets': chart_datasets
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'Perbandingan Bulanan Tahun {int(recent_years[0])} vs {int(recent_years[1])}'
                    }
                },
                'scales': {
                    'x': {
                        'stacked': False
                    },
                    'y': {
                        'stacked': False,
                        'beginAtZero': True
                    }
                }
            }
        }
        
        return self._convert_to_json_serializable(chart_data)
    
    def _categorize_seasons(self, df):
        """Kategorikan data menjadi high/medium/low season - REAL CALCULATION"""
        if df.empty:
            return {'No Data': 1}
        
        # Hitung rata-rata per bulan
        monthly_avg = df.groupby('month')['value'].mean()
        
        # Urutkan berdasarkan bulan
        monthly_avg = monthly_avg.reindex(self.months_order)
        
        # Kategorikan berdasarkan quartile
        high_threshold = monthly_avg.quantile(0.75)
        low_threshold = monthly_avg.quantile(0.25)
        
        high_season_count = len(monthly_avg[monthly_avg >= high_threshold])
        low_season_count = len(monthly_avg[monthly_avg <= low_threshold])
        medium_season_count = len(monthly_avg) - high_season_count - low_season_count
        
        return {
            'High Season': int(high_season_count),
            'Medium Season': int(medium_season_count),
            'Low Season': int(low_season_count)
        }
    
    def _get_empty_chart_data(self, chart_type):
        """Return empty chart data"""
        empty_data = {
            'type': 'bar' if chart_type != 'Pie' else 'pie',
            'data': {
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'No Data Available',
                    'data': [1],
                    'backgroundColor': ['#CCCCCC']
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'{chart_type} Chart - No Data Available'
                    }
                }
            }
        }
        
        return empty_data
    
    def generate_all_charts_data(self, df):
        """Generate semua data chart sekaligus"""
        charts = {
            'monthly': self.generate_monthly_chart_data(df),
            'yearly': self.generate_yearly_chart_data(df),
            'seasonal': self.generate_seasonal_pie_data(df),
            'comparison': self.generate_comparison_chart_data(df)
        }
        return self._convert_to_json_serializable(charts)