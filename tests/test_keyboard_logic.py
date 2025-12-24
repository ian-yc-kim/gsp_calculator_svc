import sys
import types
import importlib


class FakeStreamlit(types.ModuleType):
    def __init__(self):
        super().__init__("streamlit")
        # emulate streamlit.session_state as a simple dict
        self.session_state = {}
        # controls for simulating button clicks
        self._click_labels = set()
        self._clicked_labels = set()

    def set_page_config(self, **kwargs):
        pass

    def write(self, *args, **kwargs):
        pass

    def markdown(self, *args, **kwargs):
        pass

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


def test_backspace_multidigit():
    fake = FakeStreamlit()
    fake.session_state.update({'current_input': '123', 'display_value': '123', 'waiting_for_operand': False})
    app = _fresh_import_app(fake)

    app._handle_backspace()

    ss = fake.session_state
    assert ss.get('current_input') == '12'
    assert ss.get('display_value') == '12'


def test_backspace_single_digit_to_zero():
    fake = FakeStreamlit()
    fake.session_state.update({'current_input': '7', 'display_value': '7', 'waiting_for_operand': False})
    app = _fresh_import_app(fake)

    app._handle_backspace()

    ss = fake.session_state
    assert ss.get('current_input') == '0'
    assert ss.get('display_value') == '0'


def test_backspace_from_zero_remains_zero():
    fake = FakeStreamlit()
    fake.session_state.update({'current_input': '0', 'display_value': '0', 'waiting_for_operand': False})
    app = _fresh_import_app(fake)

    app._handle_backspace()

    ss = fake.session_state
    assert ss.get('current_input') == '0'
    assert ss.get('display_value') == '0'


def test_backspace_while_waiting_resets_to_zero():
    fake = FakeStreamlit()
    fake.session_state.update({'current_input': '999', 'display_value': '999', 'waiting_for_operand': True})
    app = _fresh_import_app(fake)

    app._handle_backspace()

    ss = fake.session_state
    assert ss.get('current_input') == '0'
    assert ss.get('display_value') == '0'


def test_backspace_negative_edge_case():
    fake = FakeStreamlit()
    fake.session_state.update({'current_input': '-1', 'display_value': '-1', 'waiting_for_operand': False})
    app = _fresh_import_app(fake)

    app._handle_backspace()

    ss = fake.session_state
    # Removing last char leaves '-' -> normalize to '0'
    assert ss.get('current_input') == '0'
    assert ss.get('display_value') == '0'
