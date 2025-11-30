import os
import json
import time
import psutil

from src.agents.planner import PlannerAgent
from src.agents.data_agent import DataAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator import EvaluatorAgent
from src.agents.creative_generator import CreativeGeneratorAgent

from src.utils.logger import log_event, time_block, end_block
from src.utils.retry import retry
import yaml


def load_config(path="config/config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def save_json(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def run_pipeline(query: str, config_path="config/config.yaml") -> dict:
    pipeline_start = time.time()
    log_event("pipeline", "start", extra={"query": query})

    config = load_config(config_path)
    reports_dir = config["paths"]["reports_dir"]
    ensure_dir(reports_dir)

    # --- 1. PLANNER ---------------------------------------------------------
    start = time_block("planner", "plan_generation")
    planner = PlannerAgent(config=config)
    plan_out = planner.run(query=query)
    end_block("planner", "plan_generation", start, extra={"steps": len(plan_out["plan"])})

    # --- 2. DATA AGENT ------------------------------------------------------
    start = time_block("data_agent", "load_summarize")
    data_agent = DataAgent(config=config)
    data_summary = data_agent.run()
    end_block(
        "data_agent",
        "load_summarize",
        start,
        extra={
            "rows_raw": len(data_summary["raw_df"]),
            "rows_low_ctr": len(data_summary["low_ctr_ads"]),
        },
    )

    # --- 3. INSIGHT AGENT ---------------------------------------------------
    start = time_block("insight_agent", "generate_hypotheses")
    insight_agent = InsightAgent(config=config)
    insights = insight_agent.run(data_summary=data_summary, query=query)
    end_block(
        "insight_agent",
        "generate_hypotheses",
        start,
        extra={"num_hypotheses": len(insights["hypotheses"])},
    )

    # --- 4. EVALUATOR AGENT -------------------------------------------------
    start = time_block("evaluator", "validate_hypotheses")
    evaluator = EvaluatorAgent(config=config)
    evaluated = evaluator.run(data_summary=data_summary, insights=insights)
    end_block(
        "evaluator",
        "validate_hypotheses",
        start,
        extra={"num_validated": len(evaluated["evaluated_hypotheses"])},
    )

    # --- 5. CREATIVE GENERATOR ---------------------------------------------
    start = time_block("creative_generator", "generate_creatives")
    creative_agent = CreativeGeneratorAgent(config=config)
    creative = creative_agent.run(data_summary=data_summary)
    end_block(
        "creative_generator",
        "generate_creatives",
        start,
        extra={"num_creative_recos": len(creative["creative_recommendations"])},
    )

    # --- SAVE JSON OUTPUTS --------------------------------------------------
    insights_path = os.path.join(reports_dir, "insights.json")
    creatives_path = os.path.join(reports_dir, "creatives.json")

    save_json(insights_path, evaluated)
    save_json(creatives_path, creative)

    # --- WRITE REPORT -------------------------------------------------------
    report_path = os.path.join(reports_dir, "report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Facebook ROAS Analysis Report\n\n")
        f.write(f"## Query\n`{query}`\n\n")
        f.write("## Hypotheses & Evaluation\n")
        for h in evaluated["evaluated_hypotheses"]:
            f.write(f"\n### {h['title']}\n")
            f.write(f"- Confidence: **{h['confidence']:.2f}**\n")
            f.write(f"- Evidence: `{h['evidence']}`\n")
            f.write(f"- Hypothesis: {h['hypothesis']}\n")

        f.write("\n\n## Creative Recommendations (Top 5)\n")
        for rec in creative["creative_recommendations"][:5]:
            f.write(f"\n- **Campaign:** {rec['campaign_name']}\n")
            f.write(f"  - Audience: {rec['audience_type']}\n")
            f.write(f"  - Original: {rec['original_message']}\n")
            f.write(f"  - Headlines: {rec['suggested_headlines']}\n")
            f.write(f"  - CTAs: {rec['suggested_ctas']}\n")

    # ------------------------------------------------------------------------
    # ✅ END OF PIPELINE → SAVE OBSERVABILITY METRICS
    # ------------------------------------------------------------------------
    total_time = time.time() - pipeline_start
    memory_usage_mb = psutil.Process().memory_info().rss / (1024 * 1024)

    metrics = {
        "pipeline_runtime_sec": round(total_time, 3),
        "memory_usage_mb": round(memory_usage_mb, 2),
        "rows_raw": len(data_summary["raw_df"]),
        "rows_low_ctr": len(data_summary["low_ctr_ads"]),
        "num_hypotheses": len(insights["hypotheses"]),
        "num_validated": len(evaluated["evaluated_hypotheses"]),
        "num_creative_recos": len(creative["creative_recommendations"])
    }

    metrics_path = os.path.join(reports_dir, "metrics.json")
    save_json(metrics_path, metrics)

    log_event("pipeline", "end", extra={"runtime_sec": total_time})

    return {
        "plan": plan_out,
        "insights": evaluated,
        "creatives": creative,
        "paths": {
            "report": report_path,
            "insights": insights_path,
            "creatives": creatives_path,
            "metrics": metrics_path
        },
    }
