from __future__ import annotations

"""GraphQL query generation agent using LlamaIndex and Ollama."""

from typing import Optional

try:
    from llama_index.core import Document, VectorStoreIndex
except Exception:  # pragma: no cover - optional dependency
    Document = None  # type: ignore
    VectorStoreIndex = None  # type: ignore

try:
    import ollama  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    ollama = None  # type: ignore


class GraphQLQueryAgent:
    """Load a GraphQL schema and generate queries for natural language questions."""

    def __init__(self, schema_path: str) -> None:
        self.schema_path = schema_path
        self._index = None
        self._schema_text = ""
        self._load_schema()

    def _load_schema(self) -> None:
        try:
            with open(self.schema_path, "r", encoding="utf-8") as fh:
                self._schema_text = fh.read()
        except Exception:
            self._schema_text = ""

        if Document is None or VectorStoreIndex is None:
            return
        try:
            docs = [Document(text=self._schema_text)]
            self._index = VectorStoreIndex.from_documents(docs)
        except Exception:
            self._index = None

    def _retrieve_context(self, question: str) -> str:
        if self._index is None:
            return self._schema_text
        try:
            engine = self._index.as_query_engine(similarity_top_k=3)
            result = engine.query(question)
            return str(result)
        except Exception:
            return self._schema_text

    def generate(self, question: str) -> str:
        context = self._retrieve_context(question)
        prompt = (
            "You are a helpful assistant that writes GraphQL queries.\n"
            f"Schema:\n{context}\n"
            f"Question: {question}\n"
            "Return only the GraphQL query." 
        )
        if ollama is None:
            return ""
        try:
            response = ollama.chat(
                model="llama3",
                messages=[{"role": "user", "content": prompt}],
            )
            if isinstance(response, dict):
                message = response.get("message", {})
                return str(message.get("content", "")).strip()
            return str(response).strip()
        except Exception:
            return ""


def generate_query(question: str, schema_path: str) -> str:
    """Convenience wrapper to generate a GraphQL query from ``question``."""
    agent = GraphQLQueryAgent(schema_path)
    return agent.generate(question)
