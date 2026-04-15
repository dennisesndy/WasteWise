"""
Application configuration and constants.
"""

# App metadata
APP_TITLE = "WasteWise | Demand Forecasting"
APP_ICON = "🌿"
APP_LAYOUT = "wide"

# Column name candidates for flexible data loading
COLUMN_CANDIDATES = {
    "product": ["product_name", "product", "item_name", "item"],
    "weather": ["weather_condition", "weather", "condition"],
    "demand": ["daily_demand", "demand", "units_sold"],
    "season": ["season", "seasonality", "seasonal_factor"],
    "discount": ["discount", "discount_pct", "discount_percent", "promo"],
    "inventory": ["inventory", "stock", "stock_level", "quantity"],
    "date": ["date", "day", "timestamp", "record_date", "transaction_date"],
}

# Default values
DEFAULT_FORECAST_DAYS = 7
DEFAULT_INITIAL_INVENTORY = 200
DEFAULT_DISCOUNT = 0

# ARIMA defaults
ARIMA_DEFAULT_ORDER = (1, 1, 1)
ARIMA_MAX_P = 3
ARIMA_MAX_D = 1
ARIMA_MAX_Q = 3

# Clustering defaults
N_CLUSTERS_DEFAULT = 4
N_CLUSTERS_MAX = 8

# Threshold values
HIGH_WASTE_THRESHOLD = 30
MODERATE_WASTE_THRESHOLD = 15
HIGH_CV_THRESHOLD = 25

# Blending weights
ARIMA_WEIGHT = 0.4
FACTOR_WEIGHT = 0.6
