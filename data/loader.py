"""
Data loading and preprocessing utilities.
"""

import pandas as pd
import streamlit as st
from config.settings import COLUMN_CANDIDATES


def find_column(df: pd.DataFrame, candidates: list) -> str | None:
    """Find the first matching column name from candidates."""
    for col in candidates:
        if col in df.columns:
            return col
    return None


def get_column_mapping(df: pd.DataFrame) -> dict:
    """Map standard column names to actual column names in the dataframe."""
    return {
        key: find_column(df, candidates)
        for key, candidates in COLUMN_CANDIDATES.items()
    }


@st.cache_data
def load_data(filepath: str = "perishable_goods_demand_forecasting_data.csv") -> pd.DataFrame:
    """Load and preprocess the dataset."""
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def get_product_list(df: pd.DataFrame, col_product: str) -> list:
    """Get sorted list of unique products."""
    if col_product:
        return sorted(df[col_product].dropna().unique())
    return []


def get_unique_values(df: pd.DataFrame, column: str, default: list = None) -> list:
    """Get sorted unique values from a column."""
    if column and column in df.columns:
        return sorted(df[column].dropna().unique())
    return default or []
