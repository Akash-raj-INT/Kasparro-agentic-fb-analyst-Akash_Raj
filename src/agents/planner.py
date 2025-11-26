from typing import Dict, Any, List
from .base import BaseAgent

class PlannerAgent(BaseAgent):
    name = "planner"

    def run(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Example query: 'Analyze ROAS drop in last 7 days'
        Output: ordered list of steps for other agents
        """
        plan: List[Dict[str, Any]] = [
            {"step": 1, "agent": "data", "action": "load_and_summarize"},
            {"step": 2, "agent": "insight", "action": "generate_hypotheses"},
            {"step": 3, "agent": "evaluator", "action": "validate_hypotheses"},
            {"step": 4, "agent": "creative", "action": "improve_low_ctr_creatives"},
        ]
        return {
            "query": query,
            "plan": plan,
        }
