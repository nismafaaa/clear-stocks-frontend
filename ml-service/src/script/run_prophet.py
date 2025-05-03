import os
import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt
from datetime import datetime

# Model
# from prophet import Prophet
from script.prophet_class import MyProphet
from prophet.diagnostics import cross_validation, performance_metrics
from prophet.serialize import model_to_json, model_from_json


class ProphetModel:
    @classmethod
    def _init(self, data_loc):
        try:
            self.data = pd.read_csv(data_loc, index_col=[0], parse_dates=[0])
            self.data.index.name = "Date"
            print(
                f"Data loaded. Shape: {self.data.shape}, Last date: {self.data.index.max()}"
            )
            if not isinstance(self.data.index, pd.DatetimeIndex):
                print(
                    "Warning: Index was not parsed as DatetimeIndex. Attempting conversion."
                )
                self.data.index = pd.to_datetime(self.data.index)
            self.data.sort_index(inplace=True)  # Ensure data is sorted by date
        except FileNotFoundError:
            print(f"Error: Data file not found at {data_loc}")
            # Init empty if error in loading data
            self.data = pd.DataFrame()
        except Exception as e:
            print(f"Error loading or parsing data from {data_loc}: {e}")
            # Init empty if error in loading data
            self.data = pd.DataFrame()

    def _get_prepared_data(data, column):
        result = data.copy()
        result["date"] = result.index
        result = result[["date", column]]
        result.rename(columns={"date": "ds", column: "y"}, inplace=True)

        return result

    def fit_best_model(self, initial, period, horizon, column="Close"):
        param_grid = {
            "changepoint_prior_scale": [0.001, 0.01, 0.1, 0.5],
            "seasonality_prior_scale": [0.01, 0.1, 1.0, 10.0],
            "seasonality_mode": ["additive", "multiplicative"],
        }

        # Generate all combinations of parameters
        all_params = [
            dict(zip(param_grid.keys(), v))
            for v in itertools.product(*param_grid.values())
        ]
        # RMSE default
        rmses = []

        # Use cross validation to evaluate all parameters
        for params in all_params:
            # Fit model with given params
            m = MyProphet(**params).fit(
                ProphetModel._get_prepared_data(data=self.data, column=column)
            )
            df_cv = cross_validation(
                m,
                initial=initial,
                period=period,
                horizon=horizon,
                parallel="threads",
            )
            df_p = performance_metrics(df_cv, rolling_window=1)
            rmses.append(df_p["rmse"].values[0])

        # Find the best parameters
        best_params = all_params[np.argmin(rmses)]

        return best_params

    def forecast_best(
        self,
        best_params,
        last_date,
        forecast_length=5,
        column="Close",
        plot_history_days=20,
    ):
        # Determine the last date in your historical data
        ld = pd.to_datetime(pd.Series([last_date]))
        yestd = ld.max()

        # Calculate the first day of the forecast period
        # This is the day *after* the last historical date or yesterday,
        # i.e. "today"
        start_forecast = yestd + pd.Timedelta(days=1)

        # Generate 'forecast_length' business days starting from 'start_forecast'
        # 'B' frequency automatically skips weekends (Saturday, Sunday)
        future_dates = pd.date_range(
            start=start_forecast, periods=forecast_length, freq="B"
        )

        fds = pd.DataFrame({"ds": future_dates})

        best_model = MyProphet(
            changepoint_prior_scale=best_params.get("changepoint_prior_scale", 0.05),
            seasonality_prior_scale=best_params.get("seasonality_prior_scale", 10.0),
            seasonality_mode=best_params.get("seasonality_mode", "additive"),
        )

        print(
            f"Fitting Prophet model on data up to {self.data.index[-1].strftime('%Y-%m-%d')}..."
        )
        best_model.fit(ProphetModel._get_prepared_data(data=self.data, column=column))

        # Generate timestamp to name results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Define output directory and ensure it exists
        output_dir = os.path.join("src", "public", "prophet", "results")
        os.makedirs(output_dir, exist_ok=True)
        print("Saving model...")

        try:
            # Create timestamped filename
            file_name = f"model_{timestamp}.json"
            file_path = os.path.join(output_dir, file_name)
            with open(file_path, "w") as fout:
                fout.write(model_to_json(best_model))  # Save model
        except:
            print("Failed saving model.")

        print(
            f"Predicting next {forecast_length} work days starting after {yestd.strftime('%Y-%m-%d')}..."
        )
        forecast = best_model.predict(fds)

        # Generate and save plot
        print("Generating forecast plot...")
        fig, ax = plt.subplots(figsize=(10, 4))

        best_model.plot(forecast, uncertainty=True, ax=ax)

        # Select the last N historical days for plotting actuals
        # Ensure plot_history_days isn't larger than available data
        actual_plot_days = min(plot_history_days, len(self.data))
        last_n_days_data = self.data.tail(actual_plot_days)

        # Plot only the selected recent actual data using line plot
        # Use a distinct color/marker and add a label.
        if not last_n_days_data.empty:
            ax.plot(
                last_n_days_data.index,
                last_n_days_data[column],
                color="orange",
                label=f"Actual (Last {actual_plot_days} Days)",
                zorder=5,
            )

        # Start plotting from last n days
        start_plot_date = last_n_days_data.index.min()
        if last_n_days_data.empty:
            start_plot_date = forecast["ds"].min() - pd.Timedelta(days=forecast_length)

        # Add padding to look cleaner
        end_plot_date = forecast["ds"].max() + pd.Timedelta(days=2)
        ax.set_xlim(start_plot_date, end_plot_date)

        ax.set_title(f"Forecast for next {forecast_length} work days (Recent History)")
        ax.set_xlabel("Date")
        ax.set_ylabel(f"Predicted {column} Price")
        ax.legend()

        plt.tight_layout()

        # Create timestamped filename
        file_name = f"forecast_{timestamp}.png"
        file_path = os.path.join(output_dir, file_name)

        # Save the figure
        try:
            fig.savefig(file_path)
            print(f"Forecast plot saved to: {file_path}")
        except Exception as e:
            print(f"Error saving plot to {file_path}: {e}")

        plt.close(fig)
        forecast_results = forecast["yhat"].to_list()

        return forecast_results , fds

    def forecast_with_existing_model(
        self,
        model_loc,
        last_date,
        forecast_length=5,
        column="Close",
        plot_history_days=20,
    ):
        # Determine the last date in your historical data
        ld = pd.to_datetime(pd.Series([last_date]))
        yestd = ld.max()

        # Calculate the first day of the forecast period
        # This is the day *after* the last historical date or yesterday,
        # i.e. "today"
        start_forecast = yestd + pd.Timedelta(days=1)

        # Generate 'forecast_length' business days starting from 'start_forecast'
        # 'B' frequency automatically skips weekends (Saturday, Sunday)
        future_dates = pd.date_range(
            start=start_forecast, periods=forecast_length, freq="B"
        )

        fds = pd.DataFrame({"ds": future_dates})

        best_model = None
        try:
            with open(model_loc, "r") as fin:
                best_model = model_from_json(fin.read())  # Load model
        except:
            print("Failed to load model. Aborting forecast...")
            return 0

        # Generate timestamp to name results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Define output directory and ensure it exists
        output_dir = os.path.join("src", "public", "prophet", "results")
        os.makedirs(output_dir, exist_ok=True)

        print(
            f"Predicting next {forecast_length} work days starting after {yestd.strftime('%Y-%m-%d')}..."
        )
        forecast = best_model.predict(fds)

        # Generate and save plot
        print("Generating forecast plot...")
        fig, ax = plt.subplots(figsize=(10, 4))

        best_model.plot(forecast, uncertainty=True, ax=ax)

        # Select the last N historical days for plotting actuals
        # Ensure plot_history_days isn't larger than available data
        actual_plot_days = min(plot_history_days, len(self.data))
        last_n_days_data = self.data.tail(actual_plot_days)

        # Plot only the selected recent actual data using line plot
        # Use a distinct color/marker and add a label.
        if not last_n_days_data.empty:
            ax.plot(
                last_n_days_data.index,
                last_n_days_data[column],
                color="orange",
                label=f"Actual (Last {actual_plot_days} Days)",
                zorder=5,
            )

        # Start plotting from last n days
        start_plot_date = last_n_days_data.index.min()
        if last_n_days_data.empty:
            start_plot_date = forecast["ds"].min() - pd.Timedelta(days=forecast_length)

        # Add padding to look cleaner
        end_plot_date = forecast["ds"].max() + pd.Timedelta(days=2)
        ax.set_xlim(start_plot_date, end_plot_date)

        ax.set_title(f"Forecast for next {forecast_length} work days (Recent History)")
        ax.set_xlabel("Date")
        ax.set_ylabel(f"Predicted {column} Price")
        ax.legend()

        plt.tight_layout()

        # Create timestamped filename
        file_name = f"forecast_{timestamp}.png"
        file_path = os.path.join(output_dir, file_name)

        # Save the figure
        try:
            fig.savefig(file_path)
            print(f"Forecast plot saved to: {file_path}")
        except Exception as e:
            print(f"Error saving plot to {file_path}: {e}")

        plt.close(fig)

        return 1


