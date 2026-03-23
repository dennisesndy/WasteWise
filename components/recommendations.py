"""
Smart recommendations component.
"""

import numpy as np
import streamlit as st
from components.header import render_section_title


def generate_recommendations(
    sim_res: dict,
    arima_res: dict = None,
    cluster_info: dict = None,
    discount: int = 0,
    weather: str = "",
    forecast_days: int = 7
) -> list[str]:
    """Generate smart recommendations based on analysis results."""
    recs = []
    waste_pct = sim_res["waste_pct"]

    # Waste-based recommendations
    if waste_pct > 30:
        optimal = int(sim_res["projected_daily"] * forecast_days * 1.05)
        rec = f"🔴 **High waste risk ({waste_pct}%)** — Reduce order to ~**{optimal} units**"
        if arima_res:
            arima_optimal = int(float(np.mean(arima_res["pred_mean"])) * forecast_days * 1.05)
            rec += f" (ARIMA suggests ~{arima_optimal} units)"
        recs.append(rec)
    elif waste_pct > 15:
        recs.append(
            f"🟡 **Moderate waste ({waste_pct}%)** — Consider a "
            f"**{min(discount + 5, 50)}% discount** to boost sales"
        )
    else:
        recs.append(
            f"🟢 **Low waste ({waste_pct}%)** — Inventory levels are well-calibrated"
        )

    # Discount recommendation
    if discount == 0 and waste_pct > 20:
        recs.append(
            f"💡 Apply a **10–15% discount** on day {max(1, forecast_days - 2)} "
            "to clear stock before expiry"
        )

    # Weather-based recommendations
    if sim_res["w_mult"] < 0.9:
        recs.append(
            f"🌧 **{weather} weather** suppresses demand — stock conservatively"
        )
    elif sim_res["w_mult"] > 1.08:
        recs.append(
            f"☀️ **{weather} weather** boosts demand — consider +10-15% stock"
        )

    # ARIMA-based recommendations
    if arima_res:
        if not arima_res["is_stationary"]:
            recs.append(
                "📊 **Non-stationary pattern detected** — demand is trending; "
                "review reorder points"
            )
        
        arima_avg = float(np.mean(arima_res["pred_mean"]))
        base = sim_res["base_demand"]
        if abs(arima_avg - base) > base * 0.15:
            direction = "above" if arima_avg > base else "below"
            recs.append(
                f"🤖 **ARIMA trend**: forecast ({round(arima_avg, 1)}/day) is "
                f"{direction} historical average ({base}/day)"
            )

    # Cluster-based recommendations
    if cluster_info:
        label = cluster_info["cluster_label"]
        if "Variable" in label:
            recs.append(
                f"🎯 **Cluster: {label}** — This product has variable demand; "
                "maintain safety stock"
            )
        elif "High-Demand" in label:
            recs.append(
                f"🎯 **Cluster: {label}** — Prioritize availability; "
                "stockouts are costly"
            )

    return recs


def render_recommendations(
    sim_res: dict,
    arima_res: dict = None,
    cluster_info: dict = None,
    discount: int = 0,
    weather: str = "",
    forecast_days: int = 7
):
    """Render the smart recommendations section."""
    render_section_title("💡", "Smart Recommendations")
    
    recs = generate_recommendations(
        sim_res=sim_res,
        arima_res=arima_res,
        cluster_info=cluster_info,
        discount=discount,
        weather=weather,
        forecast_days=forecast_days
    )
    
    for rec in recs:
        st.markdown(f"- {rec}")
