import streamlit as st

from utils.parser import evaluate_expression
from utils.calculator import format_result

try:
    st.set_page_config(layout="wide", page_title="Streamlit Calculator")
except Exception as e:
    # set_page_config may raise if called multiple times; log for debugging
    try:
        print('Component:', e)
    except Exception:
        pass

st.title("Streamlit Calculator")
st.header("Streamlit Calculator")


def render_calculator() -> None:
    """Render a minimal calculator UI and handle calculation events.

    Presents a text input for expressions and a Calculate button. On click,
    evaluates the expression and displays either the formatted result or a
    user-friendly error message.
    """
    expression: str = st.text_input('Enter expression', key='expression_input')
    clicked = st.button('Calculate')

    if clicked:
        try:
            result = evaluate_expression(expression)
            formatted = format_result(result)
            st.success(f"Result: {formatted}")
        except ValueError as e:
            # Show parser/calculator validation and arithmetic errors
            st.error(f"Error: {e}")
        except Exception as e:
            # Log unexpected errors and show a generic message to users
            try:
                print('Component:', e)
            except Exception:
                pass
            st.error("Error: failed to evaluate expression")


if __name__ == "__main__":
    # Only run the UI when executed as a script. Tests should import and
    # explicitly call render_calculator() to exercise UI logic deterministically.
    render_calculator()
