# Agent Interfaces

This document describes the public interface for each core agent in this repository. Paths are relative to the repository root.

## InputNormalizerAgent

- **Location:** `grid_agentic_ai/agents/normalizer.py`
- **Public Function:** `normalize_term(term_type: str, query: str) -> dict`
- **Description:** Resolve a drug, gene or disease name to a stable identifier using external APIs (PubChem, mygene.info or OLS).
- **Input:**
  - `term_type` – one of `"drug"`, `"gene"`, or `"disease"`.
  - `query` – text name to normalize.
- **Returns:** Dictionary with keys like `input`, `resolved_id`, optional metadata and an `error` message when not found.
- **Example:**
  ```python
  from grid_agentic_ai.agents.normalizer import normalize_term
  res = normalize_term("drug", "Imatinib")
  ```

## QueryParserAgent

- **Location:** `grid_agentic_ai/agents/query_parser.py`
- **Class:** `QueryParserAgent`
- **Public Method:** `parse(query: str) -> dict`
- **Description:** Parse natural language questions into structured components such as entity, entity type, action and filters.
- **Input:** Query string.
- **Returns:** Dictionary with keys `entity`, `entity_type`, `action` and `filters`.
- **Example:**
  ```python
  from grid_agentic_ai.agents.query_parser import QueryParserAgent
  parser = QueryParserAgent()
  parser.parse("List diseases in phase 2 for Imatinib")
  ```

## RetrieverAgent (Open Targets)

- **Location:** `grid_agentic_ai/agents/retriever_opentargets.py`
- **Functions:**
  - `get_targets_for_disease(efo_id: str) -> Optional[dict]`
  - `get_diseases_for_drug(chembl_id: str) -> Optional[dict]`
  - `get_trials_for_disease(disease_name: str, phase: str | None = None) -> list`
- **Description:** Fetch targets, diseases or clinical trials from the Open Targets API and ClinicalTrials.gov.
- **Input:** Identifiers (EFO or ChEMBL) or disease names.
- **Returns:** JSON dictionaries or lists with the requested information.
- **Example:**
  ```python
  from grid_agentic_ai.agents import retriever_opentargets as retriever
  data = retriever.get_targets_for_disease("EFO_0003767")
  ```

## MatcherAgent

- **Location:** `grid_agentic_ai/agents/matcher.py`
- **Functions:** `match_targets_to_drugs(targets: list, drug_data: list) -> list`
- **Class:** `MatcherAgent` with method `match(parsed_query: dict, retrieved_data: dict) -> dict`
- **Description:** Align parsed queries with retrieved results or directly match targets to drugs based on identifiers and filters.
- **Example:**
  ```python
  from grid_agentic_ai.agents.matcher import match_targets_to_drugs
  matches = match_targets_to_drugs(targets, drug_data)
  ```

## SummarizerAgent

- **Location:** `grid_agentic_ai/agents/summarizer.py`
- **Class:** `SummarizerAgent`
- **Public Method:** `summarize(results: dict, context: dict | None = None) -> str`
- **Description:** Produce a short human readable summary from matcher results.
- **Example:**
  ```python
  from grid_agentic_ai.agents.summarizer import SummarizerAgent
  text = SummarizerAgent().summarize({"trials_by_drug_phase": [{"drug": "DrugA", "phase": "2"}]})
  ```

## OutputGeneratorAgent

- **Location:** `grid_agentic_ai/agents/output_generator.py`
- **Class:** `OutputGeneratorAgent`
- **Public Methods:**
  - `to_csv(results, filepath)`
  - `to_json(results, filepath)`
  - `to_table(results) -> str`
  - `plot_network(nodes, edges, filepath)`
- **Description:** Export matcher results to CSV/JSON, render tables and (if libraries are installed) create simple network graphs.
- **Example:**
  ```python
  from grid_agentic_ai.agents.output_generator import OutputGeneratorAgent
  out = OutputGeneratorAgent()
  out.to_csv(results, "out.csv")
  ```

## GraphQLQueryAgent

- **Location:** `grid_agentic_ai/agents/graphql_query_agent.py`
- **Class:** `GraphQLQueryAgent`
- **Public Function:** `generate_query(question: str, schema_path: str) -> str`
- **Description:** Load a GraphQL schema, index it with LlamaIndex and use a local Ollama model to generate GraphQL queries from natural language questions.
- **Example:**
  ```python
  from grid_agentic_ai.agents.graphql_query_agent import generate_query
  query = generate_query("List drug names", "schema.graphql")
  ```
