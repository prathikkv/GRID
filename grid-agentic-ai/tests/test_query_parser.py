import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.query_parser import QueryParserAgent

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
    assert res["filters"].get("expression") == "2"
