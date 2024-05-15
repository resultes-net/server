import contextlib as ctx
import dataclasses as dc
import collections.abc as cabc

import pytest as pt

import resultes_server.months as months

@dc.dataclass
class Case:
    expression: str
    hour: int = dc.field(init=False)
    expected_month: int | None

    def __post_init__(self) -> None:
        if self.expected_month is not None:
            if not (1 <= self.expected_month <= 12):
                raise ValueError("Expected month must be None or be in [1,12]", self.expected_month)

        self.hour = eval(self.expression)

def get_test_cases() -> cabc.Iterable[Case]:
    yield Case("3*24", 1)
    yield Case("(31+28+31+30+31+27)*24", 6)
    yield Case("8770", None)
    yield Case("8736", 12)
    yield Case("8760", 12)

class TestMonths:
    @pt.mark.parametrize("test_case", [pt.param(c, id=c.expression) for c in get_test_cases()])
    def test_months(self, test_case: Case) -> None:
        context_manager = pt.raises(ValueError) if test_case.expected_month is None else ctx.nullcontext()

        actual_month = None

        with context_manager:
            actual_month = months.get_month(test_case.hour)
        
        if actual_month:
            assert actual_month == test_case.expected_month

