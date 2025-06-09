import sys
import os
from importlib import reload
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Provide placeholder requests module if missing
if 'requests' not in sys.modules:
    requests_mod = types.ModuleType('requests')
    sys.modules['requests'] = requests_mod
requests_mod = sys.modules['requests']
if not hasattr(requests_mod, 'post'):
    requests_mod.post = lambda *a, **k: None
if not hasattr(requests_mod, 'exceptions'):
    exc_mod = types.SimpleNamespace(RequestException=Exception)
    requests_mod.exceptions = exc_mod

import requests
from grid_agentic_ai.agents import retriever_opentargets as retriever


class FakeResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.RequestException('error')


def test_post_success(monkeypatch):
    def fake_post(url, json=None, timeout=None):
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


def test_post_retry_success(monkeypatch):
    calls = {'c': 0}

    def fake_post(url, json=None, timeout=None):
        calls['c'] += 1
        if calls['c'] < 3:
            raise requests.exceptions.RequestException('fail')
        return FakeResponse({'ok': True})

    monkeypatch.setattr(requests, 'post', fake_post)
    monkeypatch.setattr(retriever.time, 'sleep', lambda x: None)
    reload(retriever)
    res = retriever._post('query', {'x': 1})
    assert res == {'ok': True}
    assert calls['c'] == 3


def test_post_retry_failure(monkeypatch):
    def fake_post(url, json=None, timeout=None):
        raise requests.exceptions.RequestException('fail')

    monkeypatch.setattr(requests, 'post', fake_post)
    monkeypatch.setattr(retriever.time, 'sleep', lambda x: None)
    reload(retriever)
    res = retriever._post('query', {})
    assert res is None


def test_get_targets_for_disease(monkeypatch):
    def fake_post(url, json=None, timeout=None):
        assert 'GetTargetsForDisease' in json['query']
        return FakeResponse({
            'data': {
                'disease': {
                    'associatedTargets': {
                        'rows': [
                            {
                                'target': {'id': 'T1', 'approvedSymbol': 'BRAF'},
                                'score': 0.8,
                            }
                        ]
                    }
                }
            }
        })

    monkeypatch.setattr(requests, 'post', fake_post)
    reload(retriever)
    res = retriever.get_targets_for_disease('EFO:1')
    assert res['data']['disease']['associatedTargets']['rows'][0]['target']['approvedSymbol'] == 'BRAF'


def test_get_diseases_for_drug(monkeypatch):
    def fake_post(url, json=None, timeout=None):
        assert 'GetDiseasesForDrug' in json['query']
        return FakeResponse({
            'data': {
                'drug': {
                    'indications': {
                        'rows': [
                            {
                                'disease': {'id': 'EFO1', 'name': 'Disease A'},
                                'phase': '2',
                                'status': 'Ongoing'
                            }
                        ]
                    }
                }
            }
        })

    monkeypatch.setattr(requests, 'post', fake_post)
    reload(retriever)
    res = retriever.get_diseases_for_drug('CHEMBL1')
    assert res['data']['drug']['indications']['rows'][0]['disease']['name'] == 'Disease A'


def test_get_trials_for_disease(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        assert 'study_fields' in url
        assert params['expr'] == 'Cancer'
        return FakeResponse({
            'StudyFieldsResponse': {
                'StudyFields': [
                    {
                        'BriefTitle': ['Trial A'],
                        'Phase': ['Phase 2'],
                        'Status': ['Recruiting'],
                    },
                    {
                        'BriefTitle': ['Trial B'],
                        'Phase': ['Phase 1'],
                        'Status': ['Completed'],
                    },
                ]
            }
        })

    monkeypatch.setattr(requests, 'get', fake_get)
    reload(retriever)
    res = retriever.get_trials_for_disease('Cancer', phase='Phase 2')
    assert res == [{'title': 'Trial A', 'phase': 'Phase 2', 'status': 'Recruiting'}]


def test_get_trials_for_disease_error(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        raise requests.exceptions.RequestException('fail')

    monkeypatch.setattr(requests, 'get', fake_get)
    reload(retriever)
    res = retriever.get_trials_for_disease('Cancer')
    assert res == []
