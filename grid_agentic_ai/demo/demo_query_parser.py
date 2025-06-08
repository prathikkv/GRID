import json

from grid_agentic_ai.agents.query_parser import QueryParserAgent

queries = [
    "List drugs targeting BRAF in phase 3 trials",
    "Find diseases associated with Vemurafenib",
    "Describe gene TP53 expression in mouse",
    "Show trials for Crohn's disease phase 2",
    "List genes with expression >= 2",
]

parser = QueryParserAgent()

for q in queries:
    parsed = parser.parse(q)
    print(f"Query: {q}\nParsed: {json.dumps(parsed, indent=2)}\n")
