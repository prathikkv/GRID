"""Demo for the SummarizerAgent."""

from grid_agentic_ai.agents.summarizer import SummarizerAgent

agent = SummarizerAgent()

sample_results = {
    "trials_by_drug_phase": [
        {"drug": "Vemurafenib", "phase": "3"},
        {"drug": "Vemurafenib", "phase": "3"},
    ]
}

print(agent.summarize(sample_results))

sample_results2 = {
    "targets_with_snps": [
        {"id": "BRAF", "snps": ["rs1", "rs2"]},
        {"id": "BRCA2", "snps": ["rs3"]},
    ]
}
print(agent.summarize(sample_results2))

sample_results3 = {
    "gene_expression": [
        {"target": "BRAF", "expression": 7},
        {"target": "BRCA2", "expression": 2},
    ]
}
print(agent.summarize(sample_results3))
