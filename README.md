# Kasparro — Agentic Facebook Performance Analyst

## Overview
This project implements a self-directed multi-agent system that autonomously analyzes Facebook Ads performance, diagnoses ROAS fluctuations, and generates data-driven creative recommendations.

Built as part of the Kasparro Applied AI Engineer Assignment — Agentic Facebook Performance Analyst.

## Objective
The system automatically:
• Diagnoses why ROAS changed over time
• Identifies drivers behind performance shifts
• Generates hypotheses with confidence scores
• Validates insights using quantitative evidence
• Produces new creative directions for low-CTR campaigns

No UI required — the system runs via CLI.

## Agent Architecture

Flow:
User Query
 → Planner Agent (creates execution plan)
 → Data Agent (loads and summarizes dataset)
 → Insight Agent (generates hypotheses)
 → Evaluator Agent (validates and adjusts confidence)
 → Creative Generator (suggests new messaging)
 → Reports + JSON outputs

## Quick Start

Requirements:
• Python 3.10 – 3.12
• No UI or database required

Setup commands:
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

Run command:
python -m src.run "Analyze ROAS drop in last 7 days"

## Repository Structure

kasparro-agentic-fb-analyst-akash-raj/
├─ README.md
├─ requirements.txt
├─ config/
│  └─ config.yaml
├─ src/
│  ├─ run.py
│  ├─ orchestrator/
│  │  └─ pipeline.py
│  └─ agents/
│     ├─ base.py
│     ├─ planner.py
│     ├─ data_agent.py
│     ├─ insight_agent.py
│     ├─ evaluator.py
│     └─ creative_generator.py
├─ prompts/
├─ data/
│  ├─ sample_fb_ads.csv
│  └─ README.md
├─ reports/
│  ├─ report.md
│  ├─ insights.json
│  └─ creatives.json
├─ logs/
├─ tests/
│  └─ test_evaluator.py

## Configuration

Config file: config/config.yaml

Example:
use_sample_data: true
paths:
  sample_csv: "data/sample_fb_ads.csv"
  reports_dir: "reports"
metrics:
  low_ctr_threshold: 0.01
  low_roas_threshold: 1.2
  window_days: 7
random_seed: 42

## Outputs Generated

After running the pipeline, the following files are produced:

reports/report.md
• Final marketer summary

reports/insights.json
Contains evaluated hypotheses with confidence and evidence

Example:
{
  "evaluated_hypotheses": [
    {
      "id": "roas_drop_recent_vs_prev",
      "confidence": 0.78,
      "evidence": {
        "recent_roas": 1.21,
        "previous_roas": 1.87,
        "low_roas_spend_share": 0.46
      }
    }
  ]
}

reports/creatives.json
Includes new creative recommendations for low-CTR ads

## Reproducibility
• Deterministic output via config random_seed
• Version-pinned dependencies
• Sample dataset included
• No external API required

## How to Submit
1. Push to public GitHub repo named:
   kasparro-agentic-fb-analyst-<firstname-lastname>
2. Create release tag:
   v1.0
3. Provide:
   • Repo link
   • Commit hash
   • Run command used

## Example Submission Format

Repo: https://github.com/akashraj/kasparro-agentic-fb-analyst
Commit: a93f2d1
Tag: v1.0
Command:
python -m src.run "Analyze ROAS drop in last 7 days"
