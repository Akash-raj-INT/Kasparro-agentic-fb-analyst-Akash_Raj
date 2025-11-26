from typing import Dict, Any
import json
import os
import yaml

from src.agents.planner import PlannerAgent
from src.agents.data_agent import DataAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator import EvaluatorAgent
from src.agents.creative_generator import CreativeGeneratorAgent

def load_config(path: str = "config/config.yaml") -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def run_pipeline(query: str, config_path: str = "config/config.yaml") -> Dict[str, Any]:
    config = load_config(config_path)
    reports_dir = config["paths"]["reports_dir"]
    ensure_dir(reports_dir)

    # 1) Planner
    planner = PlannerAgent(config=config)
    plan_out = planner.run(query=query)

    # 2) Data
    data_agent = DataAgent(config=config)
    data_summary = data_agent.run()

    # 3) Insights
    insight_agent = InsightAgent(config=config)
    insights = insight_agent.run(data_summary=data_summary, query=query)

    # 4) Evaluator
    evaluator = EvaluatorAgent(config=config)
    evaluated = evaluator.run(data_summary=data_summary, insights=insights)

    # 5) Creative
    creative_agent = CreativeGeneratorAgent(config=config)
    creative = creative_agent.run(data_summary=data_summary)

    # Save JSONs
    insights_path = os.path.join(reports_dir, "insights.json")
    creatives_path = os.path.join(reports_dir, "creatives.json")

    with open(insights_path, "w", encoding="utf-8") as f:
        json.dump(evaluated, f, indent=2)

    with open(creatives_path, "w", encoding="utf-8") as f:
        json.dump(creative, f, indent=2)

    # Simple text report
    report_path = os.path.join(reports_dir, "report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Facebook ROAS Analysis\n\n")
        f.write(f"## Query\n\n`{query}`\n\n")
        f.write("## Key Hypotheses\n\n")
        for h in evaluated["evaluated_hypotheses"]:
            f.write(f"### {h['title']}\n")
            f.write(f"- Confidence: {h['confidence']:.2f}\n")
            f.write(f"- Hypothesis: {h['hypothesis']}\n")
            f.write(f"- Evidence: {h['evidence']}\n\n")
        f.write("## Creative Recommendations (sample)\n\n")
        for rec in creative["creative_recommendations"][:5]:
            f.write(f"- **Campaign**: {rec['campaign_name']} | Audience: {rec['audience_type']}\n")
            f.write(f"  - Original: {rec['original_message']}\n")
            f.write(f"  - Headlines: {rec['suggested_headlines']}\n")
            f.write(f"  - CTAs: {rec['suggested_ctas']}\n\n")

    return {
        "plan": plan_out,
        "insights": evaluated,
        "creatives": creative,
        "paths": {
            "report": report_path,
            "insights": insights_path,
            "creatives": creatives_path,
        },
    }
