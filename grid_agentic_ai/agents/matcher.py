"""Matching utilities for GRID agents.

This module provides:
- `match_targets_to_drugs`: helper to pair targets with drug data.
- `MatcherAgent`: rule-based matcher combining parsed queries with retrieved data.
"""

from __future__ import annotations
from typing import List, Dict, Any


def match_targets_to_drugs(targets: List[Dict], drug_data: List[Dict]) -> List[Dict]:
    """Match targets with drugs based on overlapping target IDs.

    Args:
        targets: List of dictionaries with keys ``id``, ``approvedSymbol``, and optional ``score``.
        drug_data: List of dictionaries with keys ``targetId``, ``drugName``, and optional ``status``.

    Returns:
        List of matched target-drug dictionaries sorted by score descending.
    """
    matches: List[Dict] = []
    for target in targets:
        for drug in drug_data:
            if drug.get("targetId") == target.get("id"):
                matches.append({
                    "target": target.get("approvedSymbol"),
                    "drug": drug.get("drugName"),
                    "status": drug.get("status"),
                    "score": target.get("score", 0)
                })
    return sorted(matches, key=lambda x: x["score"], reverse=True)


class MatcherAgent:
    """Rule-based matcher for combining parsed queries with retrieved data."""

    def match(self, parsed_query: Dict[str, Any], retrieved_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return a filtered result set based on the query type.

        Parameters
        ----------
        parsed_query:
            Structured query as produced by ``QueryParserAgent``.
        retrieved_data:
            Dictionary of previously retrieved data relevant to the query.
        """

        action = parsed_query.get("action")
        entity_type = parsed_query.get("entity_type")
        filters = parsed_query.get("filters", {})

        if action in {"list", "find"} and entity_type == "disease" and "phase" in filters:
            phase = str(filters["phase"]).lower()
            diseases = []
            for d in retrieved_data.get("diseases", []):
                status = str(d.get("status", d.get("phase", ""))).lower()
                if phase in status:
                    diseases.append(d)
            return {"diseases_by_phase": diseases}

        if action in {"list", "find"} and entity_type == "drug" and "phase" in filters:
            phase = str(filters["phase"]).lower()
            drug_name = parsed_query.get("entity")
            trials = []
            for t in retrieved_data.get("trials", []):
                if t.get("drug") != drug_name:
                    continue
                status = str(t.get("status", t.get("phase", ""))).lower()
                if phase in status:
                    trials.append(t)
            return {"trials_by_drug_phase": trials}

        if entity_type == "target" and filters.get("snp"):
            targets = [t for t in retrieved_data.get("targets", []) if t.get("snps")]
            return {"targets_with_snps": targets}

        if entity_type in {"target", "gene"} and retrieved_data.get("expression_data") is not None:
            tissue = filters.get("tissue")
            threshold = float(filters.get("expression_threshold", 0))
            expr_matches = [
                rec
                for rec in retrieved_data.get("expression_data", [])
                if (tissue is None or rec.get("tissue") == tissue)
                and rec.get("expression") is not None
                and float(rec.get("expression")) >= threshold
            ]
            return {"expression_data": expr_matches}

        if entity_type in {"target", "gene"} and retrieved_data.get("targets") is not None:
            if "expression_threshold" in filters:
                threshold = float(filters["expression_threshold"])
                results = [
                    {
                        "target": t.get("id"),
                        "expression": t.get("expression"),
                    }
                    for t in retrieved_data.get("targets", [])
                    if t.get("expression") is not None and float(t.get("expression")) >= threshold
                ]
            else:
                results = [
                    {
                        "target": t.get("id"),
                        "expression": t.get("expression"),
                    }
                    for t in retrieved_data.get("targets", [])
                    if t.get("expression") is not None
                ]
            return {"gene_expression": results}

        return {"message": "Query type not supported"}
