import os
from pathlib import Path

class StreamlitConfig:
    # Base configuration
    APP_NAME = "Employee Assessment System"
    APP_ICON = "👥"
    LAYOUT = "wide"
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/employee_assessment")
    
    # File paths
    BASE_DIR = Path(__file__).parent.parent
    REPORTS_DIR = BASE_DIR / "reports"
    TEMPLATES_DIR = BASE_DIR / "templates"
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    SESSION_EXPIRY = 3600  # 1 hour
    
    # Assessment settings
    DEFAULT_METRIC_WEIGHTS = {
        'performance': 0.4,
        'sentiment': 0.3,
        'historical': 0.3
    }
    
    # Visualization settings
    CHART_THEME = "plotly_white"
    CHART_HEIGHT = 400
    
    # Export settings
    EXPORT_FORMATS = ['PDF', 'CSV']
    EXPORT_DIR = BASE_DIR / "exports"
    
    # Validation thresholds
    FAIRNESS_THRESHOLDS = {
        'sentiment_bias': 0.2,
        'promotion_parity': 0.8,
        'performance_correlation': 0.7
    }
    
    # RAG settings
    RAG_ENABLED = True
    MAX_SIMILAR_REVIEWS = 5
    
    @classmethod
    def get_config(cls):
        """Get configuration based on environment."""
        env = os.getenv("FLASK_ENV", "development")
        if env == "production":
            return cls.get_production_config()
        elif env == "testing":
            return cls.get_testing_config()
        else:
            return cls.get_development_config()
    
    @classmethod
    def get_development_config(cls):
        """Get development configuration."""
        config = cls()
        config.DEBUG = True
        config.DATABASE_URL = "postgresql://localhost/employee_assessment_dev"
        return config
    
    @classmethod
    def get_production_config(cls):
        """Get production configuration."""
        config = cls()
        config.DEBUG = False
        config.DATABASE_URL = os.getenv("DATABASE_URL")
        config.SECRET_KEY = os.getenv("SECRET_KEY")
        return config
    
    @classmethod
    def get_testing_config(cls):
        """Get testing configuration."""
        config = cls()
        config.DEBUG = True
        config.DATABASE_URL = "postgresql://localhost/employee_assessment_test"
        config.SESSION_EXPIRY = 300  # 5 minutes
        return config 