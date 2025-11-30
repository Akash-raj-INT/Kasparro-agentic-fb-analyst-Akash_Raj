import json
from src.utils.logger import log_event


def validate_schema(df, agent: str):
    try:
        with open("schema/input_schema.json") as f:
            schema = json.load(f)
    except Exception as e:
        log_event(agent, "schema_file_missing", "error", {"error": str(e)})
        return False

    required = set(schema.get("required_columns", []))
    actual = set(df.columns)

    missing = required - actual
    extra = actual - required

    if missing:
        log_event(agent, "schema_missing_columns", "warning", {"missing": list(missing)})

    if extra:
        log_event(agent, "schema_extra_columns", "warning", {"extra": list(extra)})

    return len(missing) == 0
