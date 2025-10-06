from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..core.config import settings

# Optional heavy imports are done lazily
CrossEncoder = None  # type: ignore
SentenceTransformer = None  # type: ignore
FaithfulnessEvaluator = None  # type: ignore
RelevancyEvaluator = None  # type: ignore
CoherenceEvaluator = None  # type: ignore
EvaluationResult = None  # type: ignore
LlamaOpenAI = None  # type: ignore
Settings = None  # type: ignore


def _lazy_import_sentence_transformers() -> None:
    global CrossEncoder, SentenceTransformer
    if CrossEncoder is None or SentenceTransformer is None:
        try:
            from sentence_transformers import CrossEncoder as _CrossEncoder  # type: ignore
            from sentence_transformers import SentenceTransformer as _SentenceTransformer  # type: ignore

            CrossEncoder = _CrossEncoder
            SentenceTransformer = _SentenceTransformer
        except Exception:
            # Leave as None if unavailable
            pass


def _lazy_import_llamaindex_evaluators() -> None:
    global FaithfulnessEvaluator, RelevancyEvaluator, CoherenceEvaluator, EvaluationResult, LlamaOpenAI, Settings
    try:
        # Core evaluators
        from llama_index.core.evaluation import FaithfulnessEvaluator as _FaithfulnessEvaluator  # type: ignore
    except Exception:
        _FaithfulnessEvaluator = None  # type: ignore
    try:
        from llama_index.core.evaluation import RelevancyEvaluator as _RelevancyEvaluator  # type: ignore
    except Exception:
        _RelevancyEvaluator = None  # type: ignore
    # CoherenceEvaluator may not exist in all versions
    try:
        from llama_index.core.evaluation import CoherenceEvaluator as _CoherenceEvaluator  # type: ignore
    except Exception:
        _CoherenceEvaluator = None  # type: ignore
    try:
        from llama_index.core.evaluation import EvaluationResult as _EvaluationResult  # type: ignore
    except Exception:
        _EvaluationResult = None  # type: ignore
    try:
        from llama_index.llms.openai import OpenAI as _LlamaOpenAI  # type: ignore
        from llama_index.core import Settings as _Settings  # type: ignore
    except Exception:
        _LlamaOpenAI = None  # type: ignore
        _Settings = None  # type: ignore

    FaithfulnessEvaluator = _FaithfulnessEvaluator
    RelevancyEvaluator = _RelevancyEvaluator
    CoherenceEvaluator = _CoherenceEvaluator
    EvaluationResult = _EvaluationResult
    LlamaOpenAI = _LlamaOpenAI
    Settings = _Settings


@dataclass
class RetrievedDoc:
    id: Optional[str]
    text: str
    metadata: Optional[Dict[str, Any]] = None
    score: Optional[float] = None


