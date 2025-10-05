from __future__ import annotations

from typing import Iterable, List, Tuple

from llama_index.core import Document

from ..core.config import settings

# Import with fallbacks across LlamaIndex versions
try:
    from llama_index.core.node_parser import SentenceSplitter
except Exception:  # pragma: no cover - version fallback
    from llama_index.node_parser import SentenceSplitter  # type: ignore

try:
    from llama_index.core.node_parser import SemanticSplitterNodeParser
except Exception:  # pragma: no cover - version fallback
    SemanticSplitterNodeParser = None  # type: ignore


def split_documents_to_texts_and_metas(documents: List[Document]) -> Tuple[List[str], List[dict]]:
    """Split documents using semantic or sentence-based chunking with overlap.

    Returns parallel lists of texts and metadatas.
    """
    chunk_size = settings.chunk_size
    chunk_overlap = settings.chunk_overlap

    texts: List[str] = []
    metadatas: List[dict] = []

    if settings.use_semantic_chunking and SemanticSplitterNodeParser is not None:
        # Semantic chunking attempts
        try:
            semantic_parser = SemanticSplitterNodeParser.from_defaults(
                buffer_size=chunk_overlap,
                breakpoint_percentile_threshold=95,
            )
            for doc in documents:
                nodes = semantic_parser.get_nodes_from_documents([doc])
                for node in nodes:
                    texts.append(node.get_content())
                    # Merge node metadata with original document metadata
                    meta = dict(doc.metadata)
                    node_meta = getattr(node, "metadata", {}) or {}
                    meta.update(node_meta)
                    metadatas.append(meta)
            return texts, metadatas
        except Exception:
            # Fallback below
            pass

    # Default: sentence splitter
    splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    for doc in documents:
        chunks = splitter.split_text(doc.text)
        for idx, chunk in enumerate(chunks):
            texts.append(chunk)
            meta = dict(doc.metadata)
            meta.update({"chunk_local_index": idx})
            metadatas.append(meta)

    return texts, metadatas
