import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

def run_random_forest(df, target_col, feature_cols=None, n_forecast=7, test_size=0.2, random_state=42):
    """
    Enhanced Random Forest forecasting using Lags, Weather, and Season.
    """
    data = df.copy()
    # 1. Feature Engineering: Lags (Keep these)
    for lag in range(1, 8):
        data[f'lag_{lag}'] = data[target_col].shift(lag)
    
    # 2. Encoding Categorical Data
    categorical_cols = ['weather_condition', 'seasonality', 'quality_grade'] 
    existing_cats = [c for c in categorical_cols if c in data.columns]
    if existing_cats:
        data = pd.get_dummies(data, columns=existing_cats)
    
    data = data.dropna()

    # 3. CRITICAL: Filter out non-numeric columns
    if feature_cols is None:
        # These are the columns that cause the ValueError
        forbidden_cols = [
            target_col, 'product_id', 'product_name', 'transaction_date', 
            'expiration_date', 'category', 'date'
        ]
        
        # We only want Lag columns and the dummy (0/1) columns we just created
        feature_cols = [
            col for col in data.columns 
            if col not in forbidden_cols and not data[col].dtype == 'object'
        ]

    X = data[feature_cols]
    y = data[target_col]
    
    if len(X) < 10:
        return None, "Insufficient data for Random Forest training."

    # Split (Shuffle=False is CRITICAL for time-series)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False)
    
    rf = RandomForestRegressor(n_estimators=200, random_state=random_state, n_jobs=-1)
    rf.fit(X_train, y_train)
    
    # Validation
    y_pred = rf.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    
    # 3. Recursive Forecasting
    # We take the most recent state to start the forecast
    current_features = X.iloc[-1:].copy()
    future_preds = []
    
    for _ in range(n_forecast):
        pred = rf.predict(current_features)[0]
        future_preds.append(max(0, pred)) # Demand can't be negative
        
        # Update Lags for the next iteration
        # We slide the lag values: lag_2 becomes lag_1, and our new 'pred' becomes the new lag_1
        for i in range(7, 1, -1):
            if f'lag_{i}' in current_features.columns and f'lag_{i-1}' in current_features.columns:
                current_features[f'lag_{i}'] = current_features[f'lag_{i-1}'].values
        
        if 'lag_1' in current_features.columns:
            current_features['lag_1'] = pred

    return {
        'model': rf, 
        'preds': np.array(future_preds), 
        'mae': mae,
        'feature_importance': dict(zip(feature_cols, rf.feature_importances_))
    }