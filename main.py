import argparse
import os
import sys
import re

# Allow importing from the hyphenated folder (if needed)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'grid_agentic_ai')))

from agents.query_parser import QueryParserAgent
from agents.normalizer import normalize_term
from agents.retriever_opentargets import get_targets_for_disease, get_diseases_for_drug
from agents.matcher import MatcherAgent
from agents.summarizer import SummarizerAgent
from agents.output_generator import OutputGeneratorAgent


def run_query_pipeline(query: str) -> None:
    """Run the GRID pipeline for a single query."""
    parser = QueryParserAgent()
    parsed = parser.parse(query)

    # Heuristic fallback if parsing failed
    if not parsed.get('entity'):
        m = re.search(r"for\s+([A-Za-z0-9\-]+)", query, re.I)
        if m:
            parsed['entity'] = m.group(1)
            if not parsed.get('entity_type'):
                parsed['entity_type'] = 'drug'

    if 'phase' not in parsed.get('filters', {}):
        m = re.search(r"phase[-\s]*(\d+)", query, re.I)
        if m:
            parsed.setdefault('filters', {})['phase'] = m.group(1)

    if parsed.get('entity') and parsed.get('entity_type') == 'disease' and 'for' in query.lower():
        parsed['entity_type'] = 'drug'

    print("Parsed query:", parsed)

    # Normalize entity (e.g., resolve "Imatinib" to ChEMBL ID)
    normalized = None
    if parsed.get('entity') and parsed.get('entity_type'):
        normalized = normalize_term(parsed['entity_type'], parsed['entity'])
        if normalized is None or normalized.get('resolved_id') is None:
            print("Normalization failed. Using fallback term.")
            if normalized is None:
                normalized = {"input": parsed.get('entity')}
            normalized['resolved_id'] = parsed.get('entity')
            normalized.setdefault('source', 'user input')
    print("Normalized entity:", normalized)

    # Retrieve data
    retrieved = {}
    try:
        if parsed.get('entity_type') == 'drug':
            chembl_id = normalized.get('resolved_id') if normalized else parsed.get('entity')
            res = get_diseases_for_drug(str(chembl_id))
            retrieved['diseases'] = res
        elif parsed.get('entity_type') == 'disease':
            efo_id = normalized.get('resolved_id') if normalized else parsed.get('entity')
            res = get_targets_for_disease(str(efo_id))
            retrieved['targets'] = res
    except Exception as exc:
        print('Retriever error:', exc)

    print('Retrieved data:', retrieved)

    # Match results
    matcher = MatcherAgent()
    matched = matcher.match(parsed, retrieved)
    print('Matched results:', matched)
    if isinstance(matched, dict) and matched.get('message') == 'Query type not supported':
        print('Query type not supported')
        return

    # Summarize
    summarizer = SummarizerAgent()
    summary = summarizer.summarize(matched, context=parsed)
    if summary:
        print('Summary:', summary)
    else:
        print('No results found for this query.')

    # Print table view of first result set if available
    generator = OutputGeneratorAgent()
    table_data = None
    if isinstance(matched, dict) and matched:
        first_key = next(iter(matched))
        table_data = matched[first_key]
    if table_data:
        table_str = generator.to_table(table_data)
        if table_str:
            print(table_str)


def main(argv: list[str] | None = None) -> None:
    """Entry point for the CLI."""
    argp = argparse.ArgumentParser(description="Run GRID agentic pipeline")
    argp.add_argument("query", nargs="?", help="Query text")
    argp.add_argument("--query", dest="query_flag", help="Query text")
    args = argp.parse_args(argv)

    q = args.query or args.query_flag
    if not q:
        argp.error("No query provided")
    run_query_pipeline(q)


if __name__ == "__main__":
    main()
