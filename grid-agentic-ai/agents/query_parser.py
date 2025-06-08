"""Simple rule-based parser for GRID queries.

This module defines a ``QueryParserAgent`` class with a ``parse`` method that
extracts structured information from a natural language query. The parsing logic
uses straightforward regular expressions and keyword matching to determine the
requested entity, entity type, action, and optional filters.

Example supported queries::

    - "List drugs targeting BRAF in phase 3 trials"
    - "Find diseases associated with Vemurafenib"
    - "Describe gene TP53 expression in mouse"
    - "Show trials for Crohn's disease phase 2"
    - "List genes with expression > 2"
"""

from __future__ import annotations

import re
from typing import Dict, Any


class QueryParserAgent:
    """Lightweight rule-based query parser."""

    ACTION_KEYWORDS = ["list", "find", "describe", "show", "get", "which"]


    def parse(self, query: str) -> Dict[str, Any]:
        """Parse a natural language query into structured components."""
        text = query.lower()
        action = next((a for a in self.ACTION_KEYWORDS if a in text), "unknown")

        entity_type = None

        entity = None
        patterns = [

            (r"targeting\s+([A-Za-z0-9\-]+)", "target"),
            (r"gene\s+([A-Za-z0-9\-]+)", "gene"),
            (r"drug\s+([A-Za-z0-9\-]+)", "drug"),
            (r"for\s+([A-Za-z0-9' \-]+\sdisease)", "disease"),
            (r"disease\s+([A-Za-z0-9' \-]+)", "disease"),
            (r"associated with\s+([A-Za-z0-9' \-]+)", "drug"),
            (r"trials for\s+([A-Za-z0-9\-]+)", "drug"),
            (r"is\s+([A-Za-z0-9\-]+)\s+approved", "drug"),
            (r"for\s+([A-Za-z0-9\-]+)\s+in\s+phase", "drug"),

        ]
        for pat, etype in patterns:
            m = re.search(pat, query, re.I)
            if m:
                entity = re.sub(r"\s+phase.*", "", m.group(1)).strip()
                entity_type = etype
                break

        if entity_type is None:
            if "drug" in text:
                entity_type = "drug"
            elif "gene" in text:
                entity_type = "gene"
            elif "disease" in text:
                entity_type = "disease"
            elif "target" in text:
                entity_type = "target"

        # Additional fallback heuristics to guess the entity from common phrasing

            if re.search(r"phase|approved|trials?", text):
                m = re.search(r"(?:for|is)\s+([A-Za-z0-9\-]+)", text)
                if m:
                    entity = m.group(1)

        if m:
            filters["phase"] = m.group(1)
        m = re.search(r"expression\s*[>=]+\s*(\d+(?:\.\d+)?)", text)
        if m:
            filters["expression"] = m.group(1)
        m = re.search(r"\b(human|mouse|rat|zebrafish)\b", text)
        if m:
            filters["species"] = m.group(1)


            "entity": entity,
            "entity_type": entity_type,
            "action": action,
            "filters": filters,
        }


