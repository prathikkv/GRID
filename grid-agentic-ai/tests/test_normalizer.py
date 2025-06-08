import sys
import os
from importlib import reload
import types

# Ensure repo root in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Provide placeholder modules if requests or pubchempy are missing
if 'requests' not in sys.modules:
    requests_mod = types.ModuleType('requests')
    requests_mod.get = lambda *a, **k: None
    sys.modules['requests'] = requests_mod

if 'pubchempy' not in sys.modules:
    pcp_mod = types.ModuleType('pubchempy')
    pcp_mod.get_compounds = lambda *a, **k: []
    sys.modules['pubchempy'] = pcp_mod

import requests
from agents import normalizer

class FakeResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json


def test_normalize_drug(monkeypatch):
    fake_pcp = types.ModuleType('pubchempy')
    fake_pcp.get_compounds = lambda q, t: [types.SimpleNamespace(cid=999)]
    monkeypatch.setitem(sys.modules, 'pubchempy', fake_pcp)
    reload(normalizer)
    res = normalizer.normalize_term('drug', 'Aspirin')
    assert res['resolved_id'] == 999
    assert res['source'] == 'PubChem'


def test_normalize_gene(monkeypatch):
    def fake_get(url):
        return FakeResponse({'hits': [{'_id': '1', 'symbol': 'TEST'}]})
    monkeypatch.setattr(requests, 'get', fake_get)
    reload(normalizer)
    res = normalizer.normalize_term('gene', 'test')
    assert res['resolved_id'] == 'TEST'
    assert res['entrez_id'] == '1'


def test_normalize_disease(monkeypatch):
    def fake_get(url):
        return FakeResponse({'response': {'numFound': 1, 'docs': [{'obo_id': 'EFO:1', 'label': 'Disease'}]}})
    monkeypatch.setattr(requests, 'get', fake_get)
    reload(normalizer)
    res = normalizer.normalize_term('disease', 'dis')
    assert res['resolved_id'] == 'EFO:1'
    assert res['source'] == 'OLS/EFO'


def test_unknown_type():
    reload(normalizer)
    res = normalizer.normalize_term('foo', 'bar')
    assert res['resolved_id'] is None
