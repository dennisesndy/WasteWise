"""
WasteWise - Demand Forecasting System for Perishable Goods
Main application entry point.
"""

import streamlit as st
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# Configuration
from config.settings import APP_TITLE, APP_ICON, APP_LAYOUT

# Data
from data.loader import load_data, get_column_mapping, get_product_list, get_unique_values

# Models
from models.arima_model import run_arima_forecast, ARIMA_AVAILABLE
from models.clustering import run_clustering_analysis, get_product_cluster, SKLEARN_AVAILABLE
from models.random_forest_model import run_random_forest  # <--- New Import
from models.simulation import run_simulation

# Components
from components.sidebar import render_sidebar
from components.header import render_header, render_product_badge, render_section_title
from components.metrics import render_metric_card, render_metrics_row, render_insight_box
from components.charts import (
    render_arima_chart,
    render_simulation_chart,
    render_cluster_chart,
    render_comparison_chart,
    render_historical_chart,
    render_sensitivity_chart,
    render_factor_breakdown,
)
from components.recommendations import render_recommendations

# Styles
from styles.theme import get_custom_css

# Utils
from utils.helpers import get_waste_class, safe_mean


# ─────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state="expanded",
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


# ─────────────────────────────────────────
# Load Data
# ─────────────────────────────────────────
df = load_data()
columns = get_column_mapping(df)

# Extract column references
COL_PRODUCT = columns["product"]
COL_DEMAND = columns["demand"]
COL_WEATHER = columns["weather"]
COL_SEASON = columns["season"]
COL_DATE = columns["date"]


# ─────────────────────────────────────────
# Sidebar Controls
# ─────────────────────────────────────────
products = get_product_list(df, COL_PRODUCT)
weather_options = get_unique_values(df, COL_WEATHER, ["Sunny"])
season_options = get_unique_values(df, COL_SEASON, ["Spring", "Summer", "Autumn", "Winter"])

user_input = render_sidebar(products, weather_options, season_options)


# ─────────────────────────────────────────
# Header
# ─────────────────────────────────────────
render_header()

# Library availability warnings
if not ARIMA_AVAILABLE:
    st.warning("⚠️ `statsmodels` not installed. ARIMA forecasting disabled.")
if not SKLEARN_AVAILABLE:
    st.warning("⚠️ `scikit-learn` not installed. Clustering disabled.")


# ─────────────────────────────────────────
# Run Models
# ─────────────────────────────────────────
with st.spinner("Running analysis..."):
    # Random Forest Forecast
    rf_res = None
    if SKLEARN_AVAILABLE and COL_DATE in df.columns:
        # Filter data for the specific product before passing to RF
        product_df = df[df[COL_PRODUCT] == user_input["product"]]
        
        if COL_DATE:
            product_df = product_df.sort_values(COL_DATE)

        if len(product_df) > 14: # Ensure enough data for 7-day lags
            rf_res = run_random_forest(
                df=product_df,
                target_col=COL_DEMAND,
                n_forecast=user_input["forecast_days"]
            )
    else: st.warning("⚠️ Random Forest disabled: Date column not found or Scikit-Learn missing.")
    # ARIMA Forecast
    arima_res, arima_err = None, None
    if ARIMA_AVAILABLE:
        arima_res, arima_err = run_arima_forecast(
            df=df,
            col_product=COL_PRODUCT,
            col_demand=COL_DEMAND,
            product_name=user_input["product"],
            p=user_input["arima_p"],
            d=user_input["arima_d"],
            q=user_input["arima_q"],
            auto_order=user_input["use_auto_arima"],
            n_forecast=user_input["forecast_days"]
        )

    # Clustering
    cluster_res, cluster_err = None, None
    if SKLEARN_AVAILABLE:
        cluster_res, cluster_err = run_clustering_analysis(
            df=df,
            col_product=COL_PRODUCT,
            col_demand=COL_DEMAND,
            col_season=COL_SEASON,
            col_weather=COL_WEATHER,
            n_clusters=user_input["n_clusters"]
        )

    # Get product's cluster info
    product_cluster = get_product_cluster(cluster_res, user_input["product"]) if cluster_res else None

    # Simulation
    arima_daily = arima_res["pred_mean"].tolist() if arima_res else None
    sim_res, sim_err = run_simulation(
        df=df,
        columns=columns,
        product_name=user_input["product"],
        weather_val=user_input["weather"],
        season_val=user_input["season"],
        discount_pct=user_input["discount"],
        initial_inventory=user_input["initial_qty"],
        days=user_input["forecast_days"],
        arima_daily=arima_daily
    )



