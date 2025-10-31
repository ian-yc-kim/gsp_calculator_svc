import streamlit as st

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


def render_calculator() -> None:
    """Render a minimal calculator UI using session state.

    This replaces the legacy text_input and Calculate button with a
    simple display area and an AC (All Clear) button that resets
    calculator state.
    """
    try:
        _init_session_state()

        # Display area: always show current display_value
        try:
            st.write(st.session_state['display_value'])
        except Exception as e:
            # Defensive logging similar to existing patterns
            try:
                print('Component:', e)
            except Exception:
                pass

        # All Clear button clears the calculator state
        if st.button('AC'):
            try:
                _clear_state()
            except Exception as e:
                try:
                    print('Component:', e)
                except Exception:
                    pass
                # set an error state so UI can reflect failure if desired
                st.session_state['error_state'] = 'failed_to_clear'

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
