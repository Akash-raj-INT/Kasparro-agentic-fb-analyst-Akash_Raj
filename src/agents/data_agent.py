import os
from typing import Any, Dict

import polars as pl

from .base import BaseAgent


class DataAgent(BaseAgent):
    name = "data"

    def _get_data_path(self) -> str:
        paths = self.config.get("paths", {})
        if self.config.get("use_sample_data", True):
            return paths.get("sample_csv", "data/sample_fb_ads.csv")
        env_var = paths.get("data_csv_env", "DATA_CSV")
        return os.environ.get(env_var, "")

    def run(self, **kwargs) -> Dict[str, Any]:
        csv_path = self._get_data_path()
        if not csv_path or not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV not found at {csv_path}")

        # Read CSV with polars
        df = pl.read_csv(csv_path, try_parse_dates=True)

        # Ensure date column is proper Date/Datetime
        if "date" in df.columns and df.schema["date"] == pl.Utf8:
            df = df.with_columns(
                pl.col("date").str.strptime(pl.Date, strict=False)
            )

        # Cast numeric columns
        num_cols_float = ["ctr", "roas"]
        num_cols_other = ["spend", "impressions", "clicks", "purchases", "revenue"]

        for col in num_cols_float:
            if col in df.columns:
                df = df.with_columns(pl.col(col).cast(pl.Float64))

        for col in num_cols_other:
            if col in df.columns:
                df = df.with_columns(pl.col(col).cast(pl.Float64))

        # Time-series summary by date
        by_date = (
            df.group_by("date")
            .agg(
                spend=pl.col("spend").sum(),
                impressions=pl.col("impressions").sum(),
                clicks=pl.col("clicks").sum(),
                ctr=pl.col("ctr").mean(),
                purchases=pl.col("purchases").sum(),
                revenue=pl.col("revenue").sum(),
                roas=pl.col("roas").mean(),
            )
            .sort("date")
        )

        # Campaign-level summary
        by_campaign = (
            df.group_by("campaign_name")
            .agg(
                spend=pl.col("spend").sum(),
                impressions=pl.col("impressions").sum(),
                clicks=pl.col("clicks").sum(),
                ctr=pl.col("ctr").mean(),
                purchases=pl.col("purchases").sum(),
                revenue=pl.col("revenue").sum(),
                roas=pl.col("roas").mean(),
            )
        )

        # Low CTR ads
        low_ctr_threshold = (
            self.config.get("metrics", {}).get("low_ctr_threshold", 0.01)
        )
        low_ctr_ads = df.filter(pl.col("ctr") < low_ctr_threshold)

        return {
            "raw_df": df,                 # polars.DataFrame
            "by_date": by_date,           # polars.DataFrame
            "by_campaign": by_campaign,   # polars.DataFrame
            "low_ctr_ads": low_ctr_ads,   # polars.DataFrame
        }
