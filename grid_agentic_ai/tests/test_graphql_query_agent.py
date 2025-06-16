import os
import sys
import types
from importlib import reload

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from grid_agentic_ai.agents import graphql_query_agent as gqa


def setup_fake_llama(monkeypatch):
    fake_pkg = types.ModuleType('llama_index')
    fake_core = types.ModuleType('llama_index.core')

    class FakeIndex:
        def __init__(self, docs):
            self.docs = docs
        def as_query_engine(self, similarity_top_k=3):
            class Engine:
                def query(self_inner, q):
                    return 'schema context'
            return Engine()

    fake_core.Document = lambda text: {'text': text}
    fake_core.VectorStoreIndex = types.SimpleNamespace(from_documents=lambda docs: FakeIndex(docs))
    fake_pkg.core = fake_core
    monkeypatch.setitem(sys.modules, 'llama_index', fake_pkg)
    monkeypatch.setitem(sys.modules, 'llama_index.core', fake_core)


def setup_fake_ollama(monkeypatch):
    fake = types.ModuleType('ollama')
    def fake_chat(model=None, messages=None):
        return {'message': {'content': 'query { id }'}}
    fake.chat = fake_chat
    monkeypatch.setitem(sys.modules, 'ollama', fake)


def test_generate_query(monkeypatch, tmp_path):
    setup_fake_llama(monkeypatch)
    setup_fake_ollama(monkeypatch)
    reload(gqa)

    schema_file = tmp_path / 'schema.graphql'
    schema_file.write_text('type Query { id: ID }')

    result = gqa.generate_query('Get id', str(schema_file))
    assert 'query' in result


def test_generate_query_no_deps(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, 'llama_index', None)
    monkeypatch.setitem(sys.modules, 'llama_index.core', None)
    monkeypatch.setitem(sys.modules, 'ollama', None)
    reload(gqa)

    schema_file = tmp_path / 'schema.graphql'
    schema_file.write_text('type Query { id: ID }')

    result = gqa.generate_query('Get id', str(schema_file))
    assert result == ''
