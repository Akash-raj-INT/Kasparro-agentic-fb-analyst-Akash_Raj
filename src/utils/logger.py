import json
import time
import os
from datetime import datetime

LOG_PATH = "logs/traces.jsonl"

os.makedirs("logs", exist_ok=True)

def log_event(agent, event, status="info", extra=None):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent,
        "event": event,
        "status": status,
        "extra": extra or {},
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

def time_block(agent, action):
    start = time.time()
    log_event(agent, f"start_{action}")
    return start

def end_block(agent, action, start, extra=None):
    duration = time.time() - start
    log_event(agent, f"end_{action}", extra={"duration_sec": duration, **(extra or {})})
