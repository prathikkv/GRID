import argparse
import os
import sys
import re

# Allow importing from the hyphenated folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'grid-agentic-ai')))

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
        # Likely asking about diseases for a given drug
        parsed['entity_type'] = 'drug'

    print("Parsed query:", parsed)

    normalized = None
    if parsed.get('entity') and parsed.get('entity_type'):
        normalized = normalize_term(parsed['entity_type'], parsed['entity'])

    print("Normalized entity:", normalized)

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

    matcher = MatcherAgent()
    matched = matcher.match(parsed, retrieved)
    print('Matched results:', matched)

    summarizer = SummarizerAgent()
    summary = summarizer.summarize(matched, context=parsed)
    print('\nSUMMARY:')
    print(summary)

    output = OutputGeneratorAgent()
    if matched:
        key = next(iter(matched.keys()))
        table = output.to_table(matched[key])
        if table:
            print('\nTABLE:')
            print(table)
    else:
        print('No results to display.')


def main() -> None:
    ap = argparse.ArgumentParser(description='GRID Agentic AI CLI')
    ap.add_argument('--query', required=True, help='Natural language query')
    args = ap.parse_args()
    run_query_pipeline(args.query)


if __name__ == '__main__':
    main()
