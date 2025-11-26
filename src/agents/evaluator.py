from typing import Any, Dict, List

import polars as pl

from .base import BaseAgent


class EvaluatorAgent(BaseAgent):
    name = "evaluator"

    def run(
        self,
        data_summary: Dict[str, Any],
        insights: Dict[str, Any],
        **kwargs,
    ) -> Dict[str, Any]:
        by_campaign: pl.DataFrame = data_summary["by_campaign"]
        hypotheses: List[Dict[str, Any]] = insights.get("hypotheses", [])

        if "spend" not in by_campaign.columns or len(by_campaign) == 0:
            return {"evaluated_hypotheses": hypotheses}

        total_spend = float(by_campaign["spend"].sum())
        metrics_cfg = self.config.get("metrics", {})
        low_roas_threshold = metrics_cfg.get("low_roas_threshold", 1.2)

        for h in hypotheses:
            if h.get("id") == "roas_drop_recent_vs_prev":
                low_roas = by_campaign.filter(pl.col("roas") < low_roas_threshold)
                low_spend = float(low_roas["spend"].sum()) if len(low_roas) else 0.0
                share_spend = float(low_spend / total_spend) if total_spend else 0.0

                # Add evidence
                h.setdefault("evidence", {})
                h["evidence"]["low_roas_spend_share"] = share_spend

                # Adjust confidence based on how much spend is on low-ROAS campaigns
                if share_spend > 0.4:
                    h["confidence"] = min(1.0, h.get("confidence", 0.6) + 0.1)
                else:
                    h["confidence"] = max(0.4, h.get("confidence", 0.6) - 0.1)

        return {"evaluated_hypotheses": hypotheses}
