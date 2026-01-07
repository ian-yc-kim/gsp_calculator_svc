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


@pytest.fixture(autouse=True)
def clear_app_module():
    # Ensure fresh import for each test
    if 'app' in sys.modules:
        del sys.modules['app']
    yield
    if 'app' in sys.modules:
        del sys.modules['app']


def test_history_rendered_in_markdown_above_display(monkeypatch):
    fake = FakeStreamlit()
    fake.session_state['calculation_history'] = [
        {'expression': '1 + 2', 'result': '3'},
        {'expression': '3 × 4', 'result': '12'},
    ]
    monkeypatch.setitem(sys.modules, 'streamlit', fake)

    mod = importlib.import_module('app')
    mod.render_calculator()

    history_idx = None
    display_idx = None

    for i, call in enumerate(fake.markdowns):
        args = call[0]
        for a in args:
            if isinstance(a, str) and 'calc-history-container' in a:
                history_idx = i
            if isinstance(a, str) and 'calc-display' in a:
                display_idx = i

    assert history_idx is not None, f"history container not rendered. markdowns={fake.markdowns}"
    assert display_idx is not None, f"display not rendered. markdowns={fake.markdowns}"
    assert history_idx < display_idx, "History should appear before main display"

    # ensure history items content present
    joined = ' '.join(a for call in fake.markdowns for a in call[0] if isinstance(a, str))
    assert '1 + 2 = 3' in joined
    assert '3 × 4 = 12' in joined


def test_no_history_does_not_render_history_container(monkeypatch):
    fake = FakeStreamlit()
    fake.session_state['calculation_history'] = []
    monkeypatch.setitem(sys.modules, 'streamlit', fake)

    mod = importlib.import_module('app')
    mod.render_calculator()

    found = False
    for call in fake.markdowns:
        for a in call[0]:
            if isinstance(a, str) and 'calc-history-container' in a:
                found = True
    assert not found, "History container must not render when history is empty"
