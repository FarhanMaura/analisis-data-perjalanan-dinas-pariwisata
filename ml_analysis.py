import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import sqlite3
from datetime import datetime
import random

class TourismAnalyzer:
    def __init__(self, db_path='tourism.db'):
        self.db_path = db_path
        self.scaler = StandardScaler()
        self.last_suggestions = []

    def _convert_to_json_serializable(self, obj):
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

    def get_tourism_data(self):
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
        return df

    def analyze_seasonal_distribution(self, df):
        if df.empty:
            return {
                'season_categories': {'High': 0, 'Medium': 0, 'Low': 0},
                'monthly_performance': {},
                'season_percentages': {'High': 0, 'Medium': 0, 'Low': 0},
                'total_visitors': 0,
                'clustering_metrics': {'silhouette_score': 0, 'inertia': 0}
            }

        # 1. Prepare Data
        monthly_avg = df.groupby('month')['value'].mean()
        months_order = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        monthly_avg = monthly_avg.reindex(months_order).fillna(0)
        
        # Reshape for sklearn (n_samples, n_features)
        X = monthly_avg.values.reshape(-1, 1)
        
        # 2. Apply K-Means Clustering
        # We use 3 clusters for Low, Medium, High seasons
        try:
            # Check if we have enough variance/data points for 3 clusters
            n_unique = len(np.unique(X))
            n_clusters = min(3, n_unique) if n_unique > 0 else 1
            
            if n_clusters < 2:
                 # Fallback if data is too uniform (rare case)
                 kmeans_labels = np.zeros(len(X), dtype=int)
                 centroids = np.array([[np.mean(X)]])
                 silhouette = 0
            else:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                kmeans_labels = kmeans.fit_predict(X)
                centroids = kmeans.cluster_centers_
                try:
                    silhouette = silhouette_score(X, kmeans_labels)
                except:
                    silhouette = 0 # Can happen if all points are nearly identical
        except Exception as e:
            # Severe fallback
            print(f"KMeans Error: {e}")
            return self._fallback_quantile_analysis(df)

        # 3. Map Clusters to High/Medium/Low based on Centroid values
        # Sort cluster indices by their centroid value (ascending)
        sorted_indices = np.argsort(centroids.flatten())
        
        # Map sorted index to meaningful label
        # If we have 3 clusters: 0=Low, 1=Medium, 2=High
        # If we have 2 clusters: 0=Low, 1=High
        label_map = {}
        if n_clusters == 3:
            label_map = {sorted_indices[0]: 'Low', sorted_indices[1]: 'Medium', sorted_indices[2]: 'High'}
        elif n_clusters == 2:
            label_map = {sorted_indices[0]: 'Low', sorted_indices[1]: 'High'}
        else:
            label_map = {0: 'Medium'}

        # 4. Generate Results
        season_categories = {}
        monthly_performance = {}
        season_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        
        for i, month in enumerate(months_order):
            original_val = monthly_avg[month]
            monthly_performance[month] = float(original_val)
            
            cluster_id = kmeans_labels[i]
            category = label_map.get(cluster_id, 'Medium')
            season_categories[month] = category
            
        # Calculate Volume per Season
        total_visitors = monthly_avg.sum()
        high_season_visitors = monthly_avg[[m for m, c in season_categories.items() if c == 'High']].sum()
        medium_season_visitors = monthly_avg[[m for m, c in season_categories.items() if c == 'Medium']].sum()
        low_season_visitors = monthly_avg[[m for m, c in season_categories.items() if c == 'Low']].sum()

        if total_visitors > 0:
            high_percentage = (high_season_visitors / total_visitors) * 100
            medium_percentage = (medium_season_visitors / total_visitors) * 100
            low_percentage = (low_season_visitors / total_visitors) * 100
        else:
            high_percentage = medium_percentage = low_percentage = 0

        return {
            'season_categories': season_categories,
            'monthly_performance': monthly_performance,
            'season_percentages': {
                'High': round(high_percentage, 1),
                'Medium': round(medium_percentage, 1),
                'Low': round(low_percentage, 1)
            },
            'total_visitors': float(total_visitors),
            'high_season_months': [month for month, cat in season_categories.items() if cat == 'High'],
            'low_season_months': [month for month, cat in season_categories.items() if cat == 'Low'],
            'clustering_metrics': {
                'silhouette_score': round(float(silhouette), 3),
                'n_clusters': n_clusters,
                'method': 'K-Means Clustering'
            }
        }

    def _fallback_quantile_analysis(self, df):
        # Original logic as fallback
        monthly_avg = df.groupby('month')['value'].mean()
        months_order = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        monthly_avg = monthly_avg.reindex(months_order).fillna(0)
        total_visitors = monthly_avg.sum()
        high_threshold = monthly_avg.quantile(0.70)
        low_threshold = monthly_avg.quantile(0.30)

        season_categories = {}
        monthly_performance = {}

        for month in months_order:
            value = monthly_avg[month]
            monthly_performance[month] = float(value)

            if value >= high_threshold:
                season_categories[month] = 'High'
            elif value <= low_threshold:
                season_categories[month] = 'Low'
            else:
                season_categories[month] = 'Medium'
                
        # ... simplified return for fallback ...
        return {
            'season_categories': season_categories,
            'monthly_performance': monthly_performance,
            'season_percentages': {'High': 0, 'Medium': 0, 'Low': 0}, # Dummy
            'total_visitors': float(total_visitors),
            'high_season_months': [],
            'low_season_months': [],
            'clustering_metrics': {'method': 'Quantile (Fallback)'}
        }

    def analyze_patterns(self, df):
        if df.empty:
            return {}

        patterns = {}
        yearly_totals = df.groupby('year')['value'].sum()
        if len(yearly_totals) > 1:
            trends = []
            years_sorted = sorted(yearly_totals.index)
            for i in range(1, len(years_sorted)):
                growth = ((yearly_totals.iloc[i] - yearly_totals.iloc[i-1]) / yearly_totals.iloc[i-1]) * 100
                trends.append({
                    'period': f"{years_sorted[i-1]}-{years_sorted[i]}",
                    'growth': float(growth),
                    'direction': 'naik' if growth > 0 else 'turun'
                })
            patterns['trends'] = trends

        monthly_avg = df.groupby('month')['value'].mean()
        if not monthly_avg.empty:
            months_order = ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December']
            monthly_avg = monthly_avg.reindex(months_order)
            peak_threshold = monthly_avg.quantile(0.75)
            low_threshold = monthly_avg.quantile(0.25)
            patterns['peak_months'] = monthly_avg[monthly_avg >= peak_threshold].to_dict()
            patterns['low_months'] = monthly_avg[monthly_avg <= low_threshold].to_dict()
            patterns['avg_by_month'] = monthly_avg.to_dict()

        patterns['seasonal_distribution'] = self.analyze_seasonal_distribution(df)

        return patterns

    def get_suggestion_count_based_on_data(self, total_years, total_records):
        if total_years == 0:
            return 1
        elif total_years == 1:
            return 1
        elif total_years == 2:
            return 2
        elif total_years >= 3:
            return 3
        else:
            return 1

    def select_top_suggestions(self, potential_suggestions, max_suggestions=3):
        if not potential_suggestions:
            return []

        if len(potential_suggestions) <= max_suggestions:
            selected = potential_suggestions
        else:
            selected = random.sample(potential_suggestions, max_suggestions)
        
        self.last_suggestions = selected
        return selected

    def generate_focused_suggestions(self, patterns, total_years, total_records):
        suggestions_pool = []

        if not patterns:
            basic_suggestions = [
                "Upload data kunjungan wisatawan untuk memulai analisis.",
                "Data belum tersedia. Upload file CSV dengan data kunjungan wisatawan.",
                "Sistem siap menganalisis. Silakan upload data pertama Anda."
            ]
            return random.sample(basic_suggestions, min(1, len(basic_suggestions)))

        if total_years >= 2 and 'trends' in patterns and patterns['trends']:
            latest_trend = patterns['trends'][-1]
            growth = latest_trend['growth']

            if growth > 20:
                suggestions_pool.append(f"🚀 Pertumbuhan excellent {growth:.1f}%! Pertahankan strategi marketing yang berjalan.")
                suggestions_pool.append(f"💎 Dengan growth {growth:.1f}%, fokus pada retensi pengunjung dengan meningkatkan kualitas layanan.")
            elif growth > 5:
                suggestions_pool.append(f"📈 Trend positif {growth:.1f}%. Terus kembangkan paket wisata inovatif.")
                suggestions_pool.append(f"🎯 Growth {growth:.1f}% menunjukkan momentum bagus. Optimalkan partnership.")
            elif growth > -5:
                suggestions_pool.append(f"⚖️ Pertumbuhan stabil {growth:.1f}%. Fokus pada diversifikasi produk wisata.")
            elif growth > -15:
                suggestions_pool.append(f"⚠️ Perlu perhatian: penurunan {abs(growth):.1f}%. Tingkatkan promosi digital.")
            else:
                suggestions_pool.append(f"🚨 Penurunan signifikan {abs(growth):.1f}%. Evaluasi strategi pemasaran.")

        if 'seasonal_distribution' in patterns:
            seasonal_data = patterns['seasonal_distribution']
            high_percentage = seasonal_data['season_percentages']['High']
            low_percentage = seasonal_data['season_percentages']['Low']
            high_season_months = seasonal_data['high_season_months']
            low_season_months = seasonal_data['low_season_months']

            if high_percentage > 40 and high_season_months:
                suggestions_pool.append(f"🎪 High season ({', '.join(high_season_months)}) menyumbang {high_percentage}% total pengunjung. Optimalkan kapasitas.")
            elif high_percentage > 25 and high_season_months:
                suggestions_pool.append(f"🌟 Musim tinggi {high_percentage}% di {', '.join(high_season_months)}. Fokus pada yield management.")

            if low_percentage > 35 and low_season_months:
                suggestions_pool.append(f"💡 Low season {low_percentage}% di {', '.join(low_season_months)}. Butuh strategi khusus: buat event budaya.")
            elif low_percentage > 20 and low_season_months:
                suggestions_pool.append(f"📅 Bulan {', '.join(low_season_months)} punya potensi growth. Kembangkan paket promo.")

        if 'peak_months' in patterns and patterns['peak_months']:
            peak_months = list(patterns['peak_months'].keys())
            if len(peak_months) <= 3:
                suggestions_pool.append(f"🔥 Peak season: {', '.join(peak_months)}. Siapkan contingency plan dan tingkatkan kapasitas.")

        if 'low_months' in patterns and patterns['low_months'] and total_years >= 1:
            low_months = list(patterns['low_months'].keys())
            if low_months:
                suggestions_pool.append(f"🌱 Bulan {', '.join(low_months)} butuh stimulus. Kembangkan festival lokal.")

        if total_years == 1:
            suggestions_pool.append("📋 Data 1 tahun: Analisis dasar tersedia. Upload data tahun lain untuk melihat trend.")
        elif total_years == 2:
            suggestions_pool.append("🔍 Data 2 tahun: Trend dasar teridentifikasi. Lanjutkan pengumpulan data.")
        elif total_years >= 3:
            suggestions_pool.append("🎯 Data multi-tahun tersedia. Kembangkan strategi jangka panjang berdasarkan pola historis.")

        if total_years >= 2:
            strategic_suggestions = [
                "🛍️ Kembangkan 'Palembang Experience Package' termasuk kuliner dan heritage tour",
                "📱 Optimalkan mobile app dengan virtual tour dan digital guide",
                "🤝 Kolaborasi dengan influencer travel untuk meningkatkan brand awareness",
                "🎭 Buat kalender event tahunan dengan festival budaya",
                "🏨 Develop partnership package dengan hotel premium"
            ]
            if suggestions_pool and len(strategic_suggestions) > 0:
                suggestions_pool.append(random.choice(strategic_suggestions))

        general_suggestions = [
            "💡 Tingkatkan kualitas konten digital destinasi Palembang",
            "🔍 Optimalkan sistem booking online untuk kemudahan pengunjung",
            "🌟 Kembangkan paket wisata keluarga dengan aktivitas beragam",
            "📊 Fokus pada pengumpulan data yang konsisten untuk analisis lebih baik"
        ]

        needed_suggestions = self.get_suggestion_count_based_on_data(total_years, total_records)
        if len(suggestions_pool) < needed_suggestions:
            additional_needed = needed_suggestions - len(suggestions_pool)
            available_general = [s for s in general_suggestions if s not in suggestions_pool]
            selected_general = random.sample(available_general, min(additional_needed, len(available_general)))
            suggestions_pool.extend(selected_general)

        if not suggestions_pool:
            suggestions_pool = [
                "📊 Sistem sedang menganalisis pola data. Upload lebih banyak data untuk insight yang lebih detail.",
                "💡 Fokus pada pengumpulan data yang konsisten untuk membangun database yang komprehensif."
            ]

        suggestion_count = self.get_suggestion_count_based_on_data(total_years, total_records)
        return self.select_top_suggestions(suggestions_pool, suggestion_count)

    def prepare_features(self, df):
        if df.empty:
            return pd.DataFrame()

        pivot_df = df.pivot_table(values='value', index='year', columns='month', fill_value=0)

        all_months = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']

        for month in all_months:
            if month not in pivot_df.columns:
                pivot_df[month] = 0

        pivot_df = pivot_df[all_months]
        pivot_df['total_visitors'] = pivot_df.sum(axis=1)

        return pivot_df

    def get_detailed_analysis(self):
        df = self.get_tourism_data()

        if df.empty:
            return {
                'suggestions': ["Upload data kunjungan wisatawan untuk memulai analisis."],
                'patterns': {},
                'summary': {},
                'data_quality': {'total_years': 0, 'total_records': 0}
            }

        patterns = self.analyze_patterns(df)
        total_years = len(df['year'].unique())
        total_records = len(df)

        suggestions = self.generate_focused_suggestions(patterns, total_years, total_records)

        summary = {
            'total_years': total_years,
            'total_visitors': int(df['value'].sum()),
            'avg_monthly': float(df['value'].mean()),
            'data_period': f"{int(df['year'].min())}-{int(df['year'].max())}"
        }

        result = {
            'suggestions': suggestions,
            'patterns': self._convert_to_json_serializable(patterns),
            'summary': summary,
            'data_quality': {
                'total_years': total_years,
                'total_records': total_records,
                'completeness': 'baik' if total_records >= total_years * 10 else 'cukup'
            }
        }

        return self._convert_to_json_serializable(result)

    def get_seasonal_analysis_for_charts(self):
        df = self.get_tourism_data()
        seasonal_data = self.analyze_seasonal_distribution(df)

        return {
            'season_percentages': seasonal_data['season_percentages'],
            'season_categories': seasonal_data['season_categories'],
            'monthly_performance': seasonal_data['monthly_performance']
        }

    def get_analysis_for_export(self):
        """Get analysis data in format suitable for Excel export"""
        detailed_analysis = self.get_detailed_analysis()
        
        df = self.get_tourism_data()
        
        export_data = {
            'suggestions': detailed_analysis.get('suggestions', []),
            'patterns': detailed_analysis.get('patterns', {}),
            'summary': detailed_analysis.get('summary', {}),
            'data_quality': detailed_analysis.get('data_quality', {}),
            'raw_data': df.to_dict('records') if not df.empty else []
        }
        
        return self._convert_to_json_serializable(export_data)

    def get_seasonal_categories(self, df):
        """Get seasonal categories for export"""
        if df.empty:
            return {}
        
        seasonal_data = self.analyze_seasonal_distribution(df)
        return {
            'categories': seasonal_data.get('season_categories', {}),
            'percentages': seasonal_data.get('season_percentages', {}),
            'monthly_performance': seasonal_data.get('monthly_performance', {})
        }