"""Rule-based summarization for GRID agents.

This module defines a ``SummarizerAgent`` class that converts structured
matcher results into short, human readable summaries.  It keeps the logic
lightweight and works without network access but can be extended with
LLM calls if desired.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional


class SummarizerAgent:
    """Produce simple summaries for matcher results."""

    def summarize(self, results: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Return a human readable summary.

        Parameters
        ----------
        results:
            Dictionary of results from ``MatcherAgent``.
        context:
            Optional context such as the original parsed query.
        """
        if not results:
            return "No results to summarize."

        if "trials_by_drug_phase" in results:
            trials = results["trials_by_drug_phase"]
            if not trials:
                return "No trials matched the requested phase."
            drug = trials[0].get("drug")
            phase = trials[0].get("phase")
            return f"Found {len(trials)} trial(s) for {drug} in phase {phase}."

        if "diseases_by_phase" in results:
            diseases = results["diseases_by_phase"]
            phase = None
            if context:
                phase = context.get("filters", {}).get("phase")
            phase_str = f"phase {phase}" if phase else "the requested phase"
            if not diseases:
                return f"No diseases found in {phase_str}."
            names = ", ".join(d.get("name") for d in diseases)
            return f"Diseases in {phase_str}: {names}."

        if "targets_with_snps" in results:
            targets = results["targets_with_snps"]
            if not targets:
                return "No targets with SNP annotations found."
            names = ", ".join(t.get("id", t.get("target")) for t in targets)
            return f"Targets with SNP annotations: {names}."

        if "gene_expression" in results or "expression_data" in results:
            expr = results.get("gene_expression") or results.get("expression_data")
            if not expr:
                return "No expression data matched the criteria."
            entries = [
                f"{e.get('target')} ({e.get('expression')})" for e in expr
            ]
            return "Protein expression levels: " + ", ".join(entries) + "."

        return "No suitable summary template found."
