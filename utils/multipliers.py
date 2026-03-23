"""
Demand multiplier calculations for weather and season.
"""

SEASON_MULTIPLIERS = {
    "summer": 1.15,
    "spring": 1.05,
    "autumn": 0.95,
    "fall": 0.95,
    "winter": 0.85,
}

WEATHER_MULTIPLIERS = {
    "sunny": 1.10,
    "hot": 1.12,
    "warm": 1.08,
    "cloudy": 1.00,
    "mild": 1.00,
    "normal": 1.00,
    "rainy": 0.88,
    "rain": 0.88,
    "stormy": 0.80,
    "cold": 0.85,
    "windy": 0.92,
    "snowy": 0.78,
    "foggy": 0.90,
}


def get_season_multiplier(season_val) -> float:
    """Get demand multiplier based on season."""
    if isinstance(season_val, str):
        return SEASON_MULTIPLIERS.get(season_val.lower(), 1.0)
    if isinstance(season_val, (int, float)):
        return float(season_val)
    return 1.0


def get_weather_multiplier(weather_val) -> float:
    """Get demand multiplier based on weather condition."""
    if isinstance(weather_val, str):
        return WEATHER_MULTIPLIERS.get(weather_val.lower(), 1.0)
    return 1.0