# ─────────────────────────────────────────
# Product Badge & Warnings
# ─────────────────────────────────────────
render_product_badge(user_input["product"])

if sim_err:
    st.error(f"❌ {sim_err}")
    st.stop()

for warning in sim_res.get("warnings", []):
    st.warning(f"⚠️ {warning}")

if arima_err:
    st.info(f"ℹ️ ARIMA: {arima_err}")


# ─────────────────────────────────────────
# Navigation Tabs
# ─────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Forecast", "🎯 Clusters", "📈 Analysis"])


# ═══════════════════════════════════════════
# TAB 1: FORECAST
# ═══════════════════════════════════════════
with tab1:
    # ── Forecast Summary Metrics ──
    render_section_title("📊", "Forecast Summary")
    
    waste_pct = sim_res["waste_pct"]
    waste_cls = get_waste_class(waste_pct)
    arima_avg = round(safe_mean(arima_res["pred_mean"]), 1) if arima_res else "N/A"
    
    metrics = [
        {"label": "Typical Daily Sales", "value": sim_res["base_demand"], 
         "sub": "units/day", "card_class": "safe"},
        {"label": "AI Daily Prediction", "value": arima_avg,
         "sub": "units/day", "card_class": "arima"},
        {"label": f"Expected Sales ({user_input['forecast_days']}d)", 
         "value": sim_res["total_projected"], "sub": "units", "card_class": "safe"},
        {"label": "Expected Leftovers", "value": sim_res["total_waste"],
         "sub": "units at risk", "card_class": waste_cls},
        {"label": "Leftover Percentage", "value": f"{waste_pct}%",
         "sub": "of total inventory", "card_class": waste_cls},
    ]
    render_metrics_row(metrics)
    
    if arima_res:
        render_insight_box(
            "🔀 <strong>Smart Prediction</strong>: Combines AI trends (60%) with rules like weather and discounts (40%).",
            "info"
        )

    # ── ARIMA Chart ──
    if arima_res:
        render_section_title("🤖", "ARIMA model")
        
        arima_metrics = [
            {"label": "Model Complexity", "value": f"({arima_res['order'][0]},{arima_res['order'][1]},{arima_res['order'][2]})",
             "sub": "p,d,q", "card_class": "arima"},
            {"label": "Prediction Error Score (Mean Absolute Error)", "value": arima_res["aic"],
             "sub": "Lower is better", "card_class": "arima"},
            {"label": "Sales Pattern", 
             "value": "Steady ✅" if arima_res["is_stationary"] else "Changing ⚠️",
             "sub": "Data stability", "card_class": "arima"},
        ]
        render_metrics_row(arima_metrics, columns=3)
        render_arima_chart(arima_res, user_input["forecast_days"])

    if rf_res:
        render_section_title("🌲", "Random Forest Model")
        
        rf_metrics = [
            {"label": "AI Average Prediction", "value": round(rf_res['preds'].mean(), 1), 
             "sub": "units/day", "card_class": "safe"},
            {"label": "Average Mistake", "value": round(rf_res['mae'], 2), 
             "sub": "Off by this many units", "card_class": "arima"},
        ]
        render_metrics_row(rf_metrics, columns=2)
        
    # ── Simulation Chart ──
    render_section_title("📈", f"{user_input['forecast_days']}-Day Simulation")
    render_simulation_chart(sim_res["sim_df"], arima_res is not None)

    # ── Recommendations ──
    render_recommendations(
        sim_res=sim_res,
        arima_res=arima_res,
        cluster_info=product_cluster,
        discount=user_input["discount"],
        weather=user_input["weather"],
        forecast_days=user_input["forecast_days"]
    )

