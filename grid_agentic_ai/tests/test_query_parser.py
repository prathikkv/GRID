import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from grid_agentic_ai.agents.query_parser import QueryParserAgent

parser = QueryParserAgent()


def test_parse_drug_query():
    res = parser.parse("Find diseases associated with Vemurafenib")
    assert res["entity"] == "Vemurafenib"
    assert res["entity_type"] == "drug"
    assert res["action"] == "find"


def test_parse_gene_query():
    res = parser.parse("Describe gene TP53 expression in mouse")
    assert res["entity"] == "TP53"
    assert res["entity_type"] == "gene"
    assert res["action"] == "describe"
    assert res["filters"].get("species") == "mouse"


def test_parse_disease_query():
    res = parser.parse("Show trials for Crohn's disease phase 2")
    assert res["entity"] == "Crohn's disease"
    assert res["entity_type"] == "disease"
    assert res["filters"].get("phase") == "2"


def test_parse_expression_filter():
    res = parser.parse("List genes with expression >= 2")
    assert res["entity_type"] == "gene"
    assert res["filters"].get("expression_threshold") == "2"


def test_parse_drug_approved_query():
    res = parser.parse("Which diseases is Rituximab approved for?")
    assert res["entity"] == "Rituximab"
    assert res["entity_type"] == "drug"


def test_parse_show_trials_phase_query():
    res = parser.parse("Show trials for Dasatinib in Phase 2")
    assert res["entity"] == "Dasatinib"
    assert res["entity_type"] == "drug"
    assert res["filters"].get("phase") == "2"


def test_parse_list_diseases_for_drug_phase_query():
    res = parser.parse("List the diseases in Phase-2 for Imatinib")
    assert res["entity"] == "Imatinib"
    assert res["entity_type"] == "drug"
    assert res["filters"].get("phase") == "2"
