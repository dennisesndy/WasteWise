"""
Sidebar controls component.
"""

import streamlit as st
from config.settings import (
    DEFAULT_FORECAST_DAYS,
    DEFAULT_INITIAL_INVENTORY,
    DEFAULT_DISCOUNT,
    N_CLUSTERS_DEFAULT,
    N_CLUSTERS_MAX,
)


def render_sidebar(products: list, weather_options: list, season_options: list) -> dict:
    """
    Render sidebar controls and return selected values.
    
    Returns:
        Dictionary of user selections
    """
    st.sidebar.markdown("## 🛒 Product Selection")
    selected_product = st.sidebar.selectbox("Select Product", products)

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📊 Forecast Settings")
    
    weather = st.sidebar.selectbox("🌤 Weather Condition", weather_options)
    season = st.sidebar.selectbox("🍂 Season", season_options)
    discount = st.sidebar.slider("🏷 Discount (%)", 0, 50, DEFAULT_DISCOUNT, 5)
    initial_qty = st.sidebar.number_input(
        "📦 Initial Inventory",
        min_value=0,
        value=DEFAULT_INITIAL_INVENTORY,
        step=10
    )
    forecast_days = st.sidebar.slider(
        "📅 Forecast Horizon (days)",
        1, 30, DEFAULT_FORECAST_DAYS
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🤖 ARIMA Settings")
    
    use_auto_arima = st.sidebar.checkbox("Auto-select best order", value=True)
    
    arima_p = st.sidebar.slider("AR order (p)", 0, 5, 1, disabled=use_auto_arima)
    arima_d = st.sidebar.slider("Integration (d)", 0, 2, 1, disabled=use_auto_arima)
    arima_q = st.sidebar.slider("MA order (q)", 0, 5, 1, disabled=use_auto_arima)

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🎯 Clustering Settings")
    
    n_clusters = st.sidebar.slider(
        "Number of Clusters",
        2, N_CLUSTERS_MAX, N_CLUSTERS_DEFAULT
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "💡 Use clustering to group products with similar demand patterns "
        "for consistent inventory strategies."
    )

    return {
        "product": selected_product,
        "weather": weather,
        "season": season,
        "discount": discount,
        "initial_qty": initial_qty,
        "forecast_days": forecast_days,
        "use_auto_arima": use_auto_arima,
        "arima_p": arima_p,
        "arima_d": arima_d,
        "arima_q": arima_q,
        "n_clusters": n_clusters,
    }