# ═══════════════════════════════════════════
# TAB 2: CLUSTERS
# ═══════════════════════════════════════════
with tab2:
    render_section_title("🎯", "Product Grouping")
    
    if cluster_res:
        # Cluster metrics
        cluster_metrics = [
            {"label": "Product Groups Found", "value": cluster_res["n_clusters"],
             "sub": "Total categories", "card_class": "cluster"},
            {"label": "Grouping Quality Score", "value": cluster_res["silhouette_score"],
             "sub": "Higher is better", "card_class": "cluster"},
        ]
        
        if product_cluster:
            cluster_metrics.append({
                "label": f"{user_input['product']} Group",
                "value": product_cluster["cluster_label"],
                "sub": f"{product_cluster['products_in_cluster']} similar products",
                "card_class": "cluster"
            })
        
        render_metrics_row(cluster_metrics, columns=3)
        
        render_insight_box(
            "🎯 Products are grouped by <strong>how much they sell</strong> and "
            "<strong>how predictable they are</strong>. Similar products can use similar stocking rules.",
            "cluster"
        )
        
        render_cluster_chart(cluster_res)
        
        # Cluster interpretation
        render_section_title("📋", "Group Profiles")
        for _, row in cluster_res["cluster_summary"].iterrows():
            st.markdown(
                f"- **Group {int(row['cluster'])} ({row['label']})**: "
                f"{int(row['product_count'])} products, "
                f"average sales {row['avg_demand']:.1f} units/day"
            )
    else:
        st.info("Grouping unavailable. Check that scikit-learn is installed.")

