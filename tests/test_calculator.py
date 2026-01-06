import pytest
from decimal import Decimal

from utils.calculator import (
    add,
    subtract,
    multiply,
    divide,
    format_result,
    toggle_sign,
    calculate_percentage,
)


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (Decimal("1.1"), Decimal("2.2"), Decimal("3.3")),
        (Decimal("0"), Decimal("0"), Decimal("0")),
        (Decimal("-1"), Decimal("1"), Decimal("0")),
        (Decimal("2.345"), Decimal("0.005"), Decimal("2.350")),
    ],
)
def test_add(a, b, expected):
    assert add(a, b) == expected


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (Decimal("5"), Decimal("2"), Decimal("3")),
        (Decimal("2.5"), Decimal("0.5"), Decimal("2.0")),
        (Decimal("-1"), Decimal("-1"), Decimal("0")),
    ],
)
def test_subtract(a, b, expected):
    assert subtract(a, b) == expected


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (Decimal("2"), Decimal("3"), Decimal("6")),
        (Decimal("0.5"), Decimal("0.2"), Decimal("0.10")),
        (Decimal("-1"), Decimal("3"), Decimal("-3")),
    ],
)
def test_multiply(a, b, expected):
    assert multiply(a, b) == expected


@pytest.mark.parametrize(
    "a,b",
    [
        (Decimal("1"), Decimal("3")),
        (Decimal("10"), Decimal("4")),
        (Decimal("-5"), Decimal("2")),
    ],
)
def test_divide_normal(a, b):
    # Expected is computed with Decimal division using the same values
    expected = a / b
    assert divide(a, b) == expected


def test_divide_by_zero_raises():
    with pytest.raises(ValueError) as excinfo:
        divide(Decimal("1"), Decimal("0"))
    assert "division by zero" in str(excinfo.value)


@pytest.mark.parametrize(
    "value,precision,expected",
    [
        (Decimal("2.345"), 2, "2.35"),  # round half up
        (Decimal("2.344"), 2, "2.34"),
        (Decimal("2.500"), 2, "2.5"),  # trim trailing zero
        (Decimal("2.5"), 0, "3"),  # precision 0
        (Decimal("-1.2345"), 3, "-1.235"),
        (Decimal("0.004"), 2, "0"),  # rounds to 0.00 then trimmed
    ],
)
def test_format_result(value, precision, expected):
    assert format_result(value, precision) == expected


def test_format_result_invalid_inputs():
    with pytest.raises(TypeError):
        format_result(1.23, 2)  # non-Decimal value
    with pytest.raises(ValueError):
        format_result(Decimal("1.23"), -1)  # negative precision


# Tests for toggle_sign
@pytest.mark.parametrize(
    "value,expected",
    [
        (Decimal("123"), Decimal("-123")),
        (Decimal("-5"), Decimal("5")),
        (Decimal("0"), Decimal("0")),
        (Decimal("0.001"), Decimal("-0.001")),
    ],
)
def test_toggle_sign_success(value, expected):
    assert toggle_sign(value) == expected


def test_toggle_sign_invalid_inputs():
    with pytest.raises(TypeError):
        toggle_sign(1)
    with pytest.raises(TypeError):
        toggle_sign("1")


# Tests for calculate_percentage
@pytest.mark.parametrize(
    "value,expected",
    [
        (Decimal("200"), Decimal("2")),
        (Decimal("-50"), Decimal("-0.5")),
        (Decimal("0"), Decimal("0")),
        (Decimal("0.01"), Decimal("0.0001")),
    ],
)
def test_calculate_percentage_success(value, expected):
    assert calculate_percentage(value) == expected


def test_calculate_percentage_invalid_inputs():
    with pytest.raises(TypeError):
        calculate_percentage(1)
    with pytest.raises(TypeError):
        calculate_percentage("1")


# Additional tests for scientific notation formatting
def test_scientific_large_positive():
    out = format_result(Decimal('1e20'))
    assert 'e' in out
    assert out == '1e+20'


def test_scientific_small_positive():
    out = format_result(Decimal('1e-20'))
    assert 'e' in out
    assert out == '1e-20'


def test_scientific_large_negative():
    out = format_result(Decimal('-2.5e20'))
    # Should preserve mantissa and exponent
    assert out.startswith('-2.5')
    assert 'e+20' in out


def test_threshold_boundaries():
    # exactly at large threshold -> scientific
    assert 'e' in format_result(Decimal('1e12'))
    # just below threshold -> not scientific
    normal = format_result(Decimal('999999999999'))
    assert 'e' not in normal

    # exactly at small threshold -> scientific
    assert 'e' in format_result(Decimal('1e-9'))
    # just above small threshold -> not scientific
    assert 'e' not in format_result(Decimal('1.1e-9'))
    # additional edge: 9.9e-10 should be in scientific notation (<= 1e-9)
    assert 'e' in format_result(Decimal('9.9e-10'))


def test_zero_and_negative_zero_normalized():
    assert format_result(Decimal('0')) == '0'
    assert format_result(Decimal('-0.000')) == '0'


def test_scientific_length_constraint():
    out = format_result(Decimal('9.999999999999999e123'))
    assert 'e' in out
    assert len(out) <= 15
