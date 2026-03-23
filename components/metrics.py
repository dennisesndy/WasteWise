"""
Metric card components.
"""

import streamlit as st


def render_metric_card(
    label: str,
    value: str,
    sub: str = "",
    card_class: str = "safe"
):
    """Render a single metric card."""
    st.markdown(f"""
        <div class="metric-card {card_class}">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div class="sub">{sub}</div>
        </div>
    """, unsafe_allow_html=True)


def render_metrics_row(metrics: list[dict], columns: int = None):
    """
    Render a row of metric cards.
    
    Args:
        metrics: List of metric dicts with keys: label, value, sub, card_class
        columns: Number of columns (default: len(metrics))
    """
    if columns is None:
        columns = len(metrics)
    
    cols = st.columns(columns)
    for i, metric in enumerate(metrics):
        with cols[i % columns]:
            render_metric_card(
                label=metric.get("label", ""),
                value=str(metric.get("value", "")),
                sub=metric.get("sub", ""),
                card_class=metric.get("card_class", "safe")
            )


def render_insight_box(message: str, box_type: str = "info"):
    """
    Render an insight box.
    
    Args:
        message: The message to display
        box_type: One of 'info', 'warn', 'cluster'
    """
    css_class = {
        "info": "info",
        "warn": "warn",
        "warning": "warn",
        "cluster": "cluster",
    }.get(box_type, "")
    
    st.markdown(
        f'<div class="insight-box {css_class}">{message}</div>',
        unsafe_allow_html=True
    )
