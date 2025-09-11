## Quality‑Weighted Reciprocal Rank Fusion (QW‑RRF)

This document describes an approach to hybrid search ranking that preserves the robustness of Reciprocal Rank Fusion (RRF) while allowing per‑engine "match strength" (quality) to influence ordering in a controlled, calibration‑aware way.

### Motivation

- Plain RRF is rank‑only and robust across engines whose score scales differ; however, it cannot prefer a “strong” top result from one engine over a “weak” top result from another.
- Pure score fusion requires cross‑engine score calibration, which is brittle across queries and model updates.
- QW‑RRF strikes a balance: normalize qualities per query and per engine (bounded, monotonic), then modulate the RRF contribution by these normalized qualities.

### Recap: Standard RRF

For a document d appearing with rank r_e in engine e, the RRF contribution is:

\[ S_{RRF}(d) = \sum_e \frac{1}{k + r_e} \]

where k is a smoothing constant (commonly 60). Missing ranks contribute 0. Final ordering sorts documents by S_{RRF}(d) descending.

### QW‑RRF: Incorporating Quality

Each engine e provides a raw score s_e(d) for a doc d (e.g., BM25 score, vector cosine similarity). These are not directly comparable. We normalize them into a bounded per‑query quality \(\hat q_e(d) \in [0,1]\), then weight each RRF term by \(\hat q_e(d)\):

\[ S_{QW\text{-}RRF}(d) = \sum_e w_e \cdot \hat q_e(d) \cdot \frac{1}{k + r_e} \]

- \(\hat q_e(d)\) is computed per query, per engine (no global calibration required).
- w_e are optional per‑engine weights (default 1.0).
- If a document is absent in an engine, that term is 0.

### Normalization Options (per query, per engine)

- Softmax with temperature (recommended):
  - Stable, bounded, and monotonic with the engine’s own ordering.
  - \( \hat q_e(d) = \mathrm{softmax}(s_e(d)/\tau) \)
  - Use small \(\tau\) (e.g., 0.1–0.3) to emphasize top ranks.
- Min–max (fallback): \( \hat q = (s - s_{min}) / (s_{max} - s_{min} + \epsilon) \) when the score range is informative.
- Degenerate case handling: If an engine’s top‑k scores are flat (range < ε), return uniform \(\hat q\) over those results (reduces to plain RRF for that engine).

### Safeguards and Tie‑Breaking

- Clip \(\hat q\) to [q_min, 1.0] (e.g., q_min = 0.2) to avoid over‑penalizing an engine with conservative scores.
- If both engines’ normalizations are degenerate in a query, QW‑RRF effectively behaves like plain RRF.
- Tie‑breaking after S_{QW‑RRF}:
  1) Higher max(\(\hat q_{bm25}, \hat q_{vector}\))
  2) Better (lower) best rank across engines
  3) Deterministic engine order (e.g., BM25 before Vector)

### Parameters

- k (RRF smoothing): 60 (default)
- τ (softmax temperature): 0.15 (default). Smaller → sharper emphasis on top scores.
- q_min (quality floor): 0.2 (default)
- w_e (engine weights): 1.0 for BM25 and Vector by default

### Worked Micro‑Example

- BM25: A#1 (score 12.0), B#2 (10.0), C#3 (7.0)
- Vector: X#1 (0.42), B#2 (0.41), C#3 (0.40)
- Plain RRF gives equal top contribution to A#1 and X#1.
- QW‑RRF with softmax‑normalized qualities increases B and C (which both engines like) and can let A#1 outrank X#1 if A’s normalized quality is sufficiently higher than X’s.

### Python Reference Implementation (standalone)

The following code is self‑contained and mirrors the repository’s data structures (e.g., `SearchResult`). Integrate by adapting `SearchTools._rrf_fusion` to a new `_quality_weighted_rrf_fusion` and calling it from `search_for_documents` instead of the plain RRF.

