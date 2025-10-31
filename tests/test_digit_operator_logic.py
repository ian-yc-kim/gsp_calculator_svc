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


def test_digit_entry_updates_current_input_and_display():
    fake = FakeStreamlit()
    # configure clicks for digits 1,2,3
    fake._click_labels.update({'1', '2', '3'})
    app = _fresh_import_app(fake)

    app.render_calculator()

    ss = fake.session_state
    assert ss.get('current_input') == '123'
    assert ss.get('display_value') == '123'
    assert ss.get('waiting_for_operand') is False


def test_decimal_point_only_once():
    fake = FakeStreamlit()
    # prepopulate session state to simulate existing decimal
    fake.session_state.update({'current_input': '1.2', 'waiting_for_operand': False, 'display_value': '1.2'})
    # attempt to add another decimal point
    fake._click_labels.add('.')
    app = _fresh_import_app(fake)

    app.render_calculator()

    ss = fake.session_state
    assert ss.get('current_input') == '1.2'
    assert ss.get('display_value') == '1.2'


def test_initial_zero_replacement():
    fake = FakeStreamlit()
    # starting defaults should be used
    fake._click_labels.add('5')
    app = _fresh_import_app(fake)

    app.render_calculator()

    ss = fake.session_state
    assert ss.get('current_input') == '5'
    assert ss.get('display_value') == '5'


def test_operator_after_number_sets_previous_and_waiting():
    fake = FakeStreamlit()
    # enter 4 then 2 then +
    fake._click_labels.update({'4', '2', '+'})
    app = _fresh_import_app(fake)

    app.render_calculator()

    ss = fake.session_state
    assert ss.get('previous_value') == '42'
    assert ss.get('operator') == '+'
    assert ss.get('waiting_for_operand') is True
    assert ss.get('display_value') == '42'


def test_digit_operator_digit_sequence():
    fake = FakeStreamlit()
    # sequence: 3 + 5
    fake._click_labels.update({'3', '+', '5'})
    app = _fresh_import_app(fake)

    app.render_calculator()

    ss = fake.session_state
    assert ss.get('previous_value') == '3'
    assert ss.get('operator') == '+'
    assert ss.get('current_input') == '5'
    assert ss.get('display_value') == '5'
    assert ss.get('waiting_for_operand') is False


def test_chained_operator_initiates_pending_calculation():
    fake = FakeStreamlit()
    # sequence: 3 + 5 - (clicking another operator triggers placeholder calc)
    fake._click_labels.update({'3', '+', '5', '-'})
    app = _fresh_import_app(fake)

    app.render_calculator()

    ss = fake.session_state
    # operator should be updated to the last one
    assert ss.get('operator') == '-'
    assert ss.get('waiting_for_operand') is True
    # previous_value should not be empty after chaining
    assert ss.get('previous_value') != ''
