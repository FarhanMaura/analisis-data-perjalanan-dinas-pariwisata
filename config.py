import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-2023'
    UPLOAD_FOLDER = 'uploads'
    DATABASE = 'tourism.db'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # ML Settings
    DEFAULT_CLUSTERS = 3
    ANOMALY_THRESHOLD = 1.5