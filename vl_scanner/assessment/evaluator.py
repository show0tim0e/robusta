from typing import Any


class Evaluator:
    def evaluate(
        self,
        model: Any,
        x: Any,
        y: Any,
        adv_x: Any = None,
    ) -> dict[str, float]:
        pass