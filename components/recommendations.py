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
        rec = f"🔴 **High risk of leftovers ({waste_pct}%)** — Reduce your order to around **{optimal} units**"
        if arima_res:
            arima_optimal = int(float(np.mean(arima_res["pred_mean"])) * forecast_days * 1.05)
            rec += f" (The AI expects you'll need ~{arima_optimal} units)"
        recs.append(rec)
    elif waste_pct > 15:
        recs.append(
            f"🟡 **Moderate leftovers expected ({waste_pct}%)** — Consider running a "
            f"**{min(discount + 5, 50)}% discount** to help boost sales"
        )
    else:
        recs.append(
            f"🟢 **Low leftover risk ({waste_pct}%)** — Your inventory levels look healthy"
        )

    # Discount recommendation
    if discount == 0 and waste_pct > 20:
        recs.append(
            f"💡 Plan to apply a **10–15% discount** on day {max(1, forecast_days - 2)} "
            "to help clear out stock before it spoils"
        )

    # Weather-based recommendations
    if sim_res["w_mult"] < 0.9:
        recs.append(
            f"🌧 **{weather} weather** usually slows down sales — be conservative when ordering"
        )
    elif sim_res["w_mult"] > 1.08:
        recs.append(
            f"☀️ **{weather} weather** usually boosts sales — consider ordering 10-15% extra"
        )

    # ARIMA-based recommendations
    if arima_res:
        if not arima_res["is_stationary"]:
            recs.append(
                "📊 **Changing sales pattern detected** — Sales are currently trending up or down, so rely more on recent data than past averages."
            )
        
        arima_avg = float(np.mean(arima_res["pred_mean"]))
        base = sim_res["base_demand"]
        if abs(arima_avg - base) > base * 0.15:
            direction = "higher than" if arima_avg > base else "lower than"
            recs.append(
                f"🤖 **AI Trend Insight**: Expected sales ({round(arima_avg, 1)}/day) are trending "
                f"{direction} your normal average ({base}/day)"
            )

    # Cluster-based recommendations
    if cluster_info:
        label = cluster_info["cluster_label"]
        if "Variable" in label:
            recs.append(
                f"🎯 **Product Group: {label}** — Sales for this item bounce around a lot; "
                "keep a little extra safety stock just in case."
            )
        elif "High-Demand" in label:
            recs.append(
                f"🎯 **Product Group: {label}** — This is a fast seller; "
                "prioritize keeping it in stock because running out costs you money."
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