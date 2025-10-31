from decimal import Decimal
from typing import List

from utils.calculator import add, subtract, multiply, divide

__all__ = ["tokenize", "to_rpn", "evaluate_rpn", "evaluate_expression"]

_OPERATORS = {
    "+": {
        "prec": 1,
        "func": add,
    },
    "-": {
        "prec": 1,
        "func": subtract,
    },
    "*": {
        "prec": 2,
        "func": multiply,
    },
    "/": {
        "prec": 2,
        "func": divide,
    },
}


def tokenize(expression: str) -> List[str]:
    """Tokenize the input expression into numbers, operators, and parentheses.

    Raises ValueError on invalid characters or malformed numbers.
    """
    if not isinstance(expression, str):
        raise ValueError("expression must be a string")

    tokens: List[str] = []
    i = 0
    n = len(expression)
    while i < n:
        ch = expression[i]
        if ch.isspace():
            i += 1
            continue
        if ch in _OPERATORS or ch in "()":
            tokens.append(ch)
            i += 1
            continue
        # number parsing: digits with optional single dot
        if ch.isdigit() or ch == ".":
            num_chars = []
            dot_count = 0
            while i < n and (expression[i].isdigit() or expression[i] == "."):
                if expression[i] == ".":
                    dot_count += 1
                    if dot_count > 1:
                        raise ValueError(f"invalid numeric literal with multiple dots near: {expression[max(0,i-5):i+5]}")
                num_chars.append(expression[i])
                i += 1
            # ensure that number isn't just '.'
            num_str = "".join(num_chars)
            if num_str == ".":
                raise ValueError("invalid numeric literal '.'")
            tokens.append(num_str)
            continue
        raise ValueError(f"invalid character in expression: '{ch}'")
    return tokens


def to_rpn(tokens: List[str]) -> List[str]:
    """Convert infix tokens to RPN (postfix) using shunting-yard.

    Validates token sequences and parentheses. Raises ValueError on malformed input.
    """
    if not isinstance(tokens, list):
        raise ValueError("tokens must be a list of strings")

    output: List[str] = []
    op_stack: List[str] = []

    prev_type = "start"  # one of: start, number, operator, lparen, rparen

    for tok in tokens:
        if tok == "(" :
            # lparen cannot directly follow a number or rparen without operator
            if prev_type in ("number", "rparen"):
                raise ValueError("missing operator before '('")
            op_stack.append(tok)
            prev_type = "lparen"
            continue
        if tok == ")":
            if prev_type == "operator" or prev_type == "start" or prev_type == "lparen":
                # empty parentheses or operator before ')'
                raise ValueError("misplaced ')'")
            # pop until '('
            while op_stack and op_stack[-1] != "(":
                output.append(op_stack.pop())
            if not op_stack or op_stack[-1] != "(":
                raise ValueError("mismatched parentheses")
            op_stack.pop()  # remove '('
            prev_type = "rparen"
            continue
        if tok in _OPERATORS:
            # operator validation
            if prev_type in ("operator", "start", "lparen"):
                raise ValueError(f"misplaced operator '{tok}'")
            # pop operators with >= precedence
            while op_stack and op_stack[-1] in _OPERATORS and _OPERATORS[op_stack[-1]]["prec"] >= _OPERATORS[tok]["prec"]:
                output.append(op_stack.pop())
            op_stack.append(tok)
            prev_type = "operator"
            continue
        # must be number
        # validate token looks like a number
        try:
            # Using Decimal to validate numeric format
            Decimal(tok)
        except Exception:
            raise ValueError(f"invalid numeric token '{tok}'")
        if prev_type in ("number", "rparen"):
            raise ValueError("missing operator between operands")
        output.append(tok)
        prev_type = "number"

    # end for tokens
    if prev_type == "operator" or prev_type == "lparen":
        raise ValueError("expression ends with incomplete token")

    while op_stack:
        op = op_stack.pop()
        if op == "(" or op == ")":
            raise ValueError("mismatched parentheses")
        output.append(op)

    return output


def evaluate_rpn(rpn: List[str]) -> Decimal:
    """Evaluate an RPN expression list using decimal arithmetic functions.

    Raises ValueError on malformed RPN or on arithmetic errors like division by zero.
    """
    if not isinstance(rpn, list):
        raise ValueError("rpn must be a list of tokens")

    stack: List[Decimal] = []

    for tok in rpn:
        if tok in _OPERATORS:
            # need two operands
            if len(stack) < 2:
                raise ValueError("insufficient operands for operator")
            b = stack.pop()
            a = stack.pop()
            try:
                result = _OPERATORS[tok]["func"](a, b)
            except ValueError as e:
                # propagate ValueError from calculator (e.g., division by zero)
                raise
            except Exception as e:
                raise ValueError(f"error evaluating operator '{tok}': {e}")
            stack.append(result)
        else:
            try:
                val = Decimal(tok)
            except Exception:
                raise ValueError(f"invalid numeric token in RPN '{tok}'")
            stack.append(val)

    if len(stack) != 1:
        raise ValueError("malformed RPN expression")
    return stack[0]


def evaluate_expression(expression: str) -> Decimal:
    """Convenience: tokenize, convert to RPN, and evaluate the expression.

    Raises ValueError for malformed expressions or arithmetic errors.
    """
    try:
        tokens = tokenize(expression)
        rpn = to_rpn(tokens)
        return evaluate_rpn(rpn)
    except ValueError:
        # re-raise ValueError as-is
        raise
    except Exception as e:
        # Wrap other exceptions as ValueError to provide consistent API
        raise ValueError(f"failed to evaluate expression: {e}")
