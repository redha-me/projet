# =============================================================================
# api.py — REST API (FastAPI) pour le Systeme de Recommandation de Livres
# =============================================================================
# Lancer avec : uvicorn webapp.api:app --reload --host 0.0.0.0 --port 8000
# Documentation interactive : http://localhost:8000/docs
# =============================================================================

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from recommender import BookRecommender

# ── Initialisation ────────────────────────────────────────────────────────────
app = FastAPI(
    title="BookMatch API",
    description="API REST pour le systeme de recommandation de livres (UA1)",
    version="1.0.0",
)

try:
    recommender = BookRecommender()
except Exception as e:
    print(f"ERREUR: Impossible de charger les modeles : {e}")
    recommender = None


# ── Modeles de reponse ────────────────────────────────────────────────────────
class PopularBook(BaseModel):
    book_idx: int
    title: str
    author: Optional[str] = None
    genre: Optional[str] = None
    image_url: Optional[str] = None
    goodreads_url: Optional[str] = None
    avg_rating: float
    n_ratings: int
    score: float


class ContentRec(BaseModel):
    book_idx: Optional[int] = None
    title: str
    author: Optional[str] = None
    genre: Optional[str] = None
    image_url: Optional[str] = None
    goodreads_url: Optional[str] = None
    similarity_score: float


class CollaborativeRec(BaseModel):
    book_idx: int
    title: str
    author: Optional[str] = None
    genre: Optional[str] = None
    image_url: Optional[str] = None
    goodreads_url: Optional[str] = None
    similarity_score: float


class MFRec(BaseModel):
    rank: int
    book_idx: int
    title: str
    author: Optional[str] = None
    genre: Optional[str] = None
    image_url: Optional[str] = None
    goodreads_url: Optional[str] = None
    predicted_rating: float


class HybridRec(BaseModel):
    book_idx: int
    title: str
    author: Optional[str] = None
    genre: Optional[str] = None
    image_url: Optional[str] = None
    goodreads_url: Optional[str] = None
    score_cb: float
    score_cf: float
    score_mf: float
    hybrid_score: float


class SystemInfo(BaseModel):
    n_users: int
    n_books: int
    n_neighbors: int
    weights: dict
    global_mean: float
    models_loaded: bool


def enrich_books(records):
    """Attache les metadata riches aux lignes de recommandation."""
    enriched = []
    for record in records:
        book_idx = record.get("book_idx")
        meta = recommender.get_book_meta(int(book_idx)) if recommender is not None and book_idx is not None and str(book_idx) != "nan" else {}
        enriched.append({
            **record,
            "author": record.get("author") or meta.get("author") or None,
            "genre": record.get("genre") or meta.get("genre") or None,
            "image_url": record.get("image_url") or meta.get("image_url") or None,
            "goodreads_url": record.get("goodreads_url") or meta.get("goodreads_url") or None,
        })
    return enriched


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
def root():
    return {"message": "BookMatch API", "status": "ok"}


@app.get("/info", response_model=SystemInfo, tags=["Systeme"])
def get_system_info():
    """Retourne les informations du systeme."""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modeles non charges")
    return SystemInfo(
        n_users=recommender.n_users,
        n_books=recommender.n_books,
        n_neighbors=recommender.N_NEIGHBORS,
        weights={"cb": recommender.W_CB, "cf": recommender.W_CF, "mf": recommender.W_MF},
        global_mean=recommender.global_mean,
        models_loaded=recommender.is_loaded(),
    )


@app.get("/titles", tags=["Catalogue"])
def get_all_titles():
    """Retourne la liste de tous les titres disponibles."""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modeles non charges")
    return {"titles": recommender.get_all_titles()}


@app.get("/popular", response_model=List[PopularBook], tags=["Recommandations"])
def get_popular(top_n: int = Query(10, ge=1, le=50, description="Nombre de resultats")):
    """Livres les plus populaires (Baseline type IMDb)."""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modeles non charges")
    result = recommender.get_popular_recommendations(top_n=top_n)
    return enrich_books(result.to_dict(orient="records"))


@app.get("/content", response_model=List[ContentRec], tags=["Recommandations"])
def get_content_based(
    title: str = Query(..., description="Titre du livre de reference"),
    top_n: int = Query(10, ge=1, le=50),
    exclude_same_author: bool = Query(False),
):
    """Recommandations basees sur le contenu (TF-IDF + Cosinus)."""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modeles non charges")
    try:
        result = recommender.get_content_recommendations(
            title_query=title, top_n=top_n, exclude_same_author=exclude_same_author
        )
        return enrich_books(result.to_dict(orient="records"))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/collaborative", response_model=List[CollaborativeRec], tags=["Recommandations"])
def get_collaborative(
    book_idx: int = Query(..., description="Index du livre"),
    top_n: int = Query(10, ge=1, le=50),
):
    """Recommandations par filtrage collaboratif (KNN Item-Based)."""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modeles non charges")
    try:
        result = recommender.get_collaborative_recommendations(book_idx=book_idx, top_n=top_n)
        return enrich_books(result.to_dict(orient="records"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/mf", response_model=List[MFRec], tags=["Recommandations"])
def get_matrix_factorization(
    user_idx: int = Query(..., description="Index de l'utilisateur"),
    top_n: int = Query(10, ge=1, le=50),
):
    """Recommandations par factorisation matricielle (SVD)."""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modeles non charges")
    try:
        result = recommender.get_mf_recommendations(user_idx=user_idx, top_n=top_n)
        return enrich_books(result.to_dict(orient="records"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/hybrid", response_model=List[HybridRec], tags=["Recommandations"])
def get_hybrid(
    user_idx: int = Query(..., description="Index de l'utilisateur"),
    title: Optional[str] = Query(None, description="Titre de reference (optionnel)"),
    top_n: int = Query(10, ge=1, le=50),
    w_cb: float = Query(0.0, ge=0.0, le=1.0, description="Poids Content-Based"),
    w_cf: float = Query(0.4, ge=0.0, le=1.0, description="Poids Collaboratif"),
    w_mf: float = Query(0.6, ge=0.0, le=1.0, description="Poids Factorisation Matricielle"),
):
    """Recommandations hybrides (fusion ponderee CB + CF + MF).

    Les poids par defaut (CB=0.0, CF=0.4, MF=0.6) refletent les resultats
    de l'optimisation par grid search (Cellule 10-ter du notebook),
    tenant compte du fait que seulement ~10% des livres ont des metadata.
    """
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modeles non charges")
    try:
        result = recommender.get_hybrid_recommendations(
            user_idx=user_idx, title_query=title, top_n=top_n,
            w_cb=w_cb, w_cf=w_cf, w_mf=w_mf,
        )
        return enrich_books(result.to_dict(orient="records"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Systeme"])
def health_check():
    if recommender is None or not recommender.is_loaded():
        raise HTTPException(status_code=503, detail="Service indisponible")
    return {"status": "healthy", "models_loaded": True}
