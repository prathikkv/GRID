"""Utilities for retrieving data from the Open Targets platform and ClinicalTrials.gov."""

from typing import Optional, Dict, Any, Callable
import time

try:
    import requests  # type: ignore
except Exception:  # optional fallback
    requests = None  # type: ignore

OPENTARGETS_URL = "https://api.platform.opentargets.org/api/v4/graphql"


def _post(query: str, variables: Dict[str, Any]) -> Optional[Dict]:
    """Internal helper to POST a GraphQL query with basic error handling."""
    if not requests:
        return None

    def _do_post() -> Any:
        return requests.post(
            OPENTARGETS_URL,
            json={"query": query, "variables": variables},
            timeout=10,
        )

    try:
        response = _request_with_retry(_do_post)
        if response is not None:
            response.raise_for_status()
            return response.json()
    except requests.exceptions.RequestException as exc:  # type: ignore[attr-defined]
        print("Open Targets request failed:", exc)
    return None


def _request_with_retry(func: Callable[[], Any]) -> Optional[Any]:
    """Call `func` with retry logic for network issues."""
    if not requests:
        return None
    for attempt in range(3):
        try:
            return func()
        except requests.exceptions.RequestException as exc:  # type: ignore[attr-defined]
            if attempt == 2:
                print("Final failure:", exc)
            time.sleep(2)
    return None


def get_targets_for_disease(efo_id: str) -> Optional[Dict]:
    """Return targets associated with a disease (EFO ID) from Open Targets."""
    query = """
    query GetTargetsForDisease($efoId: String!) {
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
    """Return diseases associated with a drug (ChEMBL ID) from Open Targets."""
    query = """
    query GetDiseasesForDrug($chemblId: String!) {
      drug(chemblId: $chemblId) {
        id
        name
        indications {
          rows {
            disease {
              id
              name
            }
            phase
            status
          }
        }
      }
    }
    """
    variables = {"chemblId": chembl_id}
    return _post(query, variables)


def get_trials_for_disease(disease_name: str, phase: Optional[str] = None) -> list:
    """Return trials from ClinicalTrials.gov for a given disease and optional phase."""
    if not requests:
        return []

    params = {
        "expr": disease_name,
        "fields": "BriefTitle,Phase,Status,StudyType",
        "max_rnk": 100,
        "fmt": "json",
    }
    url = "https://clinicaltrials.gov/api/query/study_fields"

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as exc:  # type: ignore[attr-defined]
        print("ClinicalTrials.gov request failed:", exc)
        return []

    trials = []
    fields = data.get("StudyFieldsResponse", {}).get("StudyFields", [])
    for entry in fields:
        title = entry.get("BriefTitle", [""])[0]
        trial_phase = entry.get("Phase", [""])[0]
        status = entry.get("Status", [""])[0]
        if phase is None or trial_phase.lower() == phase.lower():
            trials.append({"title": title, "phase": trial_phase, "status": status})

    return trials
