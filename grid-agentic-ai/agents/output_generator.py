"""Utilities for exporting GRID agent results."""

from __future__ import annotations

import csv
import json
from typing import Any, Dict, List

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pd = None  # type: ignore

try:
    import matplotlib.pyplot as plt  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    plt = None  # type: ignore

try:
    import networkx as nx  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    nx = None  # type: ignore


class OutputGeneratorAgent:
    """Helper class for exporting results in various formats."""

    def to_csv(self, results: Any, filepath: str) -> None:
        """Write ``results`` to ``filepath`` as CSV."""
        if not results:
            # create empty file
            open(filepath, "w").close()
            return

        if pd is not None:
            try:
                df = pd.DataFrame(results)
                df.to_csv(filepath, index=False)
                return
            except Exception:
                pass  # fallback to csv module

        # Fallback: basic CSV writing
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            if isinstance(results, list):
                if results:
                    header = list(results[0].keys())
                    writer.writerow(header)
                    for row in results:
                        writer.writerow([row.get(h, "") for h in header])
            elif isinstance(results, dict):
                writer.writerow(["key", "value"])
                for k, v in results.items():
                    writer.writerow([k, v])
            else:
                writer.writerow([str(results)])

    def to_json(self, results: Any, filepath: str) -> None:
        """Write ``results`` to ``filepath`` as JSON."""
        with open(filepath, "w") as f:
            json.dump(results if results is not None else {}, f, indent=2)

    def to_table(self, results: Any) -> str:
        """Return ``results`` as a formatted table string."""
        if not results:
            return ""

        if pd is not None:
            try:
                df = pd.DataFrame(results)
                return df.to_string(index=False)
            except Exception:
                pass

        if isinstance(results, list):
            if not results:
                return ""
            header = list(results[0].keys())
            lines = ["\t".join(header)]
            for row in results:
                lines.append("\t".join(str(row.get(h, "")) for h in header))
            return "\n".join(lines)
        elif isinstance(results, dict):
            return "\n".join(f"{k}: {v}" for k, v in results.items())
        else:
            return str(results)

    def plot_network(self, nodes: List[Any], edges: List[tuple], filepath: str) -> None:
        """Generate a simple network graph image if dependencies are available."""
        if not nodes and not edges:
            return
        if nx is None or plt is None:
            return

        graph = nx.Graph()
        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)
        plt.figure()
        nx.draw(graph, with_labels=True)
        plt.savefig(filepath)
        plt.close()

