from typing import Dict, List
from sentence_transformers import CrossEncoder
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import uuid
import os


# Load models 


embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    "data",
    embedding_model,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 8})

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# Helpers


def clean_source(path: str) -> str:
    return os.path.basename(path) if path else "unknown"


def rerank(query: str, docs, top_k: int = 3):
    pairs = [(query, d.page_content) for d in docs]
    scores = reranker.predict(pairs)

    ranked = list(zip(docs, scores))
    ranked.sort(key=lambda x: x[1], reverse=True)

    return [doc for doc, score in ranked[:top_k]]


def build_retrieved_chunks(docs) -> List[Dict]:
    chunks = []

    for doc in docs:
        metadata = doc.metadata or {}

        chunk = {
            "chunk_id": str(uuid.uuid4()),
            "source_id": clean_source(metadata.get("source")),
            "document_id": metadata.get("source", "unknown"),
            "title": metadata.get("title", "unknown"),
            "content": doc.page_content,
            "score": float(metadata.get("score", 0.0)),  # optional
            "metadata": {
                "page": metadata.get("page"),
                "raw_source": metadata.get("source"),
            },
        }

        chunks.append(chunk)

    return chunks

# RAG AGENT NODE


def rag_agent(state: dict) -> dict:
    """
    LangGraph node for retrieval + reranking.
    Writes: retrieved_chunks
    """

    try:
        query = state.get("query", "")

        # ---- use rewritten query if available ----
        retrieval_query = state.get("retrieval_query", {})
        query_to_use = retrieval_query.get("rewritten_query", query)

        top_k = retrieval_query.get("top_k", 8)

        # ---- retrieve ----
        docs = vectorstore.similarity_search(query_to_use, k=top_k)

        # ---- optional filtering (course-specific) ----
        allowed_sources = (
            state.get("course_context", {})
            .get("allowed_sources", [])
        )

        if allowed_sources:
            docs = [
                d for d in docs
                if any(src in d.metadata.get("source", "") for src in allowed_sources)
            ]

        # ---- rerank ----
        docs = rerank(query_to_use, docs, top_k=3)

        # ---- build structured chunks ----
        retrieved_chunks = build_retrieved_chunks(docs)

        return {
            "retrieved_chunks": retrieved_chunks,
            "agent_runs": {
                **state.get("agent_runs", {}),
                "rag_agent": {
                    "status": "success"
                }
            }
        }

    except Exception as e:
        return {
            "retrieved_chunks": [],
            "errors": state.get("errors", []) + [f"rag_agent error: {str(e)}"],
            "agent_runs": {
                **state.get("agent_runs", {}),
                "rag_agent": {
                    "status": "failed",
                    "error": str(e)
                }
            }
        }