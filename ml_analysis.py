import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import sqlite3
from datetime import datetime

class TourismAnalyzer:
    def __init__(self, db_path='tourism.db'):
        self.db_path = db_path
        self.scaler = StandardScaler()
    
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

    def get_tourism_data(self):
        """Ambil data dari database"""
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
    
    def prepare_features(self, df):
        """Siapkan features untuk clustering"""
        if df.empty:
            return pd.DataFrame()
        
        # Buat pivot table: tahun vs bulan
        pivot_df = df.pivot_table(
            values='value', 
            index='year', 
            columns='month', 
            fill_value=0
        )
        
        # Pastikan semua bulan ada
        all_months = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
        
        for month in all_months:
            if month not in pivot_df.columns:
                pivot_df[month] = 0
        
        # Reorder columns
        pivot_df = pivot_df[all_months]
        
        # Tambahkan features tambahan
        pivot_df['total_visitors'] = pivot_df.sum(axis=1)
        pivot_df['peak_month'] = pivot_df[all_months].idxmax(axis=1)
        pivot_df['low_month'] = pivot_df[all_months].idxmin(axis=1)
        pivot_df['seasonality'] = pivot_df[all_months].std(axis=1) / (pivot_df[all_months].mean(axis=1) + 1e-8)
        
        return pivot_df
    
    def perform_clustering(self, features_df, n_clusters=3):
        """Lakukan clustering K-Means"""
        if len(features_df) < n_clusters:
            return None, None, None
        
        if n_clusters < 2:
            return None, None, None
        
        # Scale features
        feature_columns = [col for col in features_df.columns if col not in ['peak_month', 'low_month']]
        X = features_df[feature_columns]
        
        # Handle zero variance
        if X.std().sum() == 0:
            return None, None, None
            
        X_scaled = self.scaler.fit_transform(X)
        
        # Tentukan jumlah cluster optimal
        if len(features_df) >= 3:
            optimal_k = self.find_optimal_k(X_scaled)
            n_clusters = min(optimal_k, len(features_df))
        else:
            n_clusters = min(2, len(features_df))
        
        # Clustering dengan K-Means
        try:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X_scaled)
            return clusters, kmeans, X_scaled
        except:
            return None, None, None
    
    def find_optimal_k(self, X_scaled, max_k=5):
        """Cari jumlah cluster optimal menggunakan silhouette score"""
        best_k = 2
        best_score = -1
        
        for k in range(2, min(max_k + 1, len(X_scaled))):
            try:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels = kmeans.fit_predict(X_scaled)
                if len(np.unique(labels)) > 1:
                    score = silhouette_score(X_scaled, labels)
                    if score > best_score:
                        best_score = score
                        best_k = k
            except:
                continue
        
        return best_k
    
    def analyze_seasonal_patterns(self, df):
        """Analisis pola musiman"""
        if df.empty:
            return {
                'high_season': {},
                'low_season': {},
                'medium_season': {},
                'monthly_avg': {}
            }
        
        monthly_avg = df.groupby('month')['value'].mean()
        
        # Urutkan berdasarkan bulan
        months_order = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        monthly_avg = monthly_avg.reindex(months_order)
        
        # Kategorikan bulan menggunakan quartile
        high_threshold = monthly_avg.quantile(0.75)
        low_threshold = monthly_avg.quantile(0.25)
        
        high_season = monthly_avg[monthly_avg >= high_threshold]
        low_season = monthly_avg[monthly_avg <= low_threshold]
        medium_season = monthly_avg[(monthly_avg > low_threshold) & (monthly_avg < high_threshold)]
        
        return {
            'high_season': {k: float(v) for k, v in high_season.to_dict().items()},
            'low_season': {k: float(v) for k, v in low_season.to_dict().items()},
            'medium_season': {k: float(v) for k, v in medium_season.to_dict().items()},
            'monthly_avg': {k: float(v) for k, v in monthly_avg.to_dict().items()}
        }
    
    def detect_anomalies(self, df):
        """Deteksi anomaly dalam data"""
        yearly_data = df.groupby('year')['value'].sum()
        
        anomalies = []
        if len(yearly_data) > 1:
            mean_visitors = float(yearly_data.mean())
            std_visitors = float(yearly_data.std())
            
            if std_visitors > 0:
                for year, visitors in yearly_data.items():
                    z_score = (float(visitors) - mean_visitors) / std_visitors
                    if abs(z_score) > 1.5:
                        anomalies.append({
                            'year': int(year),
                            'visitors': int(visitors),
                            'z_score': float(z_score),
                            'type': 'high' if z_score > 0 else 'low'
                        })
        
        return anomalies
    
    def generate_ml_suggestions(self, df):
        """Generate saran berdasarkan analisis ML"""
        suggestions = []
        
        if df.empty:
            return ["Belum ada data untuk dianalisis"]
        
        features_df = self.prepare_features(df)
        
        if len(features_df) < 2:
            suggestions.append("📊 Data masih terbatas. Upload data dari tahun lain untuk analisis yang lebih akurat.")
            if not df.empty:
                total_visitors = int(df['value'].sum())
                avg_monthly = float(df['value'].mean())
                suggestions.append(f"📈 Total pengunjung: {total_visitors:,} | Rata-rata bulanan: {avg_monthly:,.0f}")
            return suggestions
        
        # Clustering analysis
        clusters, kmeans, X_scaled = self.perform_clustering(features_df)
        
        if clusters is not None:
            unique_clusters = int(len(np.unique(clusters)))
            suggestions.append(f"🔍 Terdeteksi {unique_clusters} pola kunjungan wisata yang berbeda berdasarkan data historis.")
        
        # Seasonal analysis
        seasonal_data = self.analyze_seasonal_patterns(df)
        
        if len(seasonal_data['high_season']) > 0:
            high_season_months = list(seasonal_data['high_season'].keys())
            avg_high = float(np.mean(list(seasonal_data['high_season'].values())))
            suggestions.append(f"🎯 **High Season**: {', '.join(high_season_months)} (avg: {avg_high:,.0f}/bulan) - Optimalkan kapasitas dan harga")
        
        if len(seasonal_data['low_season']) > 0:
            low_season_months = list(seasonal_data['low_season'].keys())
            avg_low = float(np.mean(list(seasonal_data['low_season'].values())))
            suggestions.append(f"💡 **Low Season**: {', '.join(low_season_months)} (avg: {avg_low:,.0f}/bulan) - Butuh strategi promosi khusus")
        
        # Trend analysis
        yearly_totals = df.groupby('year')['value'].sum()
        if len(yearly_totals) >= 2:
            years = sorted(yearly_totals.index)
            current_year = years[-1]
            prev_year = years[-2]
            
            current_total = int(yearly_totals[current_year])
            prev_total = int(yearly_totals[prev_year])
            
            if prev_total > 0:
                growth_rate = float((current_total - prev_total) / prev_total * 100)
                
                if growth_rate < -20:
                    suggestions.append(f"🚨 **Krisis**: Penurunan drastis {growth_rate:.1f}%. Perlu evaluasi menyeluruh strategi pariwisata.")
                elif growth_rate < -10:
                    suggestions.append(f"⚠️ **Warning**: Penurunan signifikan {growth_rate:.1f}%. Tingkatkan promosi digital.")
                elif growth_rate < 0:
                    suggestions.append(f"📉 **Perhatian**: Penurunan {growth_rate:.1f}%. Fokus pada improvement experience pengunjung.")
                elif growth_rate > 25:
                    suggestions.append(f"🎉 **Excellent**: Pertumbuhan luar biasa {growth_rate:.1f}%! Pertahankan momentum.")
                elif growth_rate > 10:
                    suggestions.append(f"📈 **Bagus**: Pertumbuhan solid {growth_rate:.1f}%. Kembangkan paket wisata premium.")
                else:
                    suggestions.append(f"➡️ **Stabil**: Pertumbuhan {growth_rate:.1f}%. Diversifikasi produk wisata.")
        
        # Anomaly detection
        anomalies = self.detect_anomalies(df)
        for anomaly in anomalies:
            if anomaly['type'] == 'high':
                suggestions.append(f"🌟 **Rekor Tinggi** di {anomaly['year']}: {anomaly['visitors']:,} pengunjung. Pelajari faktor keberhasilan ini.")
            else:
                suggestions.append(f"🔻 **Tahun Sulit** di {anomaly['year']}: {anomaly['visitors']:,} pengunjung. Analisis penyebab dan buat mitigation plan.")
        
        # Strategic recommendations
        suggestions.extend(self.generate_strategic_recommendations(df, features_df))
        
        return suggestions
    
    def generate_strategic_recommendations(self, df, features_df):
        """Generate rekomendasi strategis berdasarkan data aktual"""
        recommendations = []
        
        # Analisis bulanan untuk rekomendasi spesifik
        monthly_avg = df.groupby('month')['value'].mean()
        overall_avg = float(monthly_avg.mean())
        
        low_performance_mask = monthly_avg < overall_avg * 0.7
        if low_performance_mask.sum() > 0:
            low_performance_months = monthly_avg[low_performance_mask]
            recommendations.append(f"📅 **Fokus Improvement**: {', '.join(low_performance_months.index)} memiliki potensi peningkatan terbesar")
        
        # Recommendation berdasarkan consistency
        monthly_std = df.groupby('month')['value'].std()
        if len(monthly_std) > 0 and monthly_std.std() > 0:
            high_variance_mask = monthly_std > monthly_std.median() * 1.5
            if high_variance_mask.sum() > 0:
                high_variance_months = monthly_std[high_variance_mask]
                recommendations.append(f"🎭 **Stabilisasi**: {', '.join(high_variance_months.index)} menunjukkan fluktuasi tinggi, butuh strategi stabilisasi")
        
        # Event planning recommendation
        if len(features_df) >= 3:
            recommendations.append("🎪 **Event Planning**: Data multi-tahun tersedia, pertimbangkan event rutin di low season berdasarkan pattern keberhasilan tahun sebelumnya")
        
        # Digital marketing recommendation
        current_year = int(df['year'].max()) if not df.empty else None
        if current_year and current_year >= 2020:
            recommendations.append("📱 **Digital Boost**: Tingkatkan presence di media sosial dan platform booking online dengan konten visual menarik")
        
        # Collaboration recommendation
        recommendations.append("🤝 **Partnership**: Kolaborasi dengan hotel, restaurant, dan tour operator untuk package deals")
        
        return recommendations
    
    def get_detailed_analysis(self):
        """Dapatkan analisis detail untuk dashboard"""
        df = self.get_tourism_data()
        
        if df.empty:
            return {
                'suggestions': ["Belum ada data untuk dianalisis"],
                'seasonal_patterns': {},
                'clustering_info': {},
                'trend_analysis': {},
                'anomalies': []
            }
        
        # Analisis komprehensif
        features_df = self.prepare_features(df)
        clusters, kmeans, X_scaled = self.perform_clustering(features_df)
        seasonal_patterns = self.analyze_seasonal_patterns(df)
        anomalies = self.detect_anomalies(df)
        suggestions = self.generate_ml_suggestions(df)
        
        # Trend analysis
        yearly_totals = df.groupby('year')['value'].sum()
        trend_analysis = {
            'yearly_totals': {int(k): int(v) for k, v in yearly_totals.to_dict().items()},
            'growth_rates': {},
            'average_annual': int(yearly_totals.mean()) if not yearly_totals.empty else 0
        }
        
        if len(yearly_totals) > 1:
            years_sorted = sorted(yearly_totals.index)
            for i in range(1, len(years_sorted)):
                current = int(yearly_totals.iloc[i])
                previous = int(yearly_totals.iloc[i-1])
                if previous > 0:
                    growth = float((current - previous) / previous * 100)
                    trend_analysis['growth_rates'][f"{years_sorted[i-1]}-{years_sorted[i]}"] = round(growth, 1)
        
        clustering_info = {}
        if clusters is not None:
            clustering_info = {
                'n_clusters': int(len(np.unique(clusters))),
                'cluster_sizes': [int(x) for x in np.bincount(clusters).tolist()],
                'years_by_cluster': {}
            }
            
            for cluster_id in np.unique(clusters):
                years_in_cluster = [int(x) for x in features_df.index[clusters == cluster_id].tolist()]
                clustering_info['years_by_cluster'][f'Cluster {int(cluster_id)}'] = years_in_cluster
        
        result = {
            'suggestions': suggestions,
            'seasonal_patterns': seasonal_patterns,
            'clustering_info': clustering_info,
            'trend_analysis': trend_analysis,
            'anomalies': anomalies
        }
        
        return self._convert_to_json_serializable(result)