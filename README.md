# GRID Agentic AI

This repository provides a prototype collection of small agents for biomedical data exploration. The code now lives under the `grid-agentic-ai/` directory and includes:

- **agents/** – core agent modules
- **demo/** – example scripts showing how to use the agents
- **tests/** – unit tests with mocked API calls
- **docs/** – placeholder for additional documentation

The main agent currently implemented is `normalize_term` which resolves drug, gene, and disease terms to standard identifiers. Additional utilities include:
* `retriever_opentargets` for querying the Open Targets platform
* `matcher` for linking targets to drugs
* `summarizer` for generating short textual summaries
* `output_generator` for exporting results to CSV/JSON tables and simple graphs

## Installation

```bash
pip install -r requirements.txt
```

## Running the Demos

From the repository root, run the demo scripts inside the `grid-agentic-ai/demo` folder:

```bash
python grid-agentic-ai/demo/demo_normalizer.py
python grid-agentic-ai/demo/demo_retriever.py
```

The retriever demo requires network access and the `requests` package.

## Running Tests

Execute the unit tests with:

```bash
pytest -q
```
