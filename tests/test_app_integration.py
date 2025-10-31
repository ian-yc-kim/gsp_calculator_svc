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
        self.writes = []
        # emulate streamlit.session_state as a simple dict
        self.session_state = {}
        # controls for simulating button clicks
        self._click_labels = set()
        self._clicked_labels = set()

    def set_page_config(self, **kwargs):
        self.page_config = kwargs

    def title(self, *args, **kwargs):
        self.titles.append((args, kwargs))

    def header(self, *args, **kwargs):
        self.headers.append((args, kwargs))

    def write(self, *args, **kwargs):
        self.writes.append((args, kwargs))

    def button(self, label):
        # Simulate click only if label is configured in _click_labels
        if label in self._click_labels and label not in self._clicked_labels:
            self._clicked_labels.add(label)
            return True
        return False


@pytest.fixture(autouse=True)
def clear_app_module():
    # Ensure fresh import for each test
    if 'app' in sys.modules:
        del sys.modules['app']
    yield
    if 'app' in sys.modules:
        del sys.modules['app']


def test_session_state_initialized_defaults(monkeypatch):
    fake = FakeStreamlit()
    # inject fake streamlit before importing app
    monkeypatch.setitem(sys.modules, 'streamlit', fake)

    mod = importlib.import_module('app')

    # Call render to initialize session state
    mod.render_calculator()

    ss = fake.session_state
    assert ss.get('current_input') == "0"
    assert ss.get('previous_value') == ""
    assert ss.get('operator') is None
    assert ss.get('waiting_for_operand') is True
    assert ss.get('display_value') == "0"
    assert isinstance(ss.get('calculation_history'), list)
    assert ss.get('error_state') is None


def test_ac_button_clears_state(monkeypatch):
    fake = FakeStreamlit()
    # pre-populate with non-default values
    fake.session_state.update({
        'current_input': '123',
        'previous_value': '5',
        'operator': '+',
        'waiting_for_operand': False,
        'display_value': '123',
        'calculation_history': [{'expr': '1+1', 'result': '2'}],
        'error_state': 'some_error',
    })

    # configure the fake to simulate clicking AC
    fake._click_labels.add('AC')

    monkeypatch.setitem(sys.modules, 'streamlit', fake)

    mod = importlib.import_module('app')
    mod.render_calculator()

    ss = fake.session_state
    # after AC, values should be reset to defaults
    assert ss.get('current_input') == "0"
    assert ss.get('previous_value') == ""
    assert ss.get('operator') is None
    assert ss.get('waiting_for_operand') is True
    assert ss.get('display_value') == "0"
    assert ss.get('calculation_history') == []
    assert ss.get('error_state') is None


def test_display_shows_display_value_on_render(monkeypatch):
    fake = FakeStreamlit()
    monkeypatch.setitem(sys.modules, 'streamlit', fake)

    mod = importlib.import_module('app')
    mod.render_calculator()

    # ensure the display_value was written to the UI
    # first write arguments should include the display string '0'
    found = any('0' in str(arg) for call in fake.writes for arg in call[0])
    assert found, f"expected '0' in writes but got {fake.writes}"
