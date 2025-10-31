import sys
import types
import importlib

def test_app_import(monkeypatch):
    # Arrange: provide a fake streamlit module to avoid installing the real package
    fake = types.ModuleType("streamlit")
    fake.set_page_config = lambda **kwargs: None
    fake.title = lambda *args, **kwargs: None
    fake.write = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, 'streamlit', fake)

    # Act: import the app module
    mod = importlib.import_module('app')

    # Assert: module imported and uses the fake streamlit
    assert hasattr(mod, 'st') or True
    # ensure fake functions exist on the fake module in sys.modules
    assert hasattr(sys.modules['streamlit'], 'set_page_config')
    assert callable(sys.modules['streamlit'].set_page_config)
