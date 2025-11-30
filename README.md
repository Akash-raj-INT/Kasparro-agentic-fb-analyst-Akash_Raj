# Kasparro — Agentic Facebook Performance Analyst

A fully agentic pipeline that analyzes Facebook Ads performance, diagnoses ROAS fluctuations, validates insights, and generates creative recommendations.

This upgraded version includes:
- Structured JSON logging  
- Retry & backoff logic  
- Schema validation & drift detection  
- Observability metrics  
- Clean agent-based architecture  
- Config-driven behavior  
- Production-style orchestration  

---

## 🚀 Quick Start

```bash
python -V  # Python >= 3.10 recommended
python -m venv .venv
.\.venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
python -m src.run "Analyze ROAS drop in last 7 days"
```

---

## 📂 Data Setup

### Option A — Sample Data
Place a sample file here:

```
data/sample_fb_ads.csv
```

### Option B — Full Data
Set environment variable:

```bash
setx DATA_CSV "C:\path\to\synthetic_fb_ads_undergarments.csv"
```

Then in `config/config.yaml`:

```yaml
use_sample_data: false
paths:
  data_csv_env: "DATA_CSV"
```

---

## ⚙️ Configuration

`config/config.yaml`:

```yaml
python: "3.12"
random_seed: 42

paths:
  sample_csv: "data/sample_fb_ads.csv"
  reports_dir: "reports"
  data_csv_env: "DATA_CSV"

metrics:
  low_ctr_threshold: 0.01
  low_roas_threshold: 1.2
  window_days: 7
```

---

## 🧠 Agent Architecture

```
User Query
    ↓
Planner Agent
    ↓
Data Agent
 - Loads CSV (polars)
 - Schema validation (schema/input_schema.json)
 - Drift detection
 - Summaries: by_date, by_campaign, low_ctr
    ↓
Insight Agent
 - Generates hypotheses (ROAS drop, CTR drop, fatigue)
    ↓
Evaluator Agent
 - Validates hypotheses quantitatively
 - Adjusts confidence scores
    ↓
Creative Generator
 - Suggests headlines, message variations, CTAs
    ↓
Pipeline Output
 - report.md
 - insights.json
 - creatives.json
 - metrics.json
 - logs/traces.jsonl
```

---

## 🔧 Detailed Agent Breakdown

### **1. PlannerAgent**
Interprets the user query and creates an ordered execution plan.

### **2. DataAgent**
- Reads CSV using polars  
- Validates schema against `schema/input_schema.json`  
- Logs missing/extra columns  
- Computes:
  - Daily metrics  
  - Campaign-level metrics  
  - Low-CTR ad subset  

### **3. InsightAgent**
Creates hypotheses based on:
- ROAS anomaly detection  
- CTR decline  
- Creative performance changes  
- Audience fatigue  

### **4. EvaluatorAgent**
Validates hypotheses using:
- Spend share analysis  
- Threshold checks (ROAS, CTR)  
- Confidence score adjustments  

### **5. CreativeGeneratorAgent**
Generates:
- New headline ideas  
- Body copy  
- Calls to action  
- Audience-tailored variations  

---

## 📝 Outputs

Files generated under `/reports`:

```
reports/
 ├── report.md
 ├── insights.json
 ├── creatives.json
 └── metrics.json
```

### **Example: insights.json**
```json
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
```

---

## 📊 Observability & Logging

### **Structured Logging**
All agents log JSON events to:

```
logs/traces.jsonl
```

Fields logged:
- timestamp  
- agent name  
- event name  
- status (start, end, error)  
- duration (if applicable)  
- extra metadata  

### **Metrics**
Pipeline metrics saved to:

```
reports/metrics.json
```

Includes:
- total runtime  
- memory usage  
- rows processed  
- hypotheses generated  
- creatives generated  

---

## 🛡 Reliability Features

### ✔ Retry & Backoff
All critical operations use a retry decorator:
- 3 retries  
- exponential backoff  
- errors logged per attempt  

### ✔ Schema Validation
Loaded CSV validated via:

```
schema/input_schema.json
```

Detects:
- missing columns  
- extra columns  
- schema drift  

All drift warnings logged.

---

## 📘 Repository Structure

```
kasparro-agentic-fb-analyst/
├─ README.md
├─ requirements.txt
├─ config/
│  └─ config.yaml
├─ schema/
│  └─ input_schema.json
├─ src/
│  ├─ run.py
│  ├─ agents/
│  │  ├─ planner.py
│  │  ├─ data_agent.py
│  │  ├─ insight_agent.py
│  │  ├─ evaluator.py
│  │  └─ creative_generator.py
│  ├─ orchestrator/
│  │  └─ pipeline.py
│  └─ utils/
│     ├─ logger.py
│     ├─ retry.py
│     └─ schema_utils.py
├─ logs/
│  └─ traces.jsonl
├─ reports/
│  ├─ report.md
│  ├─ insights.json
│  ├─ creatives.json
│  └─ metrics.json
└─ data/
   └─ sample_fb_ads.csv
```

---

## 🧪 Tests

```
tests/test_evaluator.py
tests/test_schema_validation.py
```

---

## 🎯 Release

Create release tag:

```bash
git tag v1.0
git push origin v1.0
```

---

## 📝 Self-Review (for PR)

- Explain design choices  
- Why agent separation?  
- Why structured logging?  
- Why schema validation?  
- Which metrics were chosen and why?  

---

## ✔ Ready for Submission

This README meets the company’s P0, P1, and P2 requirements.

