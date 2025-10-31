import streamlit as st
from pathlib import Path

try:
    st.set_page_config(layout="wide", page_title="Streamlit Calculator")
except Exception as e:
    # set_page_config may raise if called multiple times; log for debugging
    try:
        print('Component:', e)
    except Exception:
        pass

from typing import Optional

# import evaluation and formatting utilities
from utils import parser as _parser
from utils import calculator as _calculator


def _init_session_state() -> None:
    """Initialize st.session_state with calculator defaults if missing."""
    ss = st.session_state
    # Only set defaults if keys not present
    ss.setdefault('current_input', "0")
    ss.setdefault('previous_value', "")
    ss.setdefault('operator', None)
    ss.setdefault('waiting_for_operand', True)
    ss.setdefault('display_value', "0")
    ss.setdefault('calculation_history', [])
    ss.setdefault('error_state', None)


def _inject_styles() -> None:
    """Read components/styles.css and inject into the page via markdown.

    Defensive: swallow any file IO errors and log.
    """
    try:
        base = Path(__file__).parent
        css_path = base / 'components' / 'styles.css'
        if css_path.exists():
            try:
                css_text = css_path.read_text(encoding='utf-8')
                st.markdown(f"<style>{css_text}</style>", unsafe_allow_html=True)
            except Exception as e:
                try:
                    print('Component:', e)
                except Exception:
                    pass
        else:
            # no-op if stylesheet not present
            pass
    except Exception as e:
        try:
            print('Component:', e)
        except Exception:
            pass


def _clear_state() -> None:
    """Reset all calculator session state variables to initial defaults."""
    ss = st.session_state
    ss['current_input'] = "0"
    ss['previous_value'] = ""
    ss['operator'] = None
    ss['waiting_for_operand'] = True
    ss['display_value'] = "0"
    ss['calculation_history'] = []
    ss['error_state'] = None


def _perform_calculation() -> str:
    """Perform the calculation using session state and persist history.

    Returns the string result (formatted) or a safe fallback string.
    """
    try:
        ss = st.session_state
        prev: str = ss.get('previous_value', '')
        op: Optional[str] = ss.get('operator')
        curr: str = ss.get('current_input', '0')

        # If no operator or previous value, treat current input as the result
        if not op or not prev:
            # Do not store in history; just ensure display reflects current input
            ss['display_value'] = curr
            ss['current_input'] = curr
            ss['previous_value'] = ""
            ss['operator'] = None
            ss['waiting_for_operand'] = True
            ss['error_state'] = None
            return curr

        # Map UI operator to parser operator for evaluation
        eval_op = op
        if op == '×':
            eval_op = '*'
        elif op == '÷':
            eval_op = '/'

        # Build expression for history using UI operator
        expression = f"{prev} {op} {curr}"
        # Build expression for evaluation using parser operators
        eval_expression = f"{prev} {eval_op} {curr}"

        try:
            result_dec = _parser.evaluate_expression(eval_expression)
            formatted = _calculator.format_result(result_dec)

            # Append to history
            try:
                ss['calculation_history'].append({
                    'expression': expression,
                    'result': formatted,
                })
            except Exception:
                # ensure history exists and append
                ss['calculation_history'] = ss.get('calculation_history', []) + [{
                    'expression': expression,
                    'result': formatted,
                }]

            # Update state for chaining
            ss['display_value'] = formatted
            ss['current_input'] = formatted
            ss['previous_value'] = ""
            ss['operator'] = None
            ss['waiting_for_operand'] = True
            ss['error_state'] = None

            return formatted
        except ValueError as e:
            # Calculation error (e.g., division by zero or malformed)
            try:
                ss['error_state'] = str(e)
            except Exception:
                pass
            try:
                ss['display_value'] = 'Error'
            except Exception:
                pass
            try:
                ss['current_input'] = '0'
                ss['previous_value'] = ""
                ss['operator'] = None
                ss['waiting_for_operand'] = True
            except Exception:
                pass
            try:
                print('Component:', e)
            except Exception:
                pass
            # Do not append failed calculation to history
            return '0'
    except Exception as e:
        try:
            print('Component:', e)
        except Exception:
            pass
        # Best-effort fallback
        return st.session_state.get('current_input', '0')


def _handle_digit(digit: str) -> None:
    """Handle digit or decimal point input, updating session state.

    Rules:
    - If waiting_for_operand is True, start a new current_input with the digit.
    - Prevent multiple decimal points.
    - Replace leading '0' with a non-zero digit.
    - Update display_value to reflect current_input.
    """
    try:
        if digit not in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", '.'}:
            return

        ss = st.session_state

        # If we are waiting for the next operand, begin a new input
        if ss.get('waiting_for_operand'):
            if digit == '.':
                ss['current_input'] = '0.'
            else:
                ss['current_input'] = digit
            ss['waiting_for_operand'] = False
            ss['display_value'] = ss['current_input']
            return

        # Not waiting: append or manage decimal/leading zero rules
        current = ss.get('current_input', '0')

        if digit == '.':
            if '.' in current:
                # ignore additional decimal points
                return
            # append decimal point
            ss['current_input'] = current + '.'
            ss['display_value'] = ss['current_input']
            return

        # digit is 0-9
        if current == '0':
            # Replace leading zero unless digit is also zero
            if digit == '0':
                ss['current_input'] = '0'
            else:
                ss['current_input'] = digit
        else:
            ss['current_input'] = current + digit

        ss['display_value'] = ss['current_input']
    except Exception as e:
        try:
            print('Component:', e)
        except Exception:
            pass
        try:
            st.session_state['error_state'] = 'digit_handler_error'
        except Exception:
            pass


