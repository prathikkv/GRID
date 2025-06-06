import sys
import os
from importlib import reload
import types

# Ensure repo root in path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Provide placeholder requests module if missing
if 'requests' not in sys.modules:
    requests_mod = types.ModuleType('requests')
    sys.modules['requests'] = requests_mod
requests_mod = sys.modules['requests']
if not hasattr(requests_mod, 'post'):
    requests_mod.post = lambda *a, **k: None

import requests
from agents import retriever_opentargets as retriever


class FakeResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json


def test_post_success(monkeypatch):
    def fake_post(url, json=None):
        assert url == retriever.OPENTARGETS_URL
        assert json['variables'] == {'x': 1}
        return FakeResponse({'ok': True})

    monkeypatch.setattr(requests, 'post', fake_post)
    reload(retriever)
    res = retriever._post('query', {'x': 1})
    assert res == {'ok': True}


def test_post_no_requests(monkeypatch):
    monkeypatch.setattr(retriever, 'requests', None)
    res = retriever._post('query', {})
    assert res is None


def test_get_targets_for_disease(monkeypatch):
    def fake_post(url, json=None):
        assert 'diseaseTargets' in json['query']
        return FakeResponse({'result': 'disease'})

    monkeypatch.setattr(requests, 'post', fake_post)
    reload(retriever)
    res = retriever.get_targets_for_disease('EFO:1')
    assert res == {'result': 'disease'}


def test_get_diseases_for_drug(monkeypatch):
    def fake_post(url, json=None):
        assert 'drugIndications' in json['query']
        return FakeResponse({'result': 'drug'})

    monkeypatch.setattr(requests, 'post', fake_post)
    reload(retriever)
    res = retriever.get_diseases_for_drug('CHEMBL1')
    assert res == {'result': 'drug'}
