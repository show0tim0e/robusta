from typing import Any, Dict


class Evaluator:
    def evaluate(
        self,
        model: Any,
        x: Any,
        y: Any,
        adv_x: Any = None,
    ) -> Dict[str, float]:
        pass