from grid_agentic_ai.agents.retriever_opentargets import (
    get_targets_for_disease,
    get_diseases_for_drug,
)

print(get_targets_for_disease("EFO_0003767"))
print(get_diseases_for_drug("CHEMBL1201581"))
