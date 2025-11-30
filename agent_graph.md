# Agent Architecture Diagram

User Query
     ↓
Planner Agent
 - Breaks query into subtasks
 - Generates plan for agents

     ↓
Data Agent
 - Loads CSV
 - Schema validation + drift detection
 - Summaries (by_date, by_campaign, low_ctr)

     ↓
Insight Agent
 - Detects ROAS/CTR changes
 - Generates hypotheses

     ↓
Evaluator Agent
 - Quantitatively validates hypotheses
 - Computes confidence scores

     ↓
Creative Generator
 - Produces new creative suggestions
 - Headlines, messages, CTAs

     ↓
Outputs
 - insights.json
 - creatives.json
 - report.md
 - metrics.json
 - logs/traces.jsonl
