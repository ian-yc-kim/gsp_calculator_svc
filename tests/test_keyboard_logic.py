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


def test_inject_keyboard_handlers_includes_percent_key():
    # Prepare fake streamlit and fake components to capture injected HTML/JS
    fake = FakeStreamlit()

    # Create a fake components.v1 module with html function capturing content
    captured = {}
    comp_pkg = types.ModuleType('streamlit.components')
    comp_v1 = types.ModuleType('streamlit.components.v1')

    def html_func(content, height=0):
        # store the injected content so test can inspect it
        captured['html'] = content
        return None

    comp_v1.html = html_func

    # Insert into sys.modules so import inside _inject_keyboard_handlers works
    sys.modules['streamlit'] = fake
    sys.modules['streamlit.components'] = comp_pkg
    sys.modules['streamlit.components.v1'] = comp_v1

    # Import app and call injector
    if 'app' in sys.modules:
        del sys.modules['app']
    app = importlib.import_module('app')

    # Call the injection function which should use our fake components.html
    app._inject_keyboard_handlers()

    # Ensure something was injected
    assert 'html' in captured and isinstance(captured['html'], str)

    js = captured['html']
    # Check that percent key branch exists
    assert "key === '%'" in js
    # Check that findButtonByLabel is referenced so aria-label support is used
    assert 'findButtonByLabel' in js
    # Check the event listener is added
    assert 'window.addEventListener' in js
