import sys
import os
from importlib import reload

# Ensure repo root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents import matcher
from agents.matcher import MatcherAgent


def test_match_targets_basic():
    targets = [
        {"id": "T1", "approvedSymbol": "A", "score": 0.8},
        {"id": "T2", "approvedSymbol": "B", "score": 0.9},
    ]
    drugs = [
        {"targetId": "T2", "drugName": "DrugB"},
        {"targetId": "T1", "drugName": "DrugA"},
    ]
    result = matcher.match_targets_to_drugs(targets, drugs)
    assert result == [
        {"target": "B", "drug": "DrugB", "status": None, "score": 0.9},
        {"target": "A", "drug": "DrugA", "status": None, "score": 0.8},
    ]


def test_match_targets_empty():
    assert matcher.match_targets_to_drugs([], []) == []
    assert matcher.match_targets_to_drugs([{"id": "T1", "approvedSymbol": "A"}], []) == []


def test_matcher_list_diseases_by_phase():
    agent = MatcherAgent()
    parsed = {"action": "list", "entity_type": "disease", "filters": {"phase": "2"}}
    retrieved = {"diseases": [{"name": "D1", "phase": "1"}, {"name": "D2", "phase": "2"}]}
    result = agent.match(parsed, retrieved)
    assert result == {"diseases_by_phase": [{"name": "D2", "phase": "2"}]}


def test_matcher_targets_with_snps():
    agent = MatcherAgent()
    parsed = {"action": "list", "entity_type": "target", "filters": {"snp": True}}
    retrieved = {"targets": [{"id": "T1", "snps": ["rs1"]}, {"id": "T2", "snps": []}]}
    result = agent.match(parsed, retrieved)
    assert result == {"targets_with_snps": [{"id": "T1", "snps": ["rs1"]}]}


def test_matcher_gene_expression():
    agent = MatcherAgent()
    parsed = {
        "action": "describe",
        "entity_type": "target",
        "filters": {"expression_threshold": 5}
    }
    retrieved = {"targets": [{"id": "T1", "expression": 4}, {"id": "T2", "expression": 6}]}
    result = agent.match(parsed, retrieved)
    assert result == {"gene_expression": [{"target": "T2", "expression": 6}]}


def test_matcher_trials_by_drug_and_phase():
    agent = MatcherAgent()
    parsed = {
        "action": "list",
        "entity_type": "drug",
        "entity": "DrugA",
        "filters": {"phase": "2"},
    }
    retrieved = {
        "trials": [
            {"nct": "1", "drug": "DrugA", "phase": "2"},
            {"nct": "2", "drug": "DrugA", "phase": "3"},
            {"nct": "3", "drug": "DrugB", "phase": "2"},
        ]
    }
    result = agent.match(parsed, retrieved)
    assert result == {
        "trials_by_drug_phase": [{"nct": "1", "drug": "DrugA", "phase": "2"}]
    }


def test_matcher_expression_data_by_tissue():
    agent = MatcherAgent()
    parsed = {
        "action": "describe",
        "entity_type": "target",
        "filters": {"tissue": "liver", "expression_threshold": 5},
    }
    retrieved = {
        "expression_data": [
            {"target": "T1", "tissue": "liver", "expression": 4},
            {"target": "T2", "tissue": "liver", "expression": 6},
            {"target": "T3", "tissue": "brain", "expression": 10},
        ]
    }
    result = agent.match(parsed, retrieved)
    assert result == {
        "expression_data": [
            {"target": "T2", "tissue": "liver", "expression": 6}
        ]
    }
