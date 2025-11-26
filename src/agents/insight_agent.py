from typing import Any, Dict, List

import polars as pl

from .base import BaseAgent


class InsightAgent(BaseAgent):
    name = "insight"

    def run(
        self,
        data_summary: Dict[str, Any],
        query: str,
        **kwargs,
    ) -> Dict[str, Any]:
        by_date: pl.DataFrame = data_summary["by_date"]
        metrics_cfg = self.config.get("metrics", {})
        window_days = metrics_cfg.get("window_days", 7)

        n = len(by_date)
        if n == 0:
            return {"hypotheses": []}

        # Split last 2 * window_days into previous + recent windows if possible
        if n >= window_days * 2:
            previous = by_date.slice(n - 2 * window_days, window_days)
            recent = by_date.tail(window_days)
        else:
            # Fallback: first window vs last window (may overlap)
            previous = by_date.head(window_days)
            recent = by_date.tail(window_days)

        # Compute means
        recent_roas = float(recent["roas"].mean())
        prev_roas = float(previous["roas"].mean())
        recent_ctr = float(recent["ctr"].mean())
        prev_ctr = float(previous["ctr"].mean())

        hypotheses: List[Dict[str, Any]] = []

        # Hypothesis 1: overall ROAS drop
        if recent_roas < prev_roas:
            hypotheses.append(
                {
                    "id": "roas_drop_recent_vs_prev",
                    "title": "ROAS dropped in the most recent window vs prior window",
                    "type": "performance_trend",
                    "evidence": {
                        "recent_roas": recent_roas,
                        "previous_roas": prev_roas,
                    },
                    "hypothesis": (
                        "Recent campaigns are less efficient. Possible causes: "
                        "audience fatigue, higher spend on low-ROAS campaigns, "
                        "or weaker creatives."
                    ),
                    "confidence": 0.7,
                }
            )

        # Hypothesis 2: CTR drop → fatigue / creative issue
        if recent_ctr < prev_ctr:
            hypotheses.append(
                {
                    "id": "ctr_drop_possible_fatigue",
                    "title": "CTR drop indicates potential audience fatigue or creative exhaustion",
                    "type": "creative_audience",
                    "evidence": {
                        "recent_ctr": recent_ctr,
                        "previous_ctr": prev_ctr,
                    },
                    "hypothesis": (
                        "Users are clicking less on the same audiences/creatives, "
                        "suggesting fatigue or misalignment of messaging."
                    ),
                    "confidence": 0.65,
                }
            )

        return {"hypotheses": hypotheses}
