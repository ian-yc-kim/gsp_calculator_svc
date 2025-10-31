import sys
import types
import importlib
import pytest


class FakeStreamlit(types.ModuleType):
    def __init__(self):
        super().__init__("streamlit")
        # captured UI state
        self.page_config = None
        self.titles = []
        self.headers = []
        self.inputs = {}
        self.success_messages = []
        self.error_messages = []
        self.writes = []
        self._button_clicked = False

    def set_page_config(self, **kwargs):
        self.page_config = kwargs

    def title(self, *args, **kwargs):
        self.titles.append((args, kwargs))

    def header(self, *args, **kwargs):
        self.headers.append((args, kwargs))

    def write(self, *args, **kwargs):
        self.writes.append((args, kwargs))

    def text_input(self, label, key=None):
        # return the pre-configured input value or empty string
        return self.inputs.get(key, "")

    def button(self, label):
        # simulate a single click per test invocation
        if not self._button_clicked:
            self._button_clicked = True
            return True
        return False

    def success(self, msg):
        self.success_messages.append(msg)

    def error(self, msg):
        self.error_messages.append(msg)


@pytest.mark.parametrize(
    "expr,expected",
    [
        ("5 + 3", "8"),
        ("10 / 2", "5"),
        ("(2 + 3) * 4", "20"),
    ],
)
def test_valid_expressions_display_success(monkeypatch, expr, expected):
    fake = FakeStreamlit()
    # set the input value to the expression under the expected key
    fake.inputs['expression_input'] = expr

    # inject fake streamlit before importing app
    monkeypatch.setitem(sys.modules, 'streamlit', fake)

    # ensure a fresh import so module-level state is deterministic
    if 'app' in sys.modules:
        del sys.modules['app']

    mod = importlib.import_module('app')

    # Explicitly call render_calculator so tests control execution
    mod.render_calculator()

    # Assert success message captured and contains expected formatted value
    assert len(fake.success_messages) == 1, f"no success messages for expr {expr}: {fake.success_messages}"
    # message may contain prefix 'Result: ' so just assert expected appears
    assert expected in fake.success_messages[0]
    # ensure no error messages
    assert not fake.error_messages


@pytest.mark.parametrize(
    "expr,expected_in_message",
    [
        ("abc", "invalid character"),
        ("1 / 0", "division by zero"),
        ("2 + (3", "mismatched"),
    ],
)
def test_invalid_expressions_display_error(monkeypatch, expr, expected_in_message):
    fake = FakeStreamlit()
    fake.inputs['expression_input'] = expr
    monkeypatch.setitem(sys.modules, 'streamlit', fake)

    if 'app' in sys.modules:
        del sys.modules['app']

    mod = importlib.import_module('app')
    mod.render_calculator()

    # Assert an error message was produced
    assert len(fake.error_messages) >= 1, f"expected error message for {expr}"
    joined = " ".join(fake.error_messages)
    assert expected_in_message in joined