def run(data_loc, initial, period, horizon, forecast_length=5, plot_history_days=20):
    data_file = data_loc
    pm = ProphetModel()
    pm._init(data_file)

    if not pm.data.empty:
        best_params = pm.fit_best_model(initial=initial, period=period, horizon=horizon)

        # Snippet below for debug purposes to skip cv
        # best_params = {
        #     "changepoint_prior_scale": 0.1,
        #     "seasonality_prior_scale": 10.0,
        #     "holidays_prior_scale": 0.01,
        #     "seasonality_mode": "additive",
        # }

        # Determine the actual last date from the loaded data
        actual_last_date = pm.data.index[-1].strftime("%Y-%m-%d")
        print(f"\nUsing actual last date from data: {actual_last_date}")

        forecast_values, dates = pm.forecast_best(
            best_params,
            last_date=actual_last_date,
            forecast_length=forecast_length,
            plot_history_days=plot_history_days,
        )

        print("\nForecast Results (yhat values)")
        results_df = pd.DataFrame({"Date": dates["ds"], "Forecast": forecast_values})
        print(results_df.to_string(index=False))
    else:
        print("\nForecast skipped due to data loading issues.")


def run_model_exists(data_loc, model_loc, forecast_length=5, plot_history_days=20):
    data_file = data_loc
    pm = ProphetModel()
    pm._init(data_file)

    if not pm.data.empty:
        actual_last_date = pm.data.index[-1].strftime("%Y-%m-%d")

        pm.forecast_with_existing_model(
            model_loc=model_loc,
            last_date=actual_last_date,
            forecast_length=forecast_length,
            plot_history_days=plot_history_days,
        )
    else:
        print("\nForecast skipped due to data loading issues.")


if __name__ == "__main__":
    # run("data/aapl_stock_price.csv", "2275 days", "252 days", "1 days", 5, 20)
    # run_model_exists(
    #     "data/aapl_stock_price.csv",
    #     "src/public/prophet/results/model_20250414_122037.json",
    # )
    pm = ProphetModel()
    pm._init("../data-service/data/aapl_stock_price.csv")
    temp, _ = pm.forecast_best(
        {
            'holidays': None,
            'changepoint_prior_scale': 0.1,
            'seasonality_prior_scale': 10,
            'seasonality_mode': 'additive',
            'period': 252
        },
        '2025-05-01',
        3
    )
    print(temp)

