"""
ARIMA forecasting model.
"""

import numpy as np
import streamlit as st
from config.settings import ARIMA_MAX_P, ARIMA_MAX_D, ARIMA_MAX_Q

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False


@st.cache_data(show_spinner=False)
def run_arima_forecast(
    df,
    col_product: str,
    col_demand: str,
    product_name: str,
    p: int,
    d: int,
    q: int,
    auto_order: bool,
    n_forecast: int
) -> tuple[dict | None, str | None]:
    """
    Run ARIMA forecasting on historical demand data.
    
    Returns:
        Tuple of (results_dict, error_message)
    """
    if not ARIMA_AVAILABLE:
        return None, "statsmodels not installed"

    # Filter data for product
    subset = df[df[col_product] == product_name].copy() if col_product else df.copy()
    
    if col_demand not in subset.columns or subset[col_demand].dropna().shape[0] < 10:
        return None, "Insufficient data (need ≥10 records)"

    series = subset[col_demand].dropna().astype(float).reset_index(drop=True)
    best_order, best_aic = (p, d, q), np.inf

    # Auto order selection via grid search
    if auto_order:
        for tp in range(0, ARIMA_MAX_P + 1):
            for td in range(0, ARIMA_MAX_D + 1):
                for tq in range(0, ARIMA_MAX_Q + 1):
                    try:
                        model = ARIMA(series, order=(tp, td, tq)).fit()
                        if model.aic < best_aic:
                            best_aic, best_order = model.aic, (tp, td, tq)
                    except:
                        continue
    else:
        best_order = (p, d, q)

    try:
        model = ARIMA(series, order=best_order).fit()
        forecast = model.get_forecast(steps=n_forecast)
        pred_mean = np.maximum(forecast.predicted_mean.values, 0)
        ci = forecast.conf_int(alpha=0.10)
        ci_lower = np.maximum(ci.iloc[:, 0].values, 0)
        ci_upper = ci.iloc[:, 1].values

        # Stationarity test
        adf_result = adfuller(series, autolag="AIC")
        is_stationary = adf_result[1] < 0.05

        return {
            "order": best_order,
            "aic": round(model.aic, 2),
            "bic": round(model.bic, 2),
            "pred_mean": pred_mean,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "fitted": model.fittedvalues,
            "series": series,
            "is_stationary": is_stationary,
            "adf_pvalue": round(adf_result[1], 4),
        }, None
        
    except Exception as ex:
        return None, f"ARIMA fitting failed: {str(ex)}"
