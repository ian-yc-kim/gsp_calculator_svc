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


def _format_scientific(value: Decimal, max_len: int = 15) -> str:
    """Format Decimal in scientific notation ensuring total length <= max_len.

    Produces strings like '1.23e+15' or '-2.5e-20'. Uses ROUND_HALF_UP for mantissa
    rounding. Handles rounding overflow (mantissa -> 10) by shifting exponent.
    """
    if not isinstance(value, Decimal):
        raise TypeError("_format_scientific expects a Decimal value")

    # Normalize negative zero
    try:
        if value == Decimal('0'):
            return '0'
    except Exception:
        # If comparison fails for unexpected Decimal, fallback
        pass

    sign = '-' if value < 0 else ''
    abs_v = value.copy_abs()

    # Determine exponent (power of 10) and mantissa in [1,10)
    # adjusted() gives the exponent of the most significant digit
    exp = int(abs_v.normalize().adjusted())
    # Scale to get mantissa: mantissa = abs_v * 10**(-exp)
    mantissa = abs_v.scaleb(-exp)

    # Build exponent component e±NN
    exponent_component = f"e{exp:+d}"

    # Reserve space: total length = len(sign) + len(mantissa_str) + len(exponent_component)
    # mantissa_str is like 1(.frac)
    max_len = int(max_len)
    allowed_mantissa_len = max_len - len(exponent_component) - len(sign)
    if allowed_mantissa_len <= 0:
        # Extremely constrained; fallback to a minimal representation
        # e.g., -1e+100
        return f"{sign}1{exponent_component}"

    # Determine fraction digits we can show in mantissa
    # mantissa_str length = 1 (integer digit) + (1 + frac_digits if frac_digits>0 else 0)
    # so if frac_digits>0 then length = 2 + frac_digits
    if allowed_mantissa_len == 1:
        frac_digits = 0
    else:
        frac_digits = max(0, allowed_mantissa_len - 2)

    # Quantize mantissa accordingly
    if frac_digits > 0:
        quant = Decimal('1').scaleb(-frac_digits)
    else:
        quant = Decimal('1')

    rounded_mant = mantissa.quantize(quant, rounding=ROUND_HALF_UP)

    # Handle rounding overflow where mantissa becomes 10 -> convert to 1 and increment exponent
    if rounded_mant == Decimal('10'):
        rounded_mant = Decimal('1')
        exp += 1
        exponent_component = f"e{exp:+d}"

    # Convert mantissa to string and trim trailing zeros and unnecessary dot
    s_mant = format(rounded_mant, 'f')
    if '.' in s_mant:
        s_mant = s_mant.rstrip('0').rstrip('.')

    result = f"{sign}{s_mant}{exponent_component}"

    # As a safety, ensure returned length <= max_len. If not, fallback to more compact form.
    if len(result) > max_len:
        # Try with zero fractional digits
        rounded_mant = mantissa.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        if rounded_mant == Decimal('10'):
            rounded_mant = Decimal('1')
            exp += 1
        s_mant = format(rounded_mant, 'f')
        if '.' in s_mant:
            s_mant = s_mant.rstrip('0').rstrip('.')
        result = f"{sign}{s_mant}e{exp:+d}"
        if len(result) > max_len:
            # Final fallback: minimal '1e+NN' with sign if needed
            minimal = f"{sign}1e{exp:+d}"
            if len(minimal) <= max_len:
                return minimal
            # If even minimal is too long (very unlikely), truncate exponent digits
            # Keep last (max_len - len(sign) - 2) digits of exponent
            exp_str = str(abs(exp))
            fit = max(1, max_len - len(sign) - 2)
            truncated_exp = exp_str[-fit:]
            sign_exp = '+' if exp >= 0 else '-'
            return f"{sign}1e{sign_exp}{truncated_exp}"

    return result


def format_result(value: Decimal, precision: int = 2) -> str:
    """Format a Decimal value to a string with given precision.

    Rounds using ROUND_HALF_UP. Trailing zeros and an unnecessary
    decimal point are trimmed from the resulting string.

    Extremely large or small values are represented in scientific
    notation to ensure they fit within a 15-character display.
    """
    if not isinstance(value, Decimal):
        raise TypeError("format_result expects a Decimal value")
    if not isinstance(precision, int) or precision < 0:
        raise ValueError("precision must be a non-negative integer")

    # Thresholds for scientific notation
    LARGE_THRESHOLD = Decimal('1e12')
    SMALL_THRESHOLD = Decimal('1e-9')

    # Normalize negative zero early
    try:
        if value == Decimal('0'):
            return '0'
    except Exception:
        pass

    # Decide scientific formatting based on original magnitude
    try:
        if (value.copy_abs() >= LARGE_THRESHOLD) or (value.copy_abs() <= SMALL_THRESHOLD and value != Decimal('0')):
            return _format_scientific(value, max_len=15)
    except Exception:
        # On any unexpected Decimal operation error, fall back to safe path
        pass

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
