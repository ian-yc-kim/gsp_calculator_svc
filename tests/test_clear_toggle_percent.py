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
        self.markdowns = []
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

    def markdown(self, *args, **kwargs):
        self.markdowns.append((args, kwargs))

    def button(self, label):
        # Simulate click only if label is configured in _click_labels
        if label in self._click_labels and label not in self._clicked_labels:
            self._clicked_labels.add(label)
            return True
        return False


def _fresh_import_app(fake):
    # Ensure fresh import for app with provided fake streamlit
    if 'app' in sys.modules:
        del sys.modules['app']
    sys.modules['streamlit'] = fake
    return importlib.import_module('app')


def test_clear_entry_clears_current_input_and_display_only(monkeypatch):
    fake = FakeStreamlit()
    # enter 1,2,3 then C
    fake._click_labels.update({'1', '2', '3', 'C'})
    app = _fresh_import_app(fake)

    app.render_calculator()

    ss = fake.session_state
    assert ss.get('current_input') == '0'
    assert ss.get('display_value') == '0'

    # Now sequence with previous/operator preserved: 4,5,6, +, 7,8,9, C
    fake = FakeStreamlit()
    fake._click_labels.update({'4', '5', '6', '+', '7', '8', '9', 'C'})
    app = _fresh_import_app(fake)

    app.render_calculator()

    ss = fake.session_state
    assert ss.get('display_value') == '0'
    # previous_value should still be '456' and operator be '+'
    assert ss.get('previous_value') == '456'
    assert ss.get('operator') == '+'


def test_toggle_sign_behaviour(monkeypatch):
    fake = FakeStreamlit()
    # enter 1,2,3 then ± once
    fake._click_labels.update({'1', '2', '3', '±'})
    app = _fresh_import_app(fake)
    app.render_calculator()

    ss = fake.session_state
    assert ss.get('display_value') == '-123' or ss.get('current_input') == '-123'

    # simulate pressing ± again by allowing the label to be clickable again
    # clear clicked labels so button can be clicked again and set the label
    fake._clicked_labels.discard('±')
    fake._click_labels = {'±'}
    # call render again (state persists in fake.session_state)
    app.render_calculator()

    ss = fake.session_state
    # toggled back to positive
    assert ss.get('display_value') == '123' or ss.get('current_input') == '123'

    # Test 0 toggles remain 0
    fake = FakeStreamlit()
    fake.session_state.update({'current_input': '0', 'display_value': '0', 'waiting_for_operand': False})
    fake._click_labels.add('±')
    app = _fresh_import_app(fake)
    app.render_calculator()

    ss = fake.session_state
    assert ss.get('display_value') == '0'


def test_percentage_behaviour(monkeypatch):
    # 200 -> 2
    fake = FakeStreamlit()
    fake._click_labels.update({'2', '0', '0', '%'})
    app = _fresh_import_app(fake)
    app.render_calculator()

    ss = fake.session_state
    assert ss.get('display_value') == '2' or ss.get('current_input') == '2'

    # 50 -> 0.5
    fake = FakeStreamlit()
    fake._click_labels.update({'5', '0', '%'})
    app = _fresh_import_app(fake)
    app.render_calculator()

    ss = fake.session_state
    assert ss.get('display_value') == '0.5' or ss.get('current_input') == '0.5'

    # 0 -> 0
    fake = FakeStreamlit()
    fake.session_state.update({'current_input': '0', 'display_value': '0', 'waiting_for_operand': False})
    fake._click_labels.add('%')
    app = _fresh_import_app(fake)
    app.render_calculator()

    ss = fake.session_state
    assert ss.get('display_value') == '0' or ss.get('current_input') == '0'
