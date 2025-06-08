"""Utilities for retrieving data from the Open Targets platform."""

from typing import Optional, Dict, Any

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    requests = None  # type: ignore


OPENTARGETS_URL = "https://api.platform.opentargets.org/api/v4/graphql"


def _post(query: str, variables: Dict[str, Any]) -> Optional[Dict]:
    """Internal helper to POST a GraphQL query if requests is available."""
    if not requests:
        return None
    response = requests.post(OPENTARGETS_URL, json={"query": query, "variables": variables})
    if response is not None and response.status_code == 200:
        return response.json()
    return None


def get_targets_for_disease(efo_id: str) -> Optional[Dict]:
    """Return targets associated with a disease given an EFO ID."""
    query = """
    query diseaseTargets($efoId: String!) {
      disease(efoId: $efoId) {
        id
        name
        associatedTargets {
          rows {
            target {
              id
              approvedSymbol
            }
            score
          }
        }
      }
    }
    """
    variables = {"efoId": efo_id}
    return _post(query, variables)


def get_diseases_for_drug(chembl_id: str) -> Optional[Dict]:
    """Return diseases associated with a drug given a CHEMBL ID."""
    query = """
    query drugIndications($chemblId: String!) {
      drug(chemblId: $chemblId) {
        id
        name
        indications {
          rows {
            disease {
              id
              name
            }
            status
          }
        }
      }
    }
    """
    variables = {"chemblId": chembl_id}
    return _post(query, variables)
