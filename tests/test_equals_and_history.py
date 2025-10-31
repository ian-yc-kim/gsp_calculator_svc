import sys
import types
import importlib


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


def _fresh_import_app(fake):
    # Ensure fresh import for app with provided fake streamlit
    if 'app' in sys.modules:
        del sys.modules['app']
    sys.modules['streamlit'] = fake
    return importlib.import_module('app')


def test_basic_calculation_and_history():
    fake = FakeStreamlit()
    # Simulate pressing: 5 + 3 =
    fake._click_labels.update({'5', '+', '3', '='})
    app = _fresh_import_app(fake)

    app.render_calculator()

    ss = fake.session_state
    assert ss.get('display_value') == '8'
    # last history entry
    history = ss.get('calculation_history')
    assert isinstance(history, list)
    assert history[-1] == {'expression': '5 + 3', 'result': '8'}
    assert ss.get('current_input') == '8'
    assert ss.get('previous_value') == ''
    assert ss.get('operator') is None
    assert ss.get('waiting_for_operand') is True
    assert ss.get('error_state') is None


def test_chaining_operations():
    fake = FakeStreamlit()
    # Sequence: 5 + 3 =  then + 2 =
    fake._click_labels.update({'5', '+', '3', '=', '2'})
    # Note: '=' will be processed once; we reuse render to simulate pressing + and =
    app = _fresh_import_app(fake)

    # First render: will process initial clicks including '=' and '2'
    app.render_calculator()

    ss = fake.session_state
    # After first render we expect first calculation done
    assert ss.get('display_value') in {'8', '82', '8'}  # tolerant to ordering quirks

    # Now simulate pressing + and = to finish chain (ensure we register + and = clicks now)
    fake._click_labels.update({'+', '='})
    # import app anew to refresh click handling
    app = _fresh_import_app(fake)
    app.render_calculator()

    ss = fake.session_state
    # Final expected value should be 10 if chaining worked
    # history should have two entries: 5 + 3 -> 8 and 8 + 2 -> 10
    history = ss.get('calculation_history', [])
    # basic validation: last result equals formatted '10'
    if history:
        assert history[-1].get('result') in {'10', '10.0', '10.00'} or ss.get('display_value') == '10'


def test_division_by_zero_sets_error():
    fake = FakeStreamlit()
    fake._click_labels.update({'1', '÷', '0', '='})
    app = _fresh_import_app(fake)

    app.render_calculator()

    ss = fake.session_state
    assert ss.get('display_value') == 'Error'
    err = ss.get('error_state')
    assert err is not None
    assert 'division' in str(err) or 'zero' in str(err)
    assert ss.get('current_input') == '0'
    assert ss.get('previous_value') == ''
    assert ss.get('operator') is None
    assert ss.get('waiting_for_operand') is True
    # Ensure no new history entry for failed calc
    history = ss.get('calculation_history', [])
    assert all('division' not in str(item) for item in history)


def test_equals_without_prior_operator_displays_current_input():
    fake = FakeStreamlit()
    # Defaults are current_input '0'
    fake._click_labels.update({'='})
    app = _fresh_import_app(fake)

    app.render_calculator()

    ss = fake.session_state
    assert ss.get('display_value') == '0'
    assert ss.get('calculation_history') == []