def _handle_operator(op: str) -> None:
    """Handle operator selection, managing previous_value, operator, and waiting flag.

    If there is a pending operation, invoke _perform_calculation to enable chaining.
    """
    try:
        if op not in {'+', '-', '×', '÷'}:
            return

        ss = st.session_state
        prev = ss.get('previous_value', '')
        curr = ss.get('current_input', '0')
        existing_op = ss.get('operator')

        if not prev:
            # No previous value recorded, set it from current input
            ss['previous_value'] = curr
        else:
            # There is a previous value; if there's an existing operator, perform pending calculation
            if existing_op:
                # Perform calculation and update previous_value with result
                result = _perform_calculation()
                ss['previous_value'] = result

        ss['operator'] = op
        ss['waiting_for_operand'] = True
        # update display to show the previous value (or current if prev absent)
        ss['display_value'] = ss.get('previous_value') or ss.get('current_input')
    except Exception as e:
        try:
            print('Component:', e)
        except Exception:
            pass
        try:
            st.session_state['error_state'] = 'operator_handler_error'
        except Exception:
            pass


def render_calculator() -> None:
    """Render a minimal calculator UI using session state and wire inputs.

    Buttons for digits and operators call helper handlers to mutate session state.
    """
    try:
        _init_session_state()
        _inject_styles()

        # Styled Display area: always show current display_value
        try:
            disp = st.session_state.get('display_value', '0')
            st.markdown(f"<div class=\"calc-display\">{disp}</div>", unsafe_allow_html=True)
        except Exception as e:
            # Defensive logging similar to existing patterns
            try:
                print('Component:', e)
            except Exception:
                pass
            # fallback to write for compatibility
            try:
                st.write(st.session_state.get('display_value', '0'))
            except Exception:
                pass

        # Layout buttons in rows using columns to approximate iOS layout
        try:
            rows = [
                ['AC', '±', '%', '÷'],
                ['7', '8', '9', '×'],
                ['4', '5', '6', '-'],
                ['1', '2', '3', '+'],
            ]

            for row in rows:
                cols = st.columns(4)
                for i, label in enumerate(row):
                    try:
                        if cols[i].button(label):
                            try:
                                if label == 'AC':
                                    _clear_state()
                                elif label == '±':
                                    # toggle sign of current input when possible
                                    ss = st.session_state
                                    curr = ss.get('current_input', '0')
                                    if curr and curr != '0':
                                        if curr.startswith('-'):
                                            ss['current_input'] = curr[1:]
                                        else:
                                            ss['current_input'] = '-' + curr
                                        ss['display_value'] = ss['current_input']
                                elif label == '%':
                                    # simple percent: divide current input by 100
                                    ss = st.session_state
                                    try:
                                        val = _parser.evaluate_expression(ss.get('current_input', '0') + ' / 100')
                                        ss['current_input'] = _calculator.format_result(val)
                                        ss['display_value'] = ss['current_input']
                                    except Exception:
                                        # fallback: noop
                                        pass
                                elif label in {'+', '-', '×', '÷'}:
                                    _handle_operator(label)
                                else:
                                    # digits handled here too though digits unlikely in this row
                                    _handle_digit(label)
                            except Exception as e:
                                try:
                                    print('Component:', e)
                                except Exception:
                                    pass
                                st.session_state['error_state'] = 'button_click_error'
                    except Exception as e:
                        try:
                            print('Component:', e)
                        except Exception:
                            pass

            # Last row: make 0 wide by using three columns ratios
            cols = st.columns([2, 1, 1])
            # 0 spans first (wide)
            if cols[0].button('0'):
                try:
                    _handle_digit('0')
                except Exception as e:
                    try:
                        print('Component:', e)
                    except Exception:
                        pass
                    st.session_state['error_state'] = 'digit_click_error'

            # dot
            if cols[1].button('.'):
                try:
                    _handle_digit('.')
                except Exception as e:
                    try:
                        print('Component:', e)
                    except Exception:
                        pass
                    st.session_state['error_state'] = 'digit_click_error'

            # equals
            if cols[2].button('='):
                try:
                    _perform_calculation()
                except Exception as e:
                    try:
                        print('Component:', e)
                    except Exception:
                        pass
                    st.session_state['error_state'] = 'equals_click_error'

        except Exception as e:
            try:
                print('Component:', e)
            except Exception:
                pass

        # Render calculation history if present
        try:
            history = st.session_state.get('calculation_history', [])
            if history:
                st.write('History')
                for item in history:
                    expr = item.get('expression')
                    res = item.get('result')
                    try:
                        st.write(f"{expr} = {res}")
                    except Exception:
                        # best-effort: fallback to writing raw item
                        try:
                            st.write(item)
                        except Exception:
                            pass
        except Exception as e:
            try:
                print('Component:', e)
            except Exception:
                pass

    except Exception as e:
        # Catch unexpected errors during UI rendering
        try:
            print('Component:', e)
        except Exception:
            pass
        # try to reflect error in session state
        try:
            st.session_state['error_state'] = str(e)
        except Exception:
            pass


if __name__ == "__main__":
    # Only run the UI when executed as a script. Tests should import and
    # explicitly call render_calculator() to exercise UI logic deterministically.
    render_calculator()
