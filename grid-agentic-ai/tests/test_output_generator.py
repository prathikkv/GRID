import sys
import os
from importlib import reload
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents import output_generator
from agents.output_generator import OutputGeneratorAgent


def test_to_csv_without_pandas(tmp_path, monkeypatch):
    monkeypatch.setattr(output_generator, 'pd', None)
    agent = OutputGeneratorAgent()
    data = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
    out = tmp_path / 'out.csv'
    agent.to_csv(data, str(out))
    contents = out.read_text().strip().splitlines()
    assert contents[0] == 'a,b'
    assert contents[1] == '1,2'
    assert contents[2] == '3,4'


def test_to_json(tmp_path):
    agent = OutputGeneratorAgent()
    data = {'x': 1}
    out = tmp_path / 'out.json'
    agent.to_json(data, str(out))
    assert out.read_text().strip().startswith('{')


def test_to_table_no_pandas(monkeypatch):
    monkeypatch.setattr(output_generator, 'pd', None)
    agent = OutputGeneratorAgent()
    data = [{'a': 1, 'b': 2}]
    table = agent.to_table(data)
    assert 'a' in table and 'b' in table
    assert '1' in table and '2' in table


def test_plot_network_no_deps(tmp_path, monkeypatch):
    monkeypatch.setattr(output_generator, 'nx', None)
    monkeypatch.setattr(output_generator, 'plt', None)
    agent = OutputGeneratorAgent()
    out = tmp_path / 'graph.png'
    agent.plot_network(['A'], [('A','A')], str(out))
    assert not out.exists()
