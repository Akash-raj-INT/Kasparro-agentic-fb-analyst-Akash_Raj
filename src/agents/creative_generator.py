from typing import Any, Dict, List

import polars as pl

from .base import BaseAgent


class CreativeGeneratorAgent(BaseAgent):
    name = "creative"

    def run(
        self,
        data_summary: Dict[str, Any],
        **kwargs,
    ) -> Dict[str, Any]:
        low_ctr_ads: pl.DataFrame = data_summary["low_ctr_ads"]

        recommendations: List[Dict[str, Any]] = []

        # Limit to first 20 low-CTR ads for creativity
        for row in low_ctr_ads.head(20).iter_rows(named=True):
            base_msg = str(row.get("creative_message", "") or "")
            audience = row.get("audience_type", "broad") or "broad"
            campaign = row.get("campaign_name", "") or ""

            recommendations.append(
                {
                    "campaign_name": campaign,
                    "audience_type": audience,
                    "original_message": base_msg,
                    "suggested_headlines": [
                        f"Limited-time offer for {audience} shoppers",
                        "Comfort + style you can wear all day",
                    ],
                    "suggested_body": [
                        "Upgrade your everyday essentials with breathable, all-day comfort.",
                        "Bundle & save on our most-loved styles before they sell out.",
                    ],
                    "suggested_ctas": [
                        "Shop the Collection",
                        "Claim Your Offer",
                    ],
                }
            )

        return {"creative_recommendations": recommendations}
