from decimal import Decimal, ROUND_HALF_UP
from typing import Final

__all__ = ["add", "subtract", "multiply", "divide", "format_result", "toggle_sign", "calculate_percentage"]


def add(a: Decimal, b: Decimal) -> Decimal:
    """Return the sum of two Decimal values."""
    if not isinstance(a, Decimal) or not isinstance(b, Decimal):
        raise TypeError("add expects Decimal arguments")
    return a + b


def subtract(a: Decimal, b: Decimal) -> Decimal:
    """Return the difference of two Decimal values (a - b)."""
    if not isinstance(a, Decimal) or not isinstance(b, Decimal):
        raise TypeError("subtract expects Decimal arguments")
    return a - b


def multiply(a: Decimal, b: Decimal) -> Decimal:
    """Return the product of two Decimal values."""
    if not isinstance(a, Decimal) or not isinstance(b, Decimal):
        raise TypeError("multiply expects Decimal arguments")
    return a * b


def divide(a: Decimal, b: Decimal) -> Decimal:
    """Return the division a / b using Decimal arithmetic.

    Raises ValueError when dividing by zero.
    """
    if not isinstance(a, Decimal) or not isinstance(b, Decimal):
        raise TypeError("divide expects Decimal arguments")
    if b == Decimal("0"):
        raise ValueError("division by zero")
    return a / b


def format_result(value: Decimal, precision: int = 2) -> str:
    """Format a Decimal value to a string with given precision.

    Rounds using ROUND_HALF_UP. Trailing zeros and an unnecessary
    decimal point are trimmed from the resulting string.

    Examples:
    - format_result(Decimal('2.345'), 2) -> '2.35'
    - format_result(Decimal('2.500'), 2) -> '2.5'
    - format_result(Decimal('0.004'), 2) -> '0'
    """
    if not isinstance(value, Decimal):
        raise TypeError("format_result expects a Decimal value")
    if not isinstance(precision, int) or precision < 0:
        raise ValueError("precision must be a non-negative integer")

    # Build quantizer like Decimal('0.01') for precision 2
    quant: Final[Decimal] = Decimal("1").scaleb(-precision)
    rounded = value.quantize(quant, rounding=ROUND_HALF_UP)

    # Convert to fixed-point string and trim trailing zeros
    s = format(rounded, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")

    # Normalize negative zero to '0'
    try:
        if Decimal(s) == Decimal("0"):
            s = "0"
    except Exception:
        # If Decimal(s) unexpectedly fails, just return the string
        pass

    return s


def toggle_sign(a: Decimal) -> Decimal:
    """Return the value with its sign inverted.

    Raises TypeError if input is not a Decimal.
    """
    if not isinstance(a, Decimal):
        raise TypeError("toggle_sign expects a Decimal argument")
    return a * Decimal("-1")


def calculate_percentage(a: Decimal) -> Decimal:
    """Return the value divided by 100 (percentage conversion).

    Raises TypeError if input is not a Decimal.
    """
    if not isinstance(a, Decimal):
        raise TypeError("calculate_percentage expects a Decimal argument")
    return a / Decimal("100")
