import time
from src.utils.logger import log_event

def retry(agent, action, retries=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    log_event(agent, f"{action}_attempt_{attempt}_failed", "error", {"error": str(e)})
                    time.sleep(delay * attempt)
            log_event(agent, f"{action}_failed_all_retries", "critical")
            raise
        return wrapper
    return decorator
