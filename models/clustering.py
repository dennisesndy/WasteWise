import numpy as np
import pandas as pd
import streamlit as st

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@st.cache_data(show_spinner=False)
def run_clustering_analysis(
    df: pd.DataFrame,
    col_product: str,
    col_demand: str,
    col_season: str = None,
    col_weather: str = None,
    n_clusters: int = 4
) -> tuple[dict | None, str | None]:
    """
    Perform K-means clustering on product demand patterns.
    
    Groups products by their demand characteristics to identify
    similar inventory management strategies.
    """
    if not SKLEARN_AVAILABLE:
        return None, "scikit-learn not installed"

    if not col_product or not col_demand:
        return None, "Required columns not found"

    # Aggregate features per product
    agg_dict = {col_demand: ["mean", "std", "min", "max", "count"]}
    
    product_stats = df.groupby(col_product).agg(agg_dict).reset_index()
    product_stats.columns = ["product", "demand_mean", "demand_std", 
                             "demand_min", "demand_max", "record_count"]
    
    # Calculate coefficient of variation
    product_stats["demand_cv"] = (
        product_stats["demand_std"] / product_stats["demand_mean"] * 100
    ).fillna(0)
    
    # Add seasonal variance if available
    if col_season:
        season_var = df.groupby(col_product)[col_demand].apply(
            lambda x: x.std() / x.mean() if x.mean() > 0 else 0
        ).reset_index()
        season_var.columns = ["product", "seasonal_var"]
        product_stats = product_stats.merge(season_var, on="product", how="left")
    
    # Prepare features for clustering
    feature_cols = ["demand_mean", "demand_std", "demand_cv"]
    if "seasonal_var" in product_stats.columns:
        feature_cols.append("seasonal_var")
    
    X = product_stats[feature_cols].fillna(0).values
    
    if len(X) < n_clusters:
        return None, f"Not enough products ({len(X)}) for {n_clusters} clusters"

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Fit K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    product_stats["cluster"] = kmeans.fit_predict(X_scaled)

    # Calculate silhouette score
    silhouette = silhouette_score(X_scaled, product_stats["cluster"])

    # Generate cluster summaries
    cluster_summary = product_stats.groupby("cluster").agg({
        "demand_mean": "mean",
        "demand_cv": "mean",
        "product": "count"
    }).reset_index()
    cluster_summary.columns = ["cluster", "avg_demand", "avg_volatility", "product_count"]
    
    # Assign cluster labels
    cluster_labels = []
    for _, row in cluster_summary.iterrows():
        if row["avg_demand"] > product_stats["demand_mean"].median():
            demand_level = "High-Demand"
        else:
            demand_level = "Low-Demand"
        
        if row["avg_volatility"] > product_stats["demand_cv"].median():
            volatility = "Variable"
        else:
            volatility = "Stable"
        
        cluster_labels.append(f"{demand_level}, {volatility}")
    
    cluster_summary["label"] = cluster_labels

    return {
        "product_stats": product_stats,
        "cluster_summary": cluster_summary,
        "n_clusters": n_clusters,
        "silhouette_score": round(silhouette, 3),
        "feature_cols": feature_cols,
        "centroids": kmeans.cluster_centers_,
    }, None


def get_product_cluster(clustering_result: dict, product_name: str) -> dict | None:
    """Get cluster information for a specific product."""
    if not clustering_result:
        return None
    
    product_stats = clustering_result["product_stats"]
    product_row = product_stats[product_stats["product"] == product_name]
    
    if product_row.empty:
        return None
    
    cluster_id = product_row["cluster"].values[0]
    cluster_summary = clustering_result["cluster_summary"]
    cluster_info = cluster_summary[cluster_summary["cluster"] == cluster_id]
    
    return {
        "cluster_id": int(cluster_id),
        "cluster_label": cluster_info["label"].values[0],
        "demand_mean": round(product_row["demand_mean"].values[0], 1),
        "demand_cv": round(product_row["demand_cv"].values[0], 1),
        "products_in_cluster": int(cluster_info["product_count"].values[0]),
    }
