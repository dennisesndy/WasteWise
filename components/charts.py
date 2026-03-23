"""
Chart components using Plotly.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st


# Common layout settings
LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(248,252,249,0.7)",
    font=dict(family="DM Sans", size=12),
    margin=dict(t=40, b=20, l=20, r=20),
)

GRID_COLOR = "#e5e7eb"


def render_arima_chart(arima_res: dict, forecast_days: int):
    """Render ARIMA fit and forecast chart."""
    series = arima_res["series"]
    fitted = arima_res["fitted"]
    pred = arima_res["pred_mean"]
    ci_lo = arima_res["ci_lower"]
    ci_hi = arima_res["ci_upper"]

    n_hist = len(series)
    hist_x = list(range(1, n_hist + 1))
    fore_x = list(range(n_hist + 1, n_hist + forecast_days + 1))

    fig = go.Figure()

    # Historical demand
    fig.add_trace(go.Scatter(
        x=hist_x, y=series.values,
        name="Historical", mode="lines",
        line=dict(color="#2d6a4f", width=1.5),
        opacity=0.8,
    ))

    # Fitted values
    fig.add_trace(go.Scatter(
        x=hist_x, y=fitted.values,
        name="ARIMA Fitted", mode="lines",
        line=dict(color="#457b9d", width=1.8, dash="dot"),
    ))

    # Confidence band
    fig.add_trace(go.Scatter(
        x=fore_x + fore_x[::-1],
        y=list(ci_hi) + list(ci_lo[::-1]),
        fill="toself",
        fillcolor="rgba(69,123,157,0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        name="90% CI",
        showlegend=True,
    ))

    # Forecast
    fig.add_trace(go.Scatter(
        x=fore_x, y=pred,
        name=f"Forecast ({forecast_days}d)",
        mode="lines+markers",
        line=dict(color="#457b9d", width=2.5),
        marker=dict(size=6, symbol="diamond"),
    ))

    # Separator
    fig.add_vline(
        x=n_hist + 0.5, line_dash="dash",
        line_color="#9ca3af", line_width=1.5,
        annotation_text="Forecast →",
        annotation_position="top right"
    )

    order = arima_res["order"]
    fig.update_layout(
        height=340,
        title=f"ARIMA({order[0]},{order[1]},{order[2]}) — Fit & Forecast",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title="Record Index", gridcolor=GRID_COLOR),
        yaxis=dict(title="Daily Demand", gridcolor=GRID_COLOR),
        **LAYOUT_DEFAULTS
    )

    st.plotly_chart(fig, use_container_width=True)


def render_simulation_chart(sim_df: pd.DataFrame, arima_available: bool = True):
    """Render the day-by-day simulation chart."""
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.65, 0.35],
        subplot_titles=("Demand vs. Inventory", "Daily Waste"),
        vertical_spacing=0.08,
    )

    # Factor forecast
    fig.add_trace(go.Scatter(
        x=sim_df["Day"], y=sim_df["Factor Forecast"],
        name="Factor Model", mode="lines",
        line=dict(color="#74c69d", width=1.5, dash="dash"),
    ), row=1, col=1)

    # ARIMA forecast
    if arima_available and "ARIMA Forecast" in sim_df.columns:
        fig.add_trace(go.Scatter(
            x=sim_df["Day"], y=sim_df["ARIMA Forecast"],
            name="ARIMA", mode="lines+markers",
            line=dict(color="#457b9d", width=2.2),
            marker=dict(size=5, symbol="diamond"),
        ), row=1, col=1)

    # Blended demand
    fig.add_trace(go.Scatter(
        x=sim_df["Day"], y=sim_df["Projected Demand"],
        name="Blended Demand", mode="lines+markers",
        line=dict(color="#40916c", width=2.5),
        marker=dict(size=5),
    ), row=1, col=1)

    # Units sold
    fig.add_trace(go.Bar(
        x=sim_df["Day"], y=sim_df["Units Sold"],
        name="Units Sold",
        marker_color="rgba(82,183,136,0.30)",
        marker_line_color="#52b788", marker_line_width=1,
    ), row=1, col=1)

    # Remaining inventory
    fig.add_trace(go.Scatter(
        x=sim_df["Day"], y=sim_df["Remaining Inventory"],
        name="Remaining Stock", mode="lines",
        line=dict(color="#f4a261", width=2, dash="dot"),
    ), row=1, col=1)

    # Daily waste
    fig.add_trace(go.Bar(
        x=sim_df["Day"], y=sim_df["Daily Waste"],
        name="Daily Waste",
        marker_color="rgba(230,57,70,0.60)",
        marker_line_color="#e63946", marker_line_width=1,
    ), row=2, col=1)

    fig.update_layout(
        height=480,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis2=dict(title="Day", gridcolor=GRID_COLOR),
        yaxis=dict(title="Units", gridcolor=GRID_COLOR),
        yaxis2=dict(title="Waste", gridcolor=GRID_COLOR),
        **LAYOUT_DEFAULTS
    )

    st.plotly_chart(fig, use_container_width=True)


def render_cluster_chart(cluster_result: dict):
    """Render clustering visualization."""
    product_stats = cluster_result["product_stats"]
    cluster_summary = cluster_result["cluster_summary"]

    col1, col2 = st.columns([3, 2])

    with col1:
        # Scatter plot of products by demand characteristics
        fig = px.scatter(
            product_stats,
            x="demand_mean",
            y="demand_cv",
            color="cluster",
            hover_data=["product"],
            title="Product Clusters by Demand Pattern",
            labels={
                "demand_mean": "Average Demand",
                "demand_cv": "Demand Variability (CV%)",
                "cluster": "Cluster"
            },
            color_continuous_scale="Viridis",
        )
        fig.update_traces(marker=dict(size=10, opacity=0.7))
        fig.update_layout(height=320, **LAYOUT_DEFAULTS)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Cluster summary table
        display_df = cluster_summary[["cluster", "label", "product_count", "avg_demand"]].copy()
        display_df.columns = ["Cluster", "Profile", "Products", "Avg Demand"]
        display_df["Avg Demand"] = display_df["Avg Demand"].round(1)
        st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_comparison_chart(sim_df: pd.DataFrame):
    """Render ARIMA vs Factor model comparison."""
    arima_vals = sim_df["ARIMA Forecast"].dropna().values
    factor_vals = sim_df["Factor Forecast"].values[:len(arima_vals)]
    blend_vals = sim_df["Projected Demand"].values[:len(arima_vals)]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=sim_df["Day"][:len(arima_vals)], y=arima_vals,
        name="ARIMA", mode="lines+markers",
        line=dict(color="#457b9d", width=2.2),
        marker=dict(size=6, symbol="diamond"),
    ))

    fig.add_trace(go.Scatter(
        x=sim_df["Day"][:len(factor_vals)], y=factor_vals,
        name="Factor Model", mode="lines+markers",
        line=dict(color="#74c69d", width=2.2, dash="dash"),
        marker=dict(size=6),
    ))

    fig.add_trace(go.Scatter(
        x=sim_df["Day"][:len(blend_vals)], y=blend_vals,
        name="Blended", mode="lines+markers",
        line=dict(color="#40916c", width=2.8),
        marker=dict(size=7, symbol="circle-open"),
    ))

    fig.update_layout(
        height=260,
        title="Forecast Comparison",
        xaxis=dict(title="Day", gridcolor=GRID_COLOR),
        yaxis=dict(title="Units/Day", gridcolor=GRID_COLOR),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **LAYOUT_DEFAULTS
    )

    st.plotly_chart(fig, use_container_width=True)


def render_historical_chart(
    hist_df: pd.DataFrame,
    col_demand: str,
    col_date: str,
    projected_daily: float,
    base_demand: float,
    arima_avg: float = None
):
    """Render historical demand distribution chart."""
    plot_df = hist_df.copy().reset_index(drop=True)
    
    if col_date and col_date in plot_df.columns:
        plot_df[col_date] = pd.to_datetime(plot_df[col_date], errors="coerce")
        x_axis = col_date
    else:
        plot_df["Record"] = plot_df.index + 1
        x_axis = "Record"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=plot_df[x_axis], y=plot_df[col_demand],
        mode="lines", name="Historical Demand",
        line=dict(color="#2d6a4f", width=1.5),
        fill="tozeroy", fillcolor="rgba(64,145,108,0.10)",
    ))

    fig.add_hline(
        y=projected_daily, line_dash="dash",
        line_color="#e63946", line_width=2,
        annotation_text=f"Factor: {projected_daily}",
        annotation_position="top right",
    )

    if arima_avg:
        fig.add_hline(
            y=arima_avg, line_dash="dash",
            line_color="#457b9d", line_width=2,
            annotation_text=f"ARIMA: {arima_avg}",
            annotation_position="bottom right",
        )

    fig.add_hline(
        y=base_demand, line_dash="dot",
        line_color="#f4a261", line_width=1.5,
        annotation_text=f"Avg: {base_demand}",
        annotation_position="bottom left",
    )

    fig.update_layout(
        height=280,
        xaxis_title="Record",
        yaxis_title="Daily Demand",
        yaxis=dict(gridcolor=GRID_COLOR),
        **LAYOUT_DEFAULTS
    )

    st.plotly_chart(fig, use_container_width=True)


def render_sensitivity_chart(
    discount_range: list,
    sens_demands: list,
    sens_wastes: list,
    sens_arima: list,
    current_discount: int
):
    """Render discount sensitivity analysis chart."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=discount_range, y=sens_demands,
        name="Factor Demand", mode="lines+markers",
        line=dict(color="#40916c", width=2.2),
        marker=dict(size=6),
        yaxis="y1",
    ))

    if sens_arima:
        fig.add_trace(go.Scatter(
            x=discount_range, y=sens_arima,
            name="ARIMA Demand", mode="lines+markers",
            line=dict(color="#457b9d", width=2.2, dash="dot"),
            marker=dict(size=6, symbol="diamond"),
            yaxis="y1",
        ))

    fig.add_trace(go.Bar(
        x=discount_range, y=sens_wastes,
        name="Total Waste",
        marker_color="rgba(230,57,70,0.45)",
        yaxis="y2",
    ))

    fig.add_vline(
        x=current_discount, line_dash="dash", line_color="#1b4332",
        annotation_text=f"Current: {current_discount}%",
        annotation_position="top",
    )

    fig.update_layout(
        height=300,
        xaxis=dict(title="Discount (%)", gridcolor=GRID_COLOR),
        yaxis=dict(title="Daily Demand", side="left", gridcolor=GRID_COLOR),
        yaxis2=dict(title="Total Waste", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **LAYOUT_DEFAULTS
    )

    st.plotly_chart(fig, use_container_width=True)


def render_factor_breakdown(factors: dict, multipliers: dict, arima_available: bool):
    """Render demand factor breakdown."""
    col1, col2 = st.columns([3, 2])

    with col1:
        fig = go.Figure(go.Funnel(
            y=list(factors.keys()),
            x=list(factors.values()),
            textinfo="value+percent initial",
            marker=dict(color=["#74c69d", "#52b788", "#40916c", "#1b4332"]),
        ))
        fig.update_layout(
            height=240,
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", size=12),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        mult_labels = ["Weather", "Season", "Discount"]
        mult_vals = [
            multipliers["weather"],
            multipliers["season"],
            multipliers["discount"]
        ]
        colors = ["#52b788", "#40916c", "#2d6a4f"]

        if arima_available:
            mult_labels.append("ARIMA Weight")
            mult_vals.append(0.60)
            colors.append("#457b9d")

        fig = go.Figure(go.Bar(
            x=mult_labels, y=mult_vals,
            marker_color=colors,
            text=[f"{v:.2f}x" for v in mult_vals],
            textposition="outside",
        ))
        fig.add_hline(y=1.0, line_dash="dash", line_color="#9ca3af",
                      annotation_text="Baseline")
        fig.update_layout(
            height=240,
            yaxis=dict(title="Multiplier", gridcolor=GRID_COLOR),
            showlegend=False,
            **LAYOUT_DEFAULTS
        )
        st.plotly_chart(fig, use_container_width=True)
