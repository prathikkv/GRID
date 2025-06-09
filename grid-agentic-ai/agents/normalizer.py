"""
InputNormalizerAgent: resolves biomedical terms into standard vocab IDs.

Supported types:
- 'drug' -> PubChem name -> CID
- 'gene' -> mygene.info -> HGNC symbol / Entrez ID
- 'disease' -> OLS API -> EFO ID

Input: {"type": "drug", "query": "Imatinib"}
Output: {"input": "Imatinib", "resolved_id": "CHEMBL1201581", "source": "PubChem / OLS / mygene"}
"""

"""Utilities for resolving biomedical terms via external APIs."""

from typing import Dict

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    requests = None  # type: ignore

try:
    import pubchempy as pcp  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pcp = None  # type: ignore


def normalize_term(term_type: str, query: str) -> Dict:
    """Return standardized identifiers for drugs, genes or diseases."""

    if term_type == "drug" and pcp:
        results = pcp.get_compounds(query, "name")
        if results:
            return {
                "input": query,
                "resolved_id": results[0].cid,
                "source": "PubChem",
            }
    elif term_type == "gene" and requests:
        r = requests.get(f"https://mygene.info/v3/query?q={query}&species=human")
        if r is not None and r.status_code == 200 and r.json().get("hits"):
            hit = r.json()["hits"][0]
            return {
                "input": query,
                "resolved_id": hit.get("symbol"),
                "entrez_id": hit.get("_id"),
                "source": "mygene.info",
            }
    elif term_type == "disease" and requests:
        ols_url = f"https://www.ebi.ac.uk/ols/api/search?q={query}&ontology=efo"
        r = requests.get(ols_url)
        if (
            r is not None
            and r.status_code == 200
            and r.json().get("response", {}).get("numFound", 0) > 0
        ):
            doc = r.json()["response"]["docs"][0]
            return {
                "input": query,
                "resolved_id": doc["obo_id"],
                "label": doc["label"],
                "source": "OLS/EFO",
            }

    return {"input": query, "resolved_id": None, "error": "Unable to resolve term"}

