from typing import Dict, Any

class BaseAgent:
    name: str

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def run(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement run method")