class RAGEvaluator:
    """Evaluate RAG retrieval and generation quality.

    Retrieval metrics: precision@k, recall@k, hit_rate@k, mrr@k, ndcg@k, map@k, relevance_score.
    Generation metrics: faithfulness, relevance, coherence (via LlamaIndex if available; fallback heuristics otherwise).
    """

    def __init__(self) -> None:
        self._cross_encoder = None
        self._semantic_encoder = None
        self._llm_ready = False

    # -------------------- Retrieval Evaluation --------------------
    def evaluate_retrieval(
        self,
        query: str,
        retrieved_docs: Sequence[RetrievedDoc],
        k: Optional[int] = None,
        relevant_doc_ids: Optional[Sequence[str]] = None,
        relevant_texts: Optional[Sequence[str]] = None,
        graded_relevance: Optional[Dict[str, float]] = None,
        use_cross_encoder: bool = False,
    ) -> Dict[str, Any]:
        top_k = min(k or len(retrieved_docs), len(retrieved_docs))
        docs_topk = list(retrieved_docs[:top_k])

        # Determine binary/graded relevance for each doc
        binary_labels = self._compute_binary_relevance_labels(
            docs_topk, relevant_doc_ids=relevant_doc_ids, relevant_texts=relevant_texts
        )
        graded_labels = self._compute_graded_labels(docs_topk, graded_relevance)

        precision = self._precision_at_k(binary_labels)
        recall = self._recall_at_k(binary_labels, total_relevant=self._ground_truth_count(relevant_doc_ids, relevant_texts))
        hit_rate = 1.0 if any(binary_labels) else 0.0
        mrr = self._mrr_at_k(binary_labels)
        ndcg = self._ndcg_at_k(graded_labels if graded_labels else binary_labels)
        ap = self._average_precision(binary_labels, total_relevant=self._ground_truth_count(relevant_doc_ids, relevant_texts))

        relevance_score = None
        if use_cross_encoder:
            relevance_score = self._mean_cross_encoder_score(query, docs_topk)
        else:
            # Fallback: mean of provided scores if present
            provided_scores = [d.score for d in docs_topk if isinstance(d.score, (int, float))]
            relevance_score = sum(provided_scores) / len(provided_scores) if provided_scores else None

        return {
            "k": top_k,
            "hit_rate": hit_rate,
            "precision": precision,
            "recall": recall,
            "mrr": mrr,
            "ndcg": ndcg,
            "map": ap,
            "relevance_score": relevance_score,
        }

    # -------------------- Generation Evaluation --------------------
    def evaluate_generation(
        self,
        query: str,
        response: str,
        contexts: Optional[Sequence[str]] = None,
        run_faithfulness: bool = True,
        run_relevance: bool = True,
        run_coherence: bool = True,
    ) -> Dict[str, Any]:
        _lazy_import_llamaindex_evaluators()
        results: Dict[str, Any] = {}
        contexts = list(contexts or [])

        if (run_faithfulness or run_relevance or run_coherence) and (LlamaOpenAI is not None and Settings is not None):
            # Ensure LLM configured for LlamaIndex
            if not getattr(Settings, "llm", None) and settings.openai_api_key:
                try:
                    Settings.llm = LlamaOpenAI(api_key=settings.openai_api_key)  # type: ignore[attr-defined]
                    self._llm_ready = True
                except Exception:
                    self._llm_ready = False
            else:
                self._llm_ready = True
        else:
            self._llm_ready = False

        # Faithfulness
        if run_faithfulness:
            results["faithfulness"] = self._run_llamaindex_eval(
                evaluator_cls=FaithfulnessEvaluator, query=query, response=response, contexts=contexts
            )

        # Relevance
        if run_relevance:
            results["relevance"] = self._run_llamaindex_eval(
                evaluator_cls=RelevancyEvaluator, query=query, response=response, contexts=contexts
            )

        # Coherence
        if run_coherence:
            if CoherenceEvaluator is not None and self._llm_ready:
                results["coherence"] = self._run_llamaindex_eval(
                    evaluator_cls=CoherenceEvaluator, query=query, response=response, contexts=contexts
                )
            else:
                # Fallback heuristic coherence: average similarity between adjacent sentences
                results["coherence"] = self._heuristic_coherence(response)

        return results

    # -------------------- Internals: Retrieval --------------------
    @staticmethod
    def _ground_truth_count(
        relevant_doc_ids: Optional[Sequence[str]], relevant_texts: Optional[Sequence[str]]
    ) -> int:
        ids_count = len(set(relevant_doc_ids or []))
        texts_count = len(set(relevant_texts or []))
        return max(ids_count, texts_count)

    @staticmethod
    def _doc_matches_texts(text: str, relevant_texts: Optional[Sequence[str]]) -> bool:
        if not relevant_texts:
            return False
        lower = text.lower()
        for pattern in relevant_texts:
            if pattern and pattern.lower() in lower:
                return True
        return False

    def _compute_binary_relevance_labels(
        self,
        docs: Sequence[RetrievedDoc],
        relevant_doc_ids: Optional[Sequence[str]],
        relevant_texts: Optional[Sequence[str]],
    ) -> List[int]:
        id_set = set(relevant_doc_ids or [])
        labels: List[int] = []
        for d in docs:
            is_rel = False
            if d.id and d.id in id_set:
                is_rel = True
            elif d.text and self._doc_matches_texts(d.text, relevant_texts):
                is_rel = True
            labels.append(1 if is_rel else 0)
        return labels

    @staticmethod
    def _compute_graded_labels(
        docs: Sequence[RetrievedDoc], graded_relevance: Optional[Dict[str, float]]
    ) -> Optional[List[float]]:
        if not graded_relevance:
            return None
        labels: List[float] = []
        for d in docs:
            gain = None
            if d.id and d.id in graded_relevance:
                gain = graded_relevance[d.id]
            labels.append(float(gain) if gain is not None else 0.0)
        return labels

    @staticmethod
    def _precision_at_k(labels: Sequence[int]) -> float:
        if not labels:
            return 0.0
        return float(sum(labels)) / float(len(labels))

    @staticmethod
    def _recall_at_k(labels: Sequence[int], total_relevant: int) -> float:
        if total_relevant <= 0:
            # Undefined recall without ground truth; return 0.0 to avoid misleading value
            return 0.0
        return float(sum(labels)) / float(total_relevant)

    @staticmethod
    def _mrr_at_k(labels: Sequence[int]) -> float:
        for idx, v in enumerate(labels):
            if v:
                return 1.0 / float(idx + 1)
        return 0.0

    @staticmethod
    def _dcg(labels: Sequence[float]) -> float:
        import math

        dcg = 0.0
        for i, rel in enumerate(labels):
            denom = math.log2(i + 2.0)
            dcg += (2.0 ** float(rel) - 1.0) / denom
        return dcg

    def _ndcg_at_k(self, labels: Sequence[float | int]) -> float:
        labels_f = [float(v) for v in labels]
        dcg = self._dcg(labels_f)
        ideal = sorted(labels_f, reverse=True)
        idcg = self._dcg(ideal)
        if idcg == 0.0:
            return 0.0
        return dcg / idcg

    @staticmethod
    def _average_precision(labels: Sequence[int], total_relevant: int) -> float:
        if total_relevant <= 0:
            return 0.0
        cum_prec = 0.0
        hit_count = 0
        for idx, v in enumerate(labels, start=1):
            if v:
                hit_count += 1
                cum_prec += hit_count / float(idx)
        if hit_count == 0:
            return 0.0
        return cum_prec / float(total_relevant)

    def _mean_cross_encoder_score(self, query: str, docs: Sequence[RetrievedDoc]) -> Optional[float]:
        _lazy_import_sentence_transformers()
        if CrossEncoder is None:
            return None
        if self._cross_encoder is None:
            try:
                self._cross_encoder = CrossEncoder(settings.reranker_model)
            except Exception:
                return None
        pairs = [(query, d.text) for d in docs if d.text]
        if not pairs:
            return None
        try:
            scores = self._cross_encoder.predict(pairs).tolist()  # type: ignore[attr-defined]
        except Exception:
            return None
        return float(sum(scores) / len(scores)) if scores else None

    # -------------------- Internals: Generation --------------------
    def _run_llamaindex_eval(
        self,
        evaluator_cls: Any,
        query: str,
        response: str,
        contexts: Sequence[str],
    ) -> Optional[Dict[str, Any]]:
        if evaluator_cls is None or not self._llm_ready:
            return None
        try:
            evaluator = evaluator_cls(llm=Settings.llm)  # type: ignore[call-arg]
        except TypeError:
            try:
                evaluator = evaluator_cls(service_context=None)  # type: ignore[call-arg]
            except Exception:
                evaluator = evaluator_cls()  # type: ignore[call-arg]
        except Exception:
            return None

        # Try a few method signatures to be robust across versions
        candidates: List[Tuple[str, Dict[str, Any]]] = [
            ("evaluate", {"query": query, "response": response, "contexts": contexts}),
            ("evaluate_response", {"query": query, "response": response, "contexts": contexts}),
            ("evaluate", {"response": response, "contexts": contexts}),
            ("evaluate_response", {"response": response, "contexts": contexts}),
        ]
        last_exc: Optional[Exception] = None
        for method_name, kwargs in candidates:
            if not hasattr(evaluator, method_name):
                continue
            method = getattr(evaluator, method_name)
            try:
                result = method(**kwargs)
                return self._normalize_eval_result(result)
            except TypeError as exc:
                last_exc = exc
                continue
            except Exception as exc:
                last_exc = exc
                continue
        # Could not call evaluator
        _ = last_exc  # silence
        return None

    @staticmethod
    def _normalize_eval_result(result: Any) -> Dict[str, Any]:
        # LlamaIndex EvaluationResult often has attributes: score, passing, invalid_reasons, feedback
        try:
            score = getattr(result, "score", None)
            passing = getattr(result, "passing", None)
            feedback = getattr(result, "feedback", None)
            return {"score": score, "passing": passing, "feedback": feedback}
        except Exception:
            # Fallback: return raw if not an object
            if isinstance(result, dict):
                return result
            return {"raw": str(result)}

    def _heuristic_coherence(self, response: str) -> Dict[str, Any]:
        """Compute a simple coherence proxy via adjacent sentence similarity."""
        _lazy_import_sentence_transformers()
        if SentenceTransformer is None:
            return {"score": None, "note": "sentence-transformers not available"}
        # Split into sentences (very simple)
        import re

        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", response) if s and s.strip()]
        if len(sentences) < 2:
            return {"score": 1.0, "note": "single sentence"}
        try:
            if self._semantic_encoder is None:
                self._semantic_encoder = SentenceTransformer("all-MiniLM-L6-v2")
            embeddings = self._semantic_encoder.encode(sentences, convert_to_tensor=False, normalize_embeddings=True)
        except Exception:
            return {"score": None, "note": "encoding failed"}
        # Cosine similarity between adjacent sentences
        def _cos(a: List[float], b: List[float]) -> float:
            import math

            dot = sum(x * y for x, y in zip(a, b))
            na = math.sqrt(sum(x * x for x in a))
            nb = math.sqrt(sum(y * y for y in b))
            return 0.0 if na == 0.0 or nb == 0.0 else dot / (na * nb)

        sims: List[float] = []
        for i in range(len(sentences) - 1):
            sims.append(_cos(embeddings[i], embeddings[i + 1]))
        return {"score": float(sum(sims) / len(sims)) if sims else None}