# ═══════════════════════════════════════════
# TAB 3: ANALYSIS
# ═══════════════════════════════════════════
with tab3:
    # ── Factor Breakdown ──
    render_section_title("🔬", "What is Driving Sales?")
    if rf_res and 'feature_importance' in rf_res:
        st.subheader("🌲 Top Factors Influencing the AI")
        importance_df = pd.DataFrame({
        'Feature': rf_res['feature_importance'].keys(),
        'Importance': rf_res['feature_importance'].values()
     }).sort_values(by='Importance', ascending=False).head(5)
        st.bar_chart(importance_df.set_index('Feature'))
        st.caption("This shows which factors (like Past Sales or Weather) influenced the prediction the most.")
    
    factors = {
        "Normal Daily Sales": sim_res["base_demand"],
        f"+ Weather Impact ({user_input['weather']})": round(
            sim_res["base_demand"] * sim_res["w_mult"], 1
        ),
        f"+ Season Impact ({user_input['season']})": round(
            sim_res["base_demand"] * sim_res["w_mult"] * sim_res["s_mult"], 1
        ),
        f"+ Discount Impact ({user_input['discount']}%)": sim_res["projected_daily"],
    }
    
    multipliers = {
        "weather": sim_res["w_mult"],
        "season": sim_res["s_mult"],
        "discount": sim_res["disc_adj"],
    }
    
    render_factor_breakdown(factors, multipliers, arima_res is not None)

    # ── Model Comparison ──
    if arima_res:
        render_section_title("⚖️", "Comparing Prediction Methods")
        
        sim_df = sim_res["sim_df"]
        arima_vals = sim_df["ARIMA Forecast"].dropna().values
        factor_vals = sim_df["Factor Forecast"].values[:len(arima_vals)]
        blend_vals = sim_df["Projected Demand"].values[:len(arima_vals)]
        
        mae_arima = round(float(np.mean(np.abs(arima_vals - blend_vals))), 2)
        mae_factor = round(float(np.mean(np.abs(factor_vals - blend_vals))), 2)
        diff = round(float(np.mean(arima_vals)) - float(np.mean(factor_vals)), 1)
        
        comp_metrics = [
            {"label": "AI Average Mistake", "value": mae_arima, "sub": "Units off", "card_class": "arima"},
            {"label": "Rule-based Mistake", "value": mae_factor, "sub": "Units off", "card_class": "safe"},
            {"label": "Difference Between Methods", "value": abs(diff), 
             "sub": f"AI is {'higher' if diff > 0 else 'lower'}", 
             "card_class": "warning" if abs(diff) > 5 else "safe"},
        ]
        render_metrics_row(comp_metrics, columns=3)
        render_comparison_chart(sim_df)

    # ── Historical Distribution ──
    render_section_title("📉", "Past Sales History")
    
    hist_df = sim_res["historical_subset"]
    if COL_DEMAND in hist_df.columns and not hist_df.empty:
        col_a, col_b = st.columns([3, 1])
        
        with col_a:
            arima_avg_val = round(safe_mean(arima_res["pred_mean"]), 1) if arima_res else None
            render_historical_chart(
                hist_df=hist_df,
                col_demand=COL_DEMAND,
                col_date=COL_DATE,
                projected_daily=sim_res["projected_daily"],
                base_demand=sim_res["base_demand"],
                arima_avg=arima_avg_val
            )
        
        with col_b:
            stats = hist_df[COL_DEMAND].describe().round(1)
            stats_df = pd.DataFrame({"Stat": stats.index, "Value": stats.values})
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
            cv = (hist_df[COL_DEMAND].std() / hist_df[COL_DEMAND].mean() * 100 
                  if hist_df[COL_DEMAND].mean() > 0 else 0)
            if cv > 25:
                render_insight_box(f"⚠️ Highly Unpredictable Sales (Fluctuates by {cv:.1f}%)", "warn")
            else:
                render_insight_box(f"✅ Steady Sales (Fluctuates by {cv:.1f}%)", "info")

    # ── Sensitivity Analysis ──
    render_section_title("🏷", "How Discounts Affect Sales")
    
    discount_range = list(range(0, 55, 5))
    sens_demands, sens_wastes, sens_arima = [], [], []
    
    for d in discount_range:
        d_adj = 1 + (d / 100 * 1.2)
        proj = sim_res["base_demand"] * sim_res["w_mult"] * sim_res["s_mult"] * d_adj
        waste = max(0, user_input["initial_qty"] - proj * user_input["forecast_days"])
        sens_demands.append(round(proj, 1))
        sens_wastes.append(round(waste, 1))
        if arima_res:
            arima_boosted = safe_mean(arima_res["pred_mean"]) * d_adj
            sens_arima.append(round(arima_boosted, 1))
    
    render_sensitivity_chart(
        discount_range=discount_range,
        sens_demands=sens_demands,
        sens_wastes=sens_wastes,
        sens_arima=sens_arima if arima_res else [],
        current_discount=user_input["discount"]
    )
    

    


# ─────────────────────────────────────────
# Data Expanders
# ─────────────────────────────────────────
with st.expander("🗂 Raw Historical Data"):
    raw = df[df[COL_PRODUCT] == user_input["product"]].reset_index(drop=True) if COL_PRODUCT else df
    st.dataframe(raw, use_container_width=True)

with st.expander("📋 Simulation Table"):
    st.dataframe(sim_res["sim_df"], use_container_width=True)

if arima_res:
    with st.expander("🔢 ARIMA Forecast Values"):
        arima_table = pd.DataFrame({
            "Day": list(range(1, user_input["forecast_days"] + 1)),
            "Forecast": arima_res["pred_mean"].round(1),
            "CI Lower": arima_res["ci_lower"].round(1),
            "CI Upper": arima_res["ci_upper"].round(1),
        })
        st.dataframe(arima_table, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────
# Footer
# ─────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#9ca3af; font-size:0.8rem;'>"
    "🌿 WasteWise · Demand Forecasting for Sustainable Inventory Management"
    "</p>",
    unsafe_allow_html=True,
)
