import pytest
from decimal import Decimal

from utils.parser import tokenize, to_rpn, evaluate_rpn, evaluate_expression


def test_tokenize_simple_expression():
    expr = "2 + 3 * 4"
    assert tokenize(expr) == ["2", "+", "3", "*", "4"]


def test_to_rpn_simple_expression():
    tokens = ["2", "+", "3", "*", "4"]
    assert to_rpn(tokens) == ["2", "3", "4", "*", "+"]


@pytest.mark.parametrize(
    "expr,expected",
    [
        ("2 + 3 * 4", Decimal("14")),
        ("(2 + 3) * 4", Decimal("20")),
        ("10 / (2 + 3)", Decimal("2")),
        ("1.5 + 2.5 * 3", Decimal("9.0")),
    ],
)
def test_evaluate_expressions(expr, expected):
    result = evaluate_expression(expr)
    assert result == expected


def test_evaluate_rpn_direct():
    rpn = ["1", "2", "+", "3", "*"]  # (1+2)*3 = 9
    assert evaluate_rpn(rpn) == Decimal("9")


@pytest.mark.parametrize(
    "bad_expr",
    [
        "1 + (2",
        "1 + * 2",
        "abc",
        ")1+2(",
        "1..2 + 3",
    ],
)
def test_malformed_expressions_raise(bad_expr):
    with pytest.raises(ValueError):
        evaluate_expression(bad_expr)


def test_division_by_zero_raises():
    with pytest.raises(ValueError):
        evaluate_expression("1 / 0")


def test_consecutive_numbers_without_operator_raises():
    with pytest.raises(ValueError):
        # missing operator between numbers
        evaluate_expression("1 2 + 3")
