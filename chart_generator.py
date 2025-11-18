import pandas as pd
import numpy as np
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

class ChartGenerator:
    def __init__(self, ml_analyzer=None):
        self.color_scheme = {
            'primary': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'],
            'secondary': ['#FFA07A', '#20B2AA', '#778899', '#DEB887', '#98FB98', '#FFB6C1'],
            'pastel': ['#FFD1DC', '#C4E1FF', '#D1FFBD', '#FFF4BD', '#E1C4FF', '#FFD8C9'],
            'seasonal': {
                'High': '#FF6B6B',
                'Medium': '#4ECDC4',
                'Low': '#45B7D1'
            }
        }
        self.months_order = ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December']
        self.ml_analyzer = ml_analyzer

    def _convert_to_json_serializable(self, obj: Any) -> Any:
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        elif hasattr(obj, 'tolist'):
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
            return str(obj)

    def generate_seasonal_bar_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return self._get_empty_chart_data("Bar")

        print("DEBUG: Generating SIMPLE seasonal bar chart data...")
        
        monthly_avg = df.groupby('month')['value'].mean()
        
        for month in self.months_order:
            if month not in monthly_avg:
                monthly_avg[month] = 0
        
        monthly_avg = monthly_avg.reindex(self.months_order)
        
        background_colors = []
        if not monthly_avg.empty:
            high_threshold = monthly_avg.quantile(0.70)
            low_threshold = monthly_avg.quantile(0.30)
            
            for month in self.months_order:
                value = monthly_avg[month]
                if value >= high_threshold:
                    background_colors.append('#FF6B6B')
                elif value <= low_threshold:
                    background_colors.append('#45B7D1')
                else:
                    background_colors.append('#4ECDC4')
        else:
            background_colors = ['#4ECDC4'] * 12

        chart_data = {
            'type': 'bar',
            'data': {
                'labels': self.months_order,
                'datasets': [{
                    'label': 'Rata-rata Pengunjung per Bulan',
                    'data': [float(monthly_avg[month]) for month in self.months_order],
                    'backgroundColor': background_colors,
                    'borderColor': '#2C3E50',
                    'borderWidth': 1
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Performa Bulanan dengan Kategori Musim'
                    },
                    'legend': {
                        'display': False
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Jumlah Pengunjung'
                        }
                    }
                }
            }
        }

        print("DEBUG: Simple seasonal bar chart data generated")
        return chart_data

    def generate_monthly_chart_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return self._get_empty_chart_data("Bulanan")

        monthly_avg = df.groupby('month')['value'].mean().reset_index()

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

    def generate_yearly_chart_data(self, df: pd.DataFrame) -> Dict[str, Any]:
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

    def generate_seasonal_pie_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return self._get_empty_chart_data("Pie")

        if self.ml_analyzer:
            try:
                seasonal_data = self.ml_analyzer.get_seasonal_analysis_for_charts()
                if isinstance(seasonal_data, dict) and 'season_percentages' in seasonal_data:
                    season_percentages = seasonal_data['season_percentages']

                    labels = []
                    data = []
                    background_colors = []

                    for season, percentage in season_percentages.items():
                        if percentage > 0:
                            labels.append(f'{season} Season ({percentage}%)')
                            data.append(percentage)
                            background_colors.append(self.color_scheme['seasonal'][season])

                    chart_data = {
                        'type': 'pie',
                        'data': {
                            'labels': labels,
                            'datasets': [{
                                'data': data,
                                'backgroundColor': background_colors,
                                'borderColor': '#FFFFFF',
                                'borderWidth': 2
                            }]
                        },
                        'options': {
                            'responsive': True,
                            'plugins': {
                                'title': {
                                    'display': True,
                                    'text': 'Distribusi Pengunjung Berdasarkan Musim'
                                },
                                'legend': {
                                    'position': 'bottom'
                                }
                            }
                        }
                    }

                    return self._convert_to_json_serializable(chart_data)

            except Exception as e:
                print(f"Error using ML analysis for pie chart: {e}")

        seasonal_data = self._categorize_seasons(df)

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

    def generate_comparison_chart_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return self._get_empty_chart_data("Perbandingan")

        years = sorted(df['year'].unique())
        if len(years) < 2:
            return self._get_empty_chart_data("Perbandingan")

        recent_years = years[-2:]

        chart_datasets = []
        colors = self.color_scheme['primary']

        for i, year in enumerate(recent_years):
            year_data = df[df['year'] == year]

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
                        'text': f'Perbandingan Bulanan {int(recent_years[0])} vs {int(recent_years[1])}'
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

    def _categorize_seasons(self, df: pd.DataFrame) -> Dict[str, int]:
        if df.empty:
            return {'No Data': 1}

        monthly_avg = df.groupby('month')['value'].mean()
        monthly_avg = monthly_avg.reindex(self.months_order)

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

    def _get_empty_chart_data(self, chart_type: str) -> Dict[str, Any]:
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

    def generate_all_charts_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        try:
            charts = {
                'monthly': self.generate_monthly_chart_data(df),
                'yearly': self.generate_yearly_chart_data(df),
                'seasonal_pie': self.generate_seasonal_pie_data(df),
                'seasonal_bar': self.generate_seasonal_bar_data(df),
                'comparison': self.generate_comparison_chart_data(df)
            }
            print("DEBUG: All charts data generated successfully")
            return self._convert_to_json_serializable(charts)
        except Exception as e:
            print(f"Error generating all charts: {e}")
            return {}

    def generate_chart_data_for_export(self, df: pd.DataFrame) -> Dict[str, Any]:
        try:
            charts_data = self.generate_all_charts_data(df)
            
            export_data = {
                'monthly': {
                    'labels': charts_data.get('monthly', {}).get('data', {}).get('labels', []),
                    'values': charts_data.get('monthly', {}).get('data', {}).get('datasets', [{}])[0].get('data', [])
                } if charts_data.get('monthly') else {},
                'yearly': {
                    'labels': charts_data.get('yearly', {}).get('data', {}).get('labels', []),
                    'values': charts_data.get('yearly', {}).get('data', {}).get('datasets', [{}])[0].get('data', [])
                } if charts_data.get('yearly') else {},
                'seasonal': self._get_seasonal_data_for_export(df)
            }
            
            return self._convert_to_json_serializable(export_data)
            
        except Exception as e:
            print(f"Error generating chart data for export: {e}")
            return {}

    def _get_seasonal_data_for_export(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {}
        
        if self.ml_analyzer:
            try:
                seasonal_data = self.ml_analyzer.get_seasonal_analysis_for_charts()
                if isinstance(seasonal_data, dict):
                    return seasonal_data
            except Exception as e:
                print(f"Error using ML analyzer for seasonal data: {e}")
        
        monthly_avg = df.groupby('month')['value'].mean()
        monthly_avg = monthly_avg.reindex(self.months_order)
        
        if monthly_avg.empty:
            return {}
        
        high_threshold = monthly_avg.quantile(0.70)
        low_threshold = monthly_avg.quantile(0.30)
        
        season_categories = {}
        for month in self.months_order:
            value = monthly_avg[month]
            if value >= high_threshold:
                season_categories[month] = 'High'
            elif value <= low_threshold:
                season_categories[month] = 'Low'
            else:
                season_categories[month] = 'Medium'
        
        return {
            'season_categories': season_categories,
            'monthly_performance': monthly_avg.to_dict()
        }