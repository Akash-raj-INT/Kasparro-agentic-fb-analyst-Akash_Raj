import polars as pl

from src.agents.evaluator import EvaluatorAgent


def test_evaluator_adds_spend_share():
    config = {"metrics": {"low_roas_threshold": 1.2}}
    evaluator = EvaluatorAgent(config=config)

    by_campaign = pl.DataFrame(
        {
            "campaign_name": ["A", "B"],
            "spend": [100.0, 100.0],
            "roas": [0.8, 2.0],
        }
    )

    data_summary = {"by_campaign": by_campaign}
    insights = {
        "hypotheses": [
            {
                "id": "roas_drop_recent_vs_prev",
                "title": "dummy",
                "hypothesis": "dummy",
                "evidence": {},
                "confidence": 0.7,
            }
        ]
    }

    out = evaluator.run(data_summary=data_summary, insights=insights)
    h = out["evaluated_hypotheses"][0]
    assert "low_roas_spend_share" in h["evidence"]