```python
from typing import List, Dict, Any, Tuple
import math

def _softmax_normalize(scores: List[float], tau: float) -> List[float]:
    if not scores:
        return []
    s_max = max(scores)
    exps = [math.exp((s - s_max) / max(tau, 1e-6)) for s in scores]
    denom = sum(exps) or 1.0
    return [x / denom for x in exps]

def _minmax_normalize(scores: List[float]) -> List[float]:
    if not scores:
        return []
    s_min, s_max = min(scores), max(scores)
    denom = (s_max - s_min)
    if denom < 1e-12:
        # Degenerate: return uniform
        n = len(scores)
        return [1.0 / n] * n
    return [(s - s_min) / (denom + 1e-12) for s in scores]

def _engine_quality_map(results, tau: float, method: str = "softmax", q_min: float = 0.2) -> Dict[str, float]:
    """
    Build a {document_id -> quality} map for one engine.
    results: list of SearchResult‑like with .document_id and .score
    """
    scores = [r.score for r in results]
    if not scores:
        return {}
    if method == "softmax":
        qualities = _softmax_normalize(scores, tau)
    else:
        qualities = _minmax_normalize(scores)
    # Clip to [q_min, 1.0]
    qualities = [max(q_min, min(1.0, q)) for q in qualities]
    return {r.document_id: q for r, q in zip(results, qualities)}

def _rank_map(results) -> Dict[str, int]:
    # 1‑based rank
    return {r.document_id: i for i, r in enumerate(results, start=1)}

def quality_weighted_rrf_fusion(
    bm25_results, 
    vector_results, 
    limit: int,
    *,
    k: int = 60,
    tau: float = 0.15,
    weights: Dict[str, float] = None,
    quality_method: str = "softmax",
    q_min: float = 0.2,
) -> List[Dict[str, Any]]:
    """
    Quality‑weighted RRF fusion.
    Returns list of dicts with: document_id, fused_score, rrf_score, source, rank_in_source,
    found_in, qualities (per engine).
    """
    if weights is None:
        weights = {"bm25": 1.0, "vector": 1.0}

    if not bm25_results and not vector_results:
        return []
    if not bm25_results:
        # Preserve shape similar to existing outputs
        return [
            {
                "document_id": r.document_id,
                "score": r.score,
                "rrf_score": 1.0 / (i + k),
                "fused_score": weights.get("vector", 1.0) * (1.0) * (1.0 / (i + k)),
                "source": "vector",
                "rank_in_source": i,
                "found_in": ["vector"],
                "qualities": {"vector": 1.0},
            }
            for i, r in enumerate(vector_results, start=1)
        ][:limit]
    if not vector_results:
        return [
            {
                "document_id": r.document_id,
                "score": r.score,
                "rrf_score": 1.0 / (i + k),
                "fused_score": weights.get("bm25", 1.0) * (1.0) * (1.0 / (i + k)),
                "source": "bm25",
                "rank_in_source": i,
                "found_in": ["bm25"],
                "qualities": {"bm25": 1.0},
            }
            for i, r in enumerate(bm25_results, start=1)
        ][:limit]

    # Build per‑engine maps
    bm25_q = _engine_quality_map(bm25_results, tau=tau, method=quality_method, q_min=q_min)
    vec_q = _engine_quality_map(vector_results, tau=tau, method=quality_method, q_min=q_min)
    bm25_rank = _rank_map(bm25_results)
    vec_rank = _rank_map(vector_results)

    # Union of documents
    doc_ids = set(bm25_rank.keys()) | set(vec_rank.keys())

    fused_items: List[Tuple[str, float, float]] = []  # (doc_id, fused_score, rrf_score)
    for doc_id in doc_ids:
        fused = 0.0
        rrf = 0.0
        if doc_id in bm25_rank:
            r = bm25_rank[doc_id]
            contrib = 1.0 / (k + r)
            rrf += contrib
            fused += weights.get("bm25", 1.0) * bm25_q.get(doc_id, 0.0) * contrib
        if doc_id in vec_rank:
            r = vec_rank[doc_id]
            contrib = 1.0 / (k + r)
            rrf += contrib
            fused += weights.get("vector", 1.0) * vec_q.get(doc_id, 0.0) * contrib
        fused_items.append((doc_id, fused, rrf))

    # Sort with tie‑breakers
    def tie_key(doc_id: str):
        max_q = max(bm25_q.get(doc_id, 0.0), vec_q.get(doc_id, 0.0))
        best_rank = min(bm25_rank.get(doc_id, 10**9), vec_rank.get(doc_id, 10**9))
        # BM25‑first deterministic fallback
        bm25_first = 0 if doc_id in bm25_rank else 1
        return (-max_q, best_rank, bm25_first)

    fused_items.sort(key=lambda t: (t[1], t[2],) + tie_key(t[0]), reverse=True)

    results: List[Dict[str, Any]] = []
    for doc_id, fused_score, rrf_score in fused_items[:limit]:
        # Determine primary source by better rank
        bm25_r = bm25_rank.get(doc_id, 10**9)
        vec_r = vec_rank.get(doc_id, 10**9)
        if bm25_r == 10**9 and vec_r == 10**9:
            primary = "bm25"
            rank_in_source = 10**9
        else:
            primary = "bm25" if bm25_r <= vec_r else "vector"
            rank_in_source = bm25_r if primary == "bm25" else vec_r

        # Original score from primary engine, if available (for display)
        primary_score = None
        if primary == "bm25":
            for r in bm25_results:
                if r.document_id == doc_id:
                    primary_score = r.score
                    break
        else:
            for r in vector_results:
                if r.document_id == doc_id:
                    primary_score = r.score
                    break

        results.append({
            "document_id": doc_id,
            "score": primary_score,
            "rrf_score": rrf_score,
            "fused_score": fused_score,
            "source": primary,
            "rank_in_source": rank_in_source,
            "found_in": [s for s in ("bm25", "vector") if (s == "bm25" and doc_id in bm25_rank) or (s == "vector" and doc_id in vec_rank)],
            "qualities": {"bm25": bm25_q.get(doc_id), "vector": vec_q.get(doc_id)},
        })

    return results
```

### Integration Notes

- In `SearchTools.search_for_documents(...)`, replace the call to `_rrf_fusion(...)` with `_quality_weighted_rrf_fusion(...)` (your integrated version of the above), passing `k`, `tau`, optional `weights`, and `limit=top_k`.
- Preserve the existing response shape. Consider adding `fused_score`, `qualities`, and keep `score` as the original engine score (for UI/debug).
- Keep a feature flag (e.g., in settings) to toggle between plain RRF and QW‑RRF for safe rollout and A/B testing.

### Testing Recommendations

- Unit tests for normalization: verify monotonicity and boundedness; degenerate cases return uniform.
- Property tests: if qualities are uniform, QW‑RRF == plain RRF ordering.
- Scenario tests: ensure “three strong A vs. three weak B” leads to A’s results preceding B’s under reasonable τ.
- Telemetry: log distribution summaries of raw scores and normalized qualities per engine per query during rollout.

### Trade‑offs

- Pros: preserves rank robustness, allows controlled emphasis of “strength,” minimal tuning, easy rollback.
- Cons: introduces parameters (τ, q_min, weights), small added complexity, per‑query normalization cost (negligible for typical top‑k).


