
import numpy as np
import pandas as pd
from utils.multipliers import get_season_multiplier, get_weather_multiplier
from config.settings import ARIMA_WEIGHT, FACTOR_WEIGHT


def run_simulation(
    df: pd.DataFrame,
    columns: dict,
    product_name: str,
    weather_val: str,
    season_val: str,
    discount_pct: float,
    initial_inventory: float,
    days: int,
    arima_daily: list = None
) -> tuple[dict | None, str | None]:
    """
    Run demand simulation combining factor model with ARIMA forecasts.
    
    Args:
        df: Full dataset
        columns: Column name mapping
        product_name: Selected product
        weather_val: Weather condition
        season_val: Season
        discount_pct: Discount percentage
        initial_inventory: Starting inventory
        days: Forecast horizon
        arima_daily: Optional ARIMA daily forecasts
    
    Returns:
        Tuple of (results_dict, error_message)
    """
    col_product = columns.get("product")
    col_demand = columns.get("demand")
    col_weather = columns.get("weather")
    col_season = columns.get("season")
    col_discount = columns.get("discount")

    warnings = []

    # Filter to product
    subset = df[df[col_product] == product_name].copy() if col_product else df.copy()
    if subset.empty:
        return None, "No historical data for this product"

    # Apply weather filter
    weather_subset = subset
    if col_weather:
        weather_subset = subset[subset[col_weather] == weather_val]
        if weather_subset.empty:
            weather_subset = subset
            warnings.append(f"No data for weather '{weather_val}', using overall average")

    # Apply season filter
    season_subset = weather_subset
    if col_season:
        season_subset = weather_subset[weather_subset[col_season] == season_val]
        if season_subset.empty:
            season_subset = weather_subset
            warnings.append(f"No data for season '{season_val}', using weather-filtered average")

    # Calculate base demand
    base_demand = season_subset[col_demand].mean() if col_demand else 100.0

    # Get multipliers
    w_mult = get_weather_multiplier(weather_val)
    s_mult = get_season_multiplier(season_val) if col_season else 1.0

    # Discount adjustment
    d_effect = discount_pct / 100 * 1.5
    disc_adj = 1 + d_effect

    if col_discount and col_discount in season_subset.columns:
        avg_hist = season_subset[col_discount].mean()
        disc_adj = (1 + d_effect) / max(1 + avg_hist / 100 * 1.2, 0.001)

    # Calculate factor-based daily forecast
    factor_daily = base_demand * w_mult * s_mult * disc_adj

    # Run day-by-day simulation
    sim_rows = []
    remaining = float(initial_inventory)

    for day in range(1, days + 1):
        # Blend ARIMA and factor forecasts
        blended_demand = factor_daily
        if arima_daily is not None and day <= len(arima_daily):
            blended_demand = (
                ARIMA_WEIGHT * arima_daily[day - 1] + 
                FACTOR_WEIGHT * factor_daily
            )

        # Add random variation
        day_demand = max(0, np.random.normal(blended_demand, blended_demand * 0.08))
        sold = min(remaining, day_demand)
        remaining = max(0, remaining - sold)
        daily_waste = max(0, day_demand - sold) if remaining == 0 else 0

        sim_rows.append({
            "Day": day,
            "Projected Demand": round(day_demand, 1),
            "Units Sold": round(sold, 1),
            "Remaining Inventory": round(remaining, 1),
            "Daily Waste": round(daily_waste, 1),
            "ARIMA Forecast": (
                round(arima_daily[day - 1], 1) 
                if arima_daily and day <= len(arima_daily) 
                else None
            ),
            "Factor Forecast": round(factor_daily, 1),
        })

    sim_df = pd.DataFrame(sim_rows)
    total_waste = max(0, initial_inventory - sim_df["Units Sold"].sum())

    return {
        "base_demand": round(base_demand, 1),
        "projected_daily": round(factor_daily, 1),
        "total_projected": round(factor_daily * days, 1),
        "total_sold": round(sim_df["Units Sold"].sum(), 1),
        "total_waste": round(total_waste, 1),
        "waste_pct": round(
            total_waste / initial_inventory * 100 if initial_inventory > 0 else 0, 1
        ),
        "w_mult": round(w_mult, 3),
        "s_mult": round(s_mult, 3),
        "disc_adj": round(disc_adj, 3),
        "sim_df": sim_df,
        "warnings": warnings,
        "historical_subset": season_subset,
    }, None
