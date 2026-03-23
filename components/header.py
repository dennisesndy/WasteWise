"""
Header component.
"""

import streamlit as st


def render_header():
    """Render the main application header."""
    st.markdown("""
        <div class="main-header">
            <h1>🌿 WasteWise</h1>
            <p>Intelligent Demand Forecasting for Perishable Goods</p>
        </div>
    """, unsafe_allow_html=True)


def render_product_badge(product_name: str):
    """Render the product selection badge."""
    st.markdown(
        f'<div class="product-badge">📦 {product_name}</div>',
        unsafe_allow_html=True
    )


def render_section_title(icon: str, title: str):
    """Render a section title."""
    st.markdown(
        f'<div class="section-title">{icon} {title}</div>',
        unsafe_allow_html=True
    )
