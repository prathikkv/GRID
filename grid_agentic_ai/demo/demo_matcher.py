from pprint import pprint

from grid_agentic_ai.agents.matcher import MatcherAgent

agent = MatcherAgent()

# --- Example 1: list diseases by trial phase ---
query1 = {"action": "list", "entity_type": "disease", "filters": {"phase": "3"}}
data1 = {
    "diseases": [
        {"name": "CancerA", "phase": "2"},
        {"name": "CancerB", "phase": "3"},
    ]
}
print("\nExample 1: diseases by phase")
pprint(agent.match(query1, data1))

# --- Example 2: targets that have SNPs ---
query2 = {"action": "list", "entity_type": "target", "filters": {"snp": True}}
data2 = {
    "targets": [
        {"id": "T1", "snps": ["rs1", "rs2"]},
        {"id": "T2", "snps": []},
    ]
}
print("\nExample 2: targets with SNPs")
pprint(agent.match(query2, data2))

# --- Example 3: gene expression threshold ---
query3 = {
    "action": "describe",
    "entity_type": "target",
    "filters": {"expression_threshold": 5},
}
data3 = {
    "targets": [
        {"id": "T1", "expression": 4},
        {"id": "T2", "expression": 6},
    ]
}
print("\nExample 3: gene expression for targets")
pprint(agent.match(query3, data3))
