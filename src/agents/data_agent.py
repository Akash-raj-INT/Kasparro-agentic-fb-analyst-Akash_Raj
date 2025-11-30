import os
import json
from typing import Dict, Any

import polars as pl

from src.agents.base import BaseAgent
from src.utils.logger import time_block, end_block, log_event
from src.utils.retry import retry
from src.utils.schema_utils import validate_schema


class DataAgent(BaseAgent):
    name = "data_agent"

    def _get_data_path(self) -> str:
        paths = self.config.get("paths", {})
        if self.config.get("use_sample_data", True):
            return paths.get("sample_csv", "data/sample_fb_ads.csv")
        env_var = paths.get("data_csv_env", "DATA_CSV")
        return os.environ.get(env_var, "")

    @retry(agent="data_agent", action="load_and_parse_csv", retries=3, delay=1)
    def _load_csv(self, csv_path: str) -> pl.DataFrame:
        return pl.read_csv(csv_path, try_parse_dates=True)

    def run(self, **kwargs) -> Dict[str, Any]:
        start = time_block(self.name, "run")

        csv_path = self._get_data_path()
        if not csv_path or not os.path.exists(csv_path):
            log_event(self.name, "csv_missing", "error", {"path": csv_path})
            raise FileNotFoundError(f"CSV not found at: {csv_path}")

        # Load file
        df = self._load_csv(csv_path)

        # Validate schema (P1 requirement)
        validate_schema(df, agent=self.name)

        # Ensure date column
        if "date" in df.columns and df.schema["date"] == pl.Utf8:
            df = df.with_columns(
                pl.col("date").str.strptime(pl.Date, strict=False)
            )

        # Cast numeric columns
        numeric_casts = {
            "ctr": pl.Float64,
            "roas": pl.Float64,
            "spend": pl.Float64,
            "impressions": pl.Float64,
            "clicks": pl.Float64,
            "purchases": pl.Float64,
            "revenue": pl.Float64,
        }

        for col, dtype in numeric_casts.items():
            if col in df.columns:
                df = df.with_columns(pl.col(col).cast(dtype))

        # Aggregate summaries
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

        low_ctr_threshold = self.config.get("metrics", {}).get("low_ctr_threshold", 0.01)
        low_ctr_ads = df.filter(pl.col("ctr") < low_ctr_threshold)

        # End logging
        end_block(self.name, "run", start, extra={
            "rows_loaded": len(df),
            "rows_low_ctr": len(low_ctr_ads)
        })

        return {
            "raw_df": df,
            "by_date": by_date,
            "by_campaign": by_campaign,
            "low_ctr_ads": low_ctr_ads,
        }
