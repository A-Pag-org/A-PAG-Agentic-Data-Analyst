from __future__ import annotations

import io
import base64
from typing import Any, Dict, Optional, Tuple, List

import numpy as np
import pandas as pd

# Lazy/optional import: avoid failing at module import time
try:
    from prophet import Prophet  # type: ignore
except Exception:  # pragma: no cover - optional dependency may be missing in some deployments
    Prophet = None  # type: ignore


class ForecastingService:
    def __init__(
        self,
        *,
        model: Optional[Prophet] = None,
        yearly_seasonality: str | bool = "auto",
        weekly_seasonality: str | bool = "auto",
        daily_seasonality: str | bool = "auto",
        seasonality_mode: str = "additive",
        changepoint_prior_scale: float = 0.05,
    ):
        if model is not None:
            self.prophet_model: Prophet = model
            return

        # Ensure Prophet is available before constructing the default model
        if Prophet is None:  # type: ignore[truthy-bool]
            raise RuntimeError(
                "Prophet is not available. Install 'prophet' to enable forecasting endpoints."
            )

        self.prophet_model: Prophet = Prophet(  # type: ignore[call-arg]
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality,
            seasonality_mode=seasonality_mode,
            changepoint_prior_scale=changepoint_prior_scale,
        )

    def _infer_datetime_column(self, df: pd.DataFrame) -> Optional[str]:
        if df.empty:
            return None

        preferred_names = {"ds", "date", "datetime", "timestamp", "time"}
        for name in df.columns:
            if name.lower() in preferred_names:
                try:
                    _ = pd.to_datetime(df[name], errors="raise", utc=False)
                    return name
                except Exception:
                    continue

        # Try dtype-based detection
        for name, dtype in df.dtypes.items():
            if np.issubdtype(dtype, np.datetime64):
                return name

        # Heuristic: pick the first column that largely parses to datetime
        best_name: Optional[str] = None
        best_ratio: float = 0.0
        for name in df.columns:
            try:
                parsed = pd.to_datetime(df[name], errors="coerce", utc=False)
                ratio = float(parsed.notna().mean())
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_name = name
            except Exception:
                continue
        return best_name if (best_ratio >= 0.8) else None

    def prepare_prophet_data(
        self,
        data: pd.DataFrame,
        target_column: str,
        *,
        date_column: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, str]:
        if target_column not in data.columns:
            raise ValueError(f"target_column '{target_column}' not found in provided data")

        resolved_date_col = date_column or self._infer_datetime_column(data)
        if not resolved_date_col or resolved_date_col not in data.columns:
            raise ValueError(
                "Could not infer a datetime column. Please specify 'date_column' explicitly."
            )

        df = data.copy()
        df = df[[resolved_date_col, target_column]].rename(
            columns={resolved_date_col: "ds", target_column: "y"}
        )
        df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
        df["y"] = pd.to_numeric(df["y"], errors="coerce")
        df = df.dropna(subset=["ds", "y"]).sort_values("ds")

        if df.empty:
            raise ValueError("No valid rows after parsing dates and target values.")

        return df, resolved_date_col

    async def generate_forecast(
        self,
        data: pd.DataFrame,
        *,
        target_column: str,
        date_column: Optional[str] = None,
        periods: int = 30,
        freq: str = "D",
        include_history: bool = True,
    ) -> Dict[str, Any]:
        prophet_data, resolved_date_col = self.prepare_prophet_data(
            data, target_column, date_column=date_column
        )

        # Fit model
        self.prophet_model.fit(prophet_data)

        # Forecast future
        future_df = self.prophet_model.make_future_dataframe(
            periods=periods, freq=freq, include_history=include_history
        )
        forecast_df = self.prophet_model.predict(future_df)

        # Separate history vs future for clarity
        last_train_date = prophet_data["ds"].max()
        history_pred = forecast_df[forecast_df["ds"] <= last_train_date]
        future_pred = forecast_df[forecast_df["ds"] > last_train_date]

        # Compute training metrics
        metrics = self._calculate_forecast_metrics(history_pred, prophet_data)

        # Generate plots as base64 (if matplotlib available)
        plot_png_b64, components_png_b64 = self._render_plots_base64(forecast_df)

        # Compact columns for client consumption
        def to_records(df: pd.DataFrame, cols: List[str]) -> List[Dict[str, Any]]:
            safe = df.copy()
            if "ds" in cols and np.issubdtype(safe["ds"].dtype, np.datetime64):
                safe["ds"] = safe["ds"].dt.strftime("%Y-%m-%dT%H:%M:%S")
            return safe[cols].to_dict(orient="records")

        history_rows = to_records(
            history_pred.merge(prophet_data[["ds", "y"]], on="ds", how="left"),
            ["ds", "y", "yhat", "yhat_lower", "yhat_upper"],
        )
        future_rows = to_records(
            future_pred, ["ds", "yhat", "yhat_lower", "yhat_upper"]
        )

        return {
            "metadata": {
                "date_column_used": resolved_date_col,
                "target_column": target_column,
                "freq": freq,
                "periods": periods,
                "train_rows": int(len(prophet_data)),
            },
            "history": history_rows,
            "forecast": future_rows,
            "metrics": metrics,
            "plot_png_base64": plot_png_b64,
            "components_png_base64": components_png_b64,
        }

    def _calculate_forecast_metrics(
        self, history_pred: pd.DataFrame, train_df: pd.DataFrame
    ) -> Dict[str, float]:
        merged = history_pred.merge(train_df[["ds", "y"]], on="ds", how="left")
        merged = merged.dropna(subset=["y", "yhat"])  # ensure valid points
        if merged.empty:
            return {"rmse": float("nan"), "mae": float("nan"), "mape": float("nan")}

        y_true = merged["y"].astype(float).to_numpy()
        y_pred = merged["yhat"].astype(float).to_numpy()
        err = y_pred - y_true

        mse = float(np.mean(err ** 2))
        rmse = float(np.sqrt(mse))
        mae = float(np.mean(np.abs(err)))
        denom = np.where(np.abs(y_true) < 1e-12, np.nan, np.abs(y_true))
        mape = float(np.nanmean(np.abs(err) / denom) * 100.0)
        if np.isnan(mape):
            mape = float("nan")
        return {"rmse": rmse, "mae": mae, "mape": mape}

    def _render_plots_base64(self, forecast_df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
        try:
            import matplotlib.pyplot as plt  # type: ignore
        except Exception:
            return None, None

        def fig_to_base64(fig) -> str:
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            plt.close(fig)
            buf.seek(0)
            return base64.b64encode(buf.read()).decode("ascii")

        fig_main = self.prophet_model.plot(forecast_df)
        main_b64 = fig_to_base64(fig_main)
        try:
            fig_components = self.prophet_model.plot_components(forecast_df)
            comp_b64 = fig_to_base64(fig_components)
        except Exception:
            comp_b64 = None
        return main_b64, comp_b64
