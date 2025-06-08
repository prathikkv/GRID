"""Utilities for retrieving data from the Open Targets platform."""

from typing import Optional, Dict, Any, Callable
import time

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - optional dependency
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
    except requests.exceptions.RequestException:  # type: ignore[attr-defined]
        return None
    return None


def _request_with_retry(func: Callable[[], Any]) -> Optional[Any]:
    """Call ``func`` with simple retry logic for network requests."""
    if not requests:
        return None
    for attempt in range(3):
        try:
            response = func()
            return response
        except requests.exceptions.RequestException:  # type: ignore[attr-defined]
            if attempt == 2:
                return None
            time.sleep(2)
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
            phase
            status
          }
        }
      }
    }
    """
    variables = {"chemblId": chembl_id}
    return _post(query, variables)


def get_trials_for_disease(disease_name: str, phase: str | None = None) -> list:
    """Return clinical trials for a disease from ClinicalTrials.gov.

    Parameters
    ----------
    disease_name:
        Disease name or keyword to search for.
    phase:
        Optional phase string (e.g. ``"Phase 2"``) to filter results.

    Returns
    -------
    list
        List of dictionaries with ``title``, ``phase`` and ``status`` keys.
    """
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

    trials: list = []
    fields = (
        data.get("StudyFieldsResponse", {})
        .get("StudyFields", [])
    )
    for entry in fields:
        title = entry.get("BriefTitle", [""])[0] if entry.get("BriefTitle") else ""
        trial_phase = entry.get("Phase", [""])[0] if entry.get("Phase") else ""
        status = entry.get("Status", [""])[0] if entry.get("Status") else ""
        if phase is None or str(trial_phase).lower() == str(phase).lower():
            trials.append({"title": title, "phase": trial_phase, "status": status})

    return trials
