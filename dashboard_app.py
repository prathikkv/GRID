import os
import sys
import tempfile
import streamlit as st

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover - optional
    pd = None  # type: ignore

# Ensure package path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'grid-agentic-ai')))

from agents.normalizer import normalize_term
from agents.query_parser import QueryParserAgent
from agents.retriever_opentargets import get_targets_for_disease, get_diseases_for_drug
from agents.matcher import MatcherAgent
from agents.output_generator import OutputGeneratorAgent

parser = QueryParserAgent()
matcher = MatcherAgent()
output_agent = OutputGeneratorAgent()

st.title("GRID Dashboard")

sample_queries = [
    "List the diseases in Phase-2 for Imatinib",
    "For compound Olaparib, list all the targets and their binding affinities",
    "Describe gene TP53 expression in mouse",
    "Show trials for Crohn's disease phase 2",
    "List genes with expression >= 2"
]

def _set_sample():
    st.session_state.query = st.session_state.sample_query

if "query" not in st.session_state:
    st.session_state.query = sample_queries[0]

st.selectbox(
    "Try sample query",
    options=sample_queries,
    key="sample_query",
    on_change=_set_sample,
)

query = st.text_input(
    "Enter a biomedical query:",
    st.session_state.query,
    key="query"
)

if st.button("Run Query"):
    with st.spinner("Running pipeline..."):
        try:
            parsed = parser.parse(query)
        except Exception as exc:
            st.error(f"Failed to parse query: {exc}")
            st.stop()

        entity = parsed.get("entity")
        entity_type = parsed.get("entity_type")
        filters = parsed.get("filters", {})

        if not entity or not entity_type:
            st.error("Unable to determine query entity or type.")
            st.stop()

        norm = normalize_term(entity_type, entity)
        if not norm.get("resolved_id"):
            st.error("Normalization failed for entity: %s" % entity)
            st.stop()

        retrieved_data = {}
        if entity_type == "disease":
            data = get_targets_for_disease(norm["resolved_id"])

            
            if data is None:
                st.warning("\u2757 No data retrieved. Please try a different query.")
            else:
                rows = (
                    data.get("data", {})
                    .get("disease", {})
                    .get("associatedTargets", {})
                    .get("rows", [])
                )
            if data:
                rows = data.get("data", {}).get("disease", {}).get("associatedTargets", {}).get("rows", [])
                retrieved_data["targets"] = [
                    {
                        "id": r.get("target", {}).get("id"),
                        "approvedSymbol": r.get("target", {}).get("approvedSymbol"),
                        "score": r.get("score"),
                    }
                    for r in rows
                ]
        elif entity_type == "drug":
            data = get_diseases_for_drug(norm["resolved_id"])

            if data is None:
                st.warning("\u2757 No data retrieved. Please try a different query.")
            else:
                rows = (
                    data.get("data", {})
                    .get("drug", {})
                    .get("indications", {})
                    .get("rows", [])
                )
            if data:
                rows = data.get("data", {}).get("drug", {}).get("indications", {}).get("rows", [])
                retrieved_data["diseases"] = [
                    {
                        "name": r.get("disease", {}).get("name"),
                        "phase": r.get("status"),
                    }
                    for r in rows
                ]
        else:
            data = None

        matched = matcher.match(parsed, retrieved_data)

        # Determine table data for display and export
        table_data = []
        if isinstance(matched, dict) and matched:
            key = next(iter(matched))
            table_data = matched[key]

        if isinstance(table_data, str):
            st.warning(table_data)
        elif isinstance(table_data, (list, dict)) or (
            pd is not None and isinstance(table_data, pd.DataFrame)
        ):
            if table_data:
                st.subheader("Results Table")
                st.table(table_data)
            else:
                st.info("No results found.")
        
        if table_data:
            st.subheader("Results Table")
            st.table(table_data)
        else:
            st.info("No results found.")

        # Downloads
        if isinstance(table_data, (list, dict)) or (
            pd is not None and isinstance(table_data, pd.DataFrame)
        ):
            if table_data:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_csv:
                    output_agent.to_csv(table_data, tmp_csv.name)
                    tmp_csv.seek(0)
                    csv_bytes = tmp_csv.read()
                st.download_button("Download CSV", csv_bytes, file_name="results.csv")

                with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp_json:
                    output_agent.to_json(table_data, tmp_json.name)
                    tmp_json.seek(0)
                    json_bytes = tmp_json.read()
                st.download_button("Download JSON", json_bytes, file_name="results.json")
        if table_data:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_csv:
                output_agent.to_csv(table_data, tmp_csv.name)
                tmp_csv.seek(0)
                csv_bytes = tmp_csv.read()
            st.download_button("Download CSV", csv_bytes, file_name="results.csv")

            with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp_json:
                output_agent.to_json(table_data, tmp_json.name)
                tmp_json.seek(0)
                json_bytes = tmp_json.read()
            st.download_button("Download JSON", json_bytes, file_name="results.json")

        # Plot network if possible
        nodes = []
        edges = []
        if entity_type == "disease" and isinstance(table_data, list) and table_data:
            nodes = [entity] + [r.get("approvedSymbol") for r in table_data]
            edges = [(entity, r.get("approvedSymbol")) for r in table_data]
        elif entity_type == "drug" and isinstance(table_data, list) and table_data:
        if entity_type == "disease" and table_data:
            nodes = [entity] + [r.get("approvedSymbol") for r in table_data]
            edges = [(entity, r.get("approvedSymbol")) for r in table_data]
        elif entity_type == "drug" and table_data:
            nodes = [entity] + [r.get("name") for r in table_data]
            edges = [(entity, r.get("name")) for r in table_data]

        if nodes and edges:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_img:
                output_agent.plot_network(nodes, edges, tmp_img.name)
                if os.path.exists(tmp_img.name):
                    st.image(tmp_img.name)
        
        st.success("Pipeline completed")
