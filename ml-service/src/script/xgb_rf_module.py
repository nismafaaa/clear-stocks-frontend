"""
time_series_module.py

A collection of functions for time series preprocessing, feature engineering,
model training, and hyperparameter optimization using Optuna.

HOW TO RUN OPTUNA HYPERPARAMETER SEARCH

The functions `xgb_objective(trial, X_train, X_test, y_train, y_test)` and
`rf_objective(trial, X_train, X_test, y_train, y_test)` require both an
Optuna `trial` object and the training/testing datasets as arguments.
Optuna itself expects an objective of signature:

    def objective(trial):
        …

To bridge this without modifying any function signatures in this file,
use `functools.partial` in your external script to “freeze” the data arguments,
producing a callable that only takes `trial`.  
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import optuna

def train_test_split(data: pd.DataFrame, split_date: pd.Timestamp):
    """
    Split a time-indexed DataFrame into training and testing sets.

    Args:
        data (pd.DataFrame): Time-series data with a DatetimeIndex.
        split_date (pd.Timestamp): The cutoff date for splitting.

    Returns:
        train (pd.DataFrame), test (pd.DataFrame)
    """
    train = data[data.index < split_date]
    test = data[data.index >= split_date]
    return train, test

def seasonalDecompose(y: pd.Series, period: int, is_plot: bool = True):
    """
    Perform STL decomposition on a time series.

    Args:
        y (pd.Series): Time series to decompose.
        period (int): Seasonal period.
        is_plot (bool): Whether to plot the decomposition result.

    Returns:
        result: The fitted STL result object.
    """
    stl = STL(y, period=period)
    result = stl.fit()
    if is_plot:
        fig = result.plot()
        fig.set_size_inches(13, 6)
        for axes in fig.axes:
            axes.grid(True)
        plt.show()
    return result

def feature_engineering(data: pd.DataFrame, label: str = None):
    """
    Create time series features including STL components, lags, rolling stats, and datetime features.

    Args:
        data (pd.DataFrame): Input data with a DatetimeIndex.
        label (str): Name of the target column. If provided, returns (X, y).

    Returns:
        X (pd.DataFrame) or (X, y) tuple if label is specified.
    """
    # Decompose the first column of data
    sdcompose_result = seasonalDecompose(data.iloc[:, 0], period=5, is_plot=False)
    df = pd.concat(
        [data,
         sdcompose_result.trend.rename('trend'),
         sdcompose_result.seasonal.rename('seasonal'),
         sdcompose_result.resid.rename('resid')
        ], axis=1)
    # Basic lag and moving average
    df['lag'] = df.iloc[:, 0].diff()
    df['ma'] = df.iloc[:, 0].rolling(window=2).mean()
    df = df.fillna(0)
    # Datetime features
    df['date'] = df.index
    df['hour'] = df['date'].dt.hour
    df['dayofweek'] = df['date'].dt.dayofweek
    df['quarter'] = df['date'].dt.quarter
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['dayofyear'] = df['date'].dt.dayofyear
    df['dayofmonth'] = df['date'].dt.day

    feature_cols = [col for col in df.columns if col not in ([label] if label else []) + ['date']]
    X = df[feature_cols]
    if label:
        y = df[label]
        return X, y
    return X

def root_mean_squared_error(y_true, y_pred):
    """Compute RMSE between true and predicted values."""
    return np.sqrt(mean_squared_error(y_true, y_pred))

def train_eval_ml_model(model, X_train, X_test, y_train, y_test):
    """
    Train model, predict on test set, and return RMSE.

    Args:
        model: A scikit‑learn compatible regressor with fit/predict.
        X_train, X_test, y_train, y_test: Training and testing data.

    Returns:
        rmse (float)
    """
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    return root_mean_squared_error(y_test, y_pred)

def optuna_search(objective, n_trials: int, direction: str = "minimize"):
    """
    Run an Optuna hyperparameter search.

    Args:
        objective: Objective function for Optuna.
        n_trials (int): Number of trials.
        direction (str): "minimize" or "maximize".

    Returns:
        best_params (dict)
    """
    study = optuna.create_study(direction=direction)
    study.optimize(objective, n_trials=n_trials)
    print("Best trial:")
    trial = study.best_trial
    print(f"  Value: {trial.value}")
    print("  Params:")
    for key, val in trial.params.items():
        print(f"    {key}: {val}")
    return trial.params

def xgb_objective(trial, X_train, X_test, y_train, y_test):
    """
    Optuna objective for XGBRegressor.
    """
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 300, 1500),
        'max_depth': trial.suggest_int('max_depth', 4, 15),
        'learning_rate': trial.suggest_loguniform('learning_rate', 0.0005, 0.2),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 20),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'reg_alpha': trial.suggest_loguniform('reg_alpha', 1e-5, 100.0),
        'reg_lambda': trial.suggest_loguniform('reg_lambda', 1e-5, 100.0),
        'random_state': 42,
        'objective': 'reg:squarederror'
    }
    model = XGBRegressor(**params)
    return train_eval_ml_model(model, X_train, X_test, y_train, y_test)

def rf_objective(trial, X_train, X_test, y_train, y_test):
    """
    Optuna objective for RandomForestRegressor.
    """
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'max_depth': trial.suggest_int('max_depth', 5, 50),
        'min_samples_split': trial.suggest_int('min_samples_split', 2, 10),
        'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 20),
        'bootstrap': trial.suggest_categorical('bootstrap', [True, False])
    }
    model = RandomForestRegressor(**params)
    return train_eval_ml_model(model, X_train, X_test, y_train, y_test)
