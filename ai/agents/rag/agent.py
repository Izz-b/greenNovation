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


def truncate_content(text: str, max_chars: int) -> str:
    return text[:max_chars] if max_chars else text


def build_retrieved_chunks(docs, max_chars: int) -> List[Dict]:
    chunks = []

    for doc in docs:
        metadata = doc.metadata or {}

        content = truncate_content(doc.page_content, max_chars)

        chunk = {
            "chunk_id": str(uuid.uuid4()),
            "source_id": clean_source(metadata.get("source")),
            "document_id": metadata.get("source", "unknown"),
            "title": metadata.get("title", "unknown"),
            "content": content,
            "score": float(metadata.get("score", 0.0)),
            "metadata": {
                "page": metadata.get("page"),
                "raw_source": metadata.get("source"),
            },
        }

        chunks.append(chunk)

    return chunks



# RAG AGENT (ENERGY-AWARE)

def rag_agent(state: dict) -> dict:
    try:
        query = state.get("query", "")

        # ENERGY DECISION
        energy = state.get("energy_decision", {})

        use_rag = energy.get("use_rag", True)
        top_k = energy.get("top_k", 5)
        max_chars = energy.get("chunk_truncation_chars", 800)

        # Optional: skip reranking in light mode
        mode = energy.get("mode", "balanced")
        use_rerank = mode != "light"

        if not use_rag:
            return {
                "retrieved_chunks": [],
                "agent_runs": {
                    **state.get("agent_runs", {}),
                    "rag_agent": {
                        "status": "skipped",
                        "reason": "Energy agent disabled RAG"
                    }
                }
            }

        # QUERY
        retrieval_query = state.get("retrieval_query", {})
        query_to_use = retrieval_query.get("rewritten_query", query)

        # fallback if energy didn't specify
        top_k = retrieval_query.get("top_k", top_k)

        # RETRIEVE
        docs = vectorstore.similarity_search(query_to_use, k=top_k)

        # FILTER (course-specific)
        
        allowed_sources = (
            state.get("course_context", {})
            .get("allowed_sources", [])
        )

        if allowed_sources:
            docs = [
                d for d in docs
                if any(src in d.metadata.get("source", "") for src in allowed_sources)
            ]

        # RERANK (optional)
        
        if use_rerank and len(docs) > 1:
            docs = rerank(query_to_use, docs, top_k=min(3, len(docs)))

        
        # BUILD CHUNKS (truncated)
      
        retrieved_chunks = build_retrieved_chunks(docs, max_chars)

        return {
            "retrieved_chunks": retrieved_chunks,
            "agent_runs": {
                **state.get("agent_runs", {}),
                "rag_agent": {
                    "status": "success",
                    "mode": mode,
                    "top_k_used": top_k,
                    "rerank_used": use_rerank
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