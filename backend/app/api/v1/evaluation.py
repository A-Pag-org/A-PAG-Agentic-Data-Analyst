from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...services.evaluation import RAGEvaluator, RetrievedDoc


router = APIRouter(prefix="/evaluation", tags=["evaluation"])


class RetrievedDocIn(BaseModel):
    id: Optional[str] = None
    text: str
    score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class RetrievalEvalRequest(BaseModel):
    query: str
    docs: List[RetrievedDocIn] = Field(default_factory=list)
    k: Optional[int] = None
    relevant_doc_ids: Optional[List[str]] = None
    relevant_texts: Optional[List[str]] = None
    graded_relevance: Optional[Dict[str, float]] = None
    use_cross_encoder: bool = False


class GenerationEvalRequest(BaseModel):
    query: str
    response: str
    contexts: Optional[List[str]] = None
    run_faithfulness: bool = True
    run_relevance: bool = True
    run_coherence: bool = True


@router.post("/retrieval")
async def evaluate_retrieval(req: RetrievalEvalRequest):
    try:
        evaluator = RAGEvaluator()
        result = evaluator.evaluate_retrieval(
            query=req.query,
            retrieved_docs=[RetrievedDoc(**d.model_dump()) for d in req.docs],
            k=req.k,
            relevant_doc_ids=req.relevant_doc_ids,
            relevant_texts=req.relevant_texts,
            graded_relevance=req.graded_relevance,
            use_cross_encoder=req.use_cross_encoder,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/generation")
async def evaluate_generation(req: GenerationEvalRequest):
    try:
        evaluator = RAGEvaluator()
        result = evaluator.evaluate_generation(
            query=req.query,
            response=req.response,
            contexts=req.contexts,
            run_faithfulness=req.run_faithfulness,
            run_relevance=req.run_relevance,
            run_coherence=req.run_coherence,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
