import sys
import os
from importlib import reload

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.summarizer import SummarizerAgent


def test_summary_empty():
    agent = SummarizerAgent()
    assert agent.summarize({}) == "No results to summarize."


def test_summary_trials_by_phase():
    agent = SummarizerAgent()
    res = agent.summarize({"trials_by_drug_phase": [{"drug": "DrugA", "phase": "2"}]})
    assert res == "Found 1 trial(s) for DrugA in phase 2."


def test_summary_targets_with_snps():
    agent = SummarizerAgent()
    res = agent.summarize({"targets_with_snps": [{"id": "T1", "snps": ["rs1"]}]})
    assert res == "Targets with SNP annotations: T1."


def test_summary_expression():
    agent = SummarizerAgent()
    res = agent.summarize({"gene_expression": [{"target": "T1", "expression": 5}]})
    assert res == "Protein expression levels: T1 (5)."
