import pprint
from grid_agentic_ai.agents.retriever_opentargets import get_diseases_for_drug


def main() -> None:
    """Fetch diseases for Imatinib and print name, phase and status."""
    chembl_id = "CHEMBL1201581"  # Imatinib
    data = get_diseases_for_drug(chembl_id)
    if data is None:
        print("No data retrieved from Open Targets. Check network connectivity.")
        return
    rows = (
        data.get("data", {})
        .get("drug", {})
        .get("indications", {})
        .get("rows", [])
    )
    if not rows:
        print("No indications found.")
        return
    for entry in rows:
        disease = entry.get("disease", {}).get("name", "")
        phase = entry.get("phase", "")
        status = entry.get("status", "")
        print(f"{disease}: {phase} {status}")


if __name__ == "__main__":
    main()
