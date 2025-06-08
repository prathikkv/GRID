# GRID Agentic AI



- **agents/** – core agent modules
- **demo/** – example scripts showing how to use the agents
- **tests/** – unit tests with mocked API calls
- **docs/** – placeholder for additional documentation

The main agent currently implemented is `normalize_term` which resolves drug, gene, and disease terms to standard identifiers.

> **Note**
> These agents rely on external services such as PubChem, mygene.info and the Open Targets Platform. Live internet access is required for any query that retrieves real data.

## Agents Overview

| Agent | Purpose |
|-------|---------|
| **normalizer** | Resolves biomedical terms to canonical identifiers. |
| **retriever_opentargets** | Fetches associated targets or diseases from Open Targets and trial data from ClinicalTrials.gov. |
| **matcher** | Aligns parsed query filters with retrieved data. |
| **query_parser** | Converts natural language queries into structured intent and filters. |
| **summarizer** | Generates short textual summaries of matched results. |
| **output_generator** | Exports tables and network graphs. |

The main agent currently implemented is `normalize_term` which resolves drug, gene, and disease terms to standard identifiers. Additional utilities include:
* `retriever_opentargets` for querying the Open Targets platform
* `matcher` for linking targets to drugs
* `summarizer` for generating short textual summaries
* `output_generator` for exporting results to CSV/JSON tables and simple graphs

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit interface:

```bash
streamlit run dashboard_app.py
```

Run a CLI query:

```bash
python main.py "List the diseases in Phase-2 for Imatinib"
```

These commands require an active internet connection to contact the Open Targets API.
Expression filtering and network plots are optional features that depend on the query
and installed libraries.

## Running the Demos

From the repository root, run the demo scripts inside the `grid_agentic_ai/demo` folder:

```bash
python grid_agentic_ai/demo/demo_normalizer.py
python grid_agentic_ai/demo/demo_retriever.py

## Running the Demos

From the repository root, run the demo scripts inside the `grid-agentic-ai/demo` folder:

```bash
python grid-agentic-ai/demo/demo_normalizer.py
python grid-agentic-ai/demo/demo_retriever.py
```

The retriever demo requires network access and the `requests` package.

## Streamlit Dashboard

To experiment interactively, launch the Streamlit dashboard:

```bash
streamlit run dashboard_app.py
```

The app provides a text box and several sample queries you can choose from. Results are displayed as tables and optional network graphs.

## CLI Usage

You can run the entire pipeline with a single command:

```bash
python main.py "Show trials for Crohn's disease phase 2"
python main.py --query "List diseases in Phase-2 for Imatinib"
```

This executes query parsing, normalization, retrieval, matching, summarization,
and optional table output.


## Running Tests

Execute the unit tests with:

```bash
pytest -q
```

## MVP Status

The following modules are implemented as part of the minimum viable product:

- [x] Query Parser
- [x] Matcher Agent
- [x] Output Formatter
- [x] Streamlit Dashboard
- [x] Open Targets Live Integration
- [ ] ClinicalTrials.gov (Optional)
- [ ] Network Graph Visual Enhancements (Optional)

