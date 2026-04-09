# =============================================================================
# recommender.py — Moteur de recommandation de livres
# =============================================================================
# Charge les modeles serialises depuis le dossier models/
# et fournit les fonctions de recommandation utilisees par l'API et Streamlit.
# =============================================================================

import os
import pickle
import json
import numpy as np
import pandas as pd
import joblib
from urllib.parse import quote_plus
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity

# ── Configuration ─────────────────────────────────────────────────────────────
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")


class BookRecommender:
    """Systeme de recommandation de livres — charge les modeles serialises."""

    def __init__(self, models_dir: str = MODELS_DIR):
        self.models_dir = models_dir
        self._loaded = False

        # Valeurs par defaut (seront ecrasees par config.json)
        self.W_CB = 0.0
        self.W_CF = 0.4
        self.W_MF = 0.6
        self.global_mean = 3.923

        self.load_models()

    def load_models(self):
        """Charge tous les modeles et donnees depuis le dossier models/."""
        try:
            # Config
            config_path = os.path.join(self.models_dir, "config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    self.config = json.load(f)
            else:
                self.config = {}

            # Matrices numpy/scipy — chargees en premier (toujours presentes)
            self.interactions_matrix = sparse.load_npz(
                os.path.join(self.models_dir, "interactions_matrix.npz")
            )
            self.interactions_matrix_T = self.interactions_matrix.T.tocsr()
            self.predicted_ratings = np.load(
                os.path.join(self.models_dir, "predicted_ratings.npy")
            ).astype(np.float32)  # Normalize to float32 (may have been saved as float16)
            self.user_bias = np.load(
                os.path.join(self.models_dir, "user_bias.npy")
            )
            self.book_bias = np.load(
                os.path.join(self.models_dir, "book_bias.npy")
            )

            # Modeles sklearn — optionnels (peuvent manquer si metadata incomplete)
            self.tfidf_vectorizer = None
            self.tfidf_matrix = None
            self.knn_model = None
            self.svd_model = None
            self.kmeans_model = None
            self.cluster_svd = None
            self.book_embeddings = None

            for name, filename in [
                ("tfidf_vectorizer", "tfidf_vectorizer.joblib"),
                ("knn_model", "knn_model.joblib"),
                ("svd_model", "svd_model.joblib"),
                ("kmeans_model", "kmeans_model.joblib"),
                ("cluster_svd", "cluster_svd.joblib"),
            ]:
                path = os.path.join(self.models_dir, filename)
                if os.path.exists(path):
                    setattr(self, name, joblib.load(path))

            # Matrices optionnelles
            for name, filename in [
                ("tfidf_matrix", "tfidf_matrix.npz"),
                ("book_embeddings", "book_embeddings.npy"),
            ]:
                path = os.path.join(self.models_dir, filename)
                if os.path.exists(path):
                    if "npz" in filename:
                        setattr(self, name, sparse.load_npz(path))
                    else:
                        setattr(self, name, np.load(path))

            # Lookups et DataFrames
            lookups_path = os.path.join(self.models_dir, "lookups.pkl")
            if os.path.exists(lookups_path):
                with open(lookups_path, "rb") as f:
                    lookups = pickle.load(f)
                self.idx_to_title = lookups.get("idx_to_title", {})
                self.title_to_idx = lookups.get("title_to_idx", {})
                self.book_idx_to_row = lookups.get("book_idx_to_row", {})
                self.book_mapping_to_idx_in_content = lookups.get("book_mapping_to_idx_in_content", {})
                self.book_idx_to_kmeans_cluster = lookups.get("book_idx_to_kmeans_cluster", {})
                self.cluster_to_book_idxs = lookups.get("cluster_to_book_idxs", {})
                self.book_idx_to_image_url = lookups.get("book_idx_to_image_url", {})
                self.book_idx_to_goodreads = lookups.get("book_idx_to_goodreads", {})
                self.book_idx_to_author = lookups.get("book_idx_to_author", {})
                self.book_idx_to_description = lookups.get("book_idx_to_description", {})
                self.book_idx_to_genre = lookups.get("book_idx_to_genre", {})
                self.metadata_quality = lookups.get("metadata_quality", {})
            else:
                self.idx_to_title = {}
                self.title_to_idx = {}
                self.book_idx_to_row = {}
                self.book_mapping_to_idx_in_content = {}
                self.book_idx_to_kmeans_cluster = {}
                self.cluster_to_book_idxs = {}
                self.book_idx_to_image_url = {}
                self.book_idx_to_goodreads = {}
                self.book_idx_to_author = {}
                self.book_idx_to_description = {}
                self.book_idx_to_genre = {}
                self.metadata_quality = {}

            # DataFrames
            df_path = os.path.join(self.models_dir, "df_interactions.parquet")
            if os.path.exists(df_path):
                self.df = pd.read_parquet(df_path)
            else:
                self.df = pd.DataFrame()

            df_content_path = os.path.join(self.models_dir, "df_content_reset.parquet")
            if os.path.exists(df_content_path):
                self.df_content_reset = pd.read_parquet(df_content_path)
            else:
                self.df_content_reset = pd.DataFrame()

            # Constantes depuis la config
            self.n_users = self.config.get("n_users", self.predicted_ratings.shape[0])
            self.n_books = self.config.get("n_books", self.predicted_ratings.shape[1])
            self.N_NEIGHBORS = self.config.get("n_neighbors", 20)

            # Poids hybrides — utilisons les valeurs optimisees si disponibles
            self.W_CB = self.config.get("w_cb", 0.0)
            self.W_CF = self.config.get("w_cf", 0.4)
            self.W_MF = self.config.get("w_mf", 0.6)
            self.global_mean = self.config.get("global_mean", 3.923)

            self._loaded = True
            print(f"Modeles charges depuis '{self.models_dir}'")
            print(f"  Utilisateurs: {self.n_users:,} | Livres: {self.n_books}")
            print(f"  Poids hybrides par defaut: CB={self.W_CB}, CF={self.W_CF}, MF={self.W_MF}")

        except Exception as e:
            print(f"Erreur de chargement: {e}")
            raise

    # ── Utilitaires ───────────────────────────────────────────────────────────

    @staticmethod
    def minmax_normalize(scores: np.ndarray) -> np.ndarray:
        """Normalisation min-max."""
        s_min, s_max = scores.min(), scores.max()
        if s_max - s_min < 1e-9:
            return np.zeros_like(scores)
        return (scores - s_min) / (s_max - s_min)

    # ── 1) Baseline : Popularite ponderee ─────────────────────────────────────

    def get_popular_recommendations(self, top_n: int = 10, exclude_book_idxs=None,
                                     min_confidence_percentile: int = 60) -> pd.DataFrame:
        """Recommandations basees sur la popularite (formule type IMDb)."""
        if exclude_book_idxs is None:
            exclude_book_idxs = []

        book_stats = (
            self.df.groupby("book_idx")["rating"]
            .agg(avg_rating="mean", n_ratings="count")
            .reset_index()
        )
        m = np.percentile(book_stats["n_ratings"], min_confidence_percentile)
        r_global = self.df["rating"].mean()
        v = book_stats["n_ratings"]
        r = book_stats["avg_rating"]
        book_stats["score"] = (v / (v + m)) * r + (m / (v + m)) * r_global

        if exclude_book_idxs:
            book_stats = book_stats[~book_stats["book_idx"].isin(exclude_book_idxs)]

        top_books = book_stats.nlargest(top_n, "score").copy()
        top_books["title"] = top_books["book_idx"].map(self.idx_to_title)

        return top_books[["book_idx", "title", "avg_rating", "n_ratings", "score"]].reset_index(drop=True)

    # ── 2) Content-Based : TF-IDF + Cosinus ───────────────────────────────────

    def get_content_recommendations(self, title_query: str, top_n: int = 10,
                                     exclude_same_author: bool = False) -> pd.DataFrame:
        """Recommandations basees sur la similarite de contenu (TF-IDF)."""
        if self.tfidf_vectorizer is None or self.tfidf_matrix is None:
            raise ValueError("Modele TF-IDF non disponible (metadata incomplete).")

        query_lower = title_query.lower().strip()
        if query_lower not in self.title_to_idx:
            candidates = [t for t in self.title_to_idx if query_lower in t]
            if not candidates:
                raise ValueError(f"Titre introuvable : '{title_query}'.")
            query_lower = candidates[0]

        ref_book_idx = self.title_to_idx[query_lower]
        if ref_book_idx not in self.book_idx_to_row:
            raise ValueError(f"Le livre '{title_query}' n'a pas de metadata textuelle.")

        ref_row = self.book_idx_to_row[ref_book_idx]
        ref_vector = self.tfidf_matrix[ref_row]
        sim_scores = cosine_similarity(ref_vector, self.tfidf_matrix).flatten()

        result = self.df_content_reset.copy()
        result["similarity_score"] = sim_scores.astype(np.float32)
        result = result[result.index != ref_row]

        if exclude_same_author:
            ref_author = self.df_content_reset.loc[ref_row, "author"]
            if ref_author and ref_author.lower() != "unknown":
                result = result[result["author"].str.lower() != ref_author.lower()]

        top = result.nlargest(top_n, "similarity_score").copy()
        top["book_idx"] = top["book_id_mapping"].map(self.book_mapping_to_idx_in_content)
        return top[["book_idx", "title", "author", "genre", "similarity_score"]].reset_index(drop=True)

    # ── 3) Collaborative Filtering : Item-Based KNN ───────────────────────────

    def get_collaborative_recommendations(self, book_idx: int, top_n: int = 10) -> pd.DataFrame:
        """Recommandations basees sur le filtrage collaboratif (KNN)."""
        if self.knn_model is None:
            raise ValueError("Modele KNN non disponible.")

        if book_idx < 0 or book_idx >= self.n_books:
            raise ValueError(f"book_idx hors plage : {book_idx}")

        distances, indices = self.knn_model.kneighbors(self.interactions_matrix_T[book_idx])
        distances = distances.flatten()
        indices = indices.flatten()
        similarities = 1 - distances

        result_list = []
        for sim, neighbor_idx in zip(similarities, indices):
            if neighbor_idx == book_idx:
                continue
            result_list.append({"book_idx": int(neighbor_idx), "similarity_score": sim})

        result_df = pd.DataFrame(result_list)
        result_df["title"] = result_df["book_idx"].map(self.idx_to_title)
        return result_df.head(top_n).reset_index(drop=True)[["book_idx", "title", "similarity_score"]]

    # ── 4) Matrix Factorization : SVD ─────────────────────────────────────────

    def get_mf_recommendations(self, user_idx: int, top_n: int = 10,
                                exclude_book_idxs=None) -> pd.DataFrame:
        """Recommandations basees sur la factorisation matricielle (SVD)."""
        if user_idx < 0 or user_idx >= self.predicted_ratings.shape[0]:
            raise ValueError(f"user_idx hors plage : {user_idx}")
        if exclude_book_idxs is None:
            exclude_book_idxs = set()

        user_predictions = self.predicted_ratings[user_idx].copy()
        books_already_read = set(self.interactions_matrix[user_idx].nonzero()[1])
        for bidx in books_already_read | set(exclude_book_idxs):
            user_predictions[bidx] = -np.inf

        top_indices = np.argsort(-user_predictions)[:top_n]
        results = []
        for rank, bidx in enumerate(top_indices, 1):
            if user_predictions[bidx] == -np.inf:
                break
            results.append({
                "rank": rank,
                "book_idx": int(bidx),
                "title": self.idx_to_title.get(bidx, "Unknown"),
                "predicted_rating": float(user_predictions[bidx]),
            })
        return pd.DataFrame(results)

    # ── 5) Hybrid Scorer : Fusion CB + CF + MF ────────────────────────────────

    def get_hybrid_recommendations(self, user_idx: int, title_query: str = None,
                                    top_n: int = 10,
                                    w_cb: float = None, w_cf: float = None,
                                    w_mf: float = None) -> pd.DataFrame:
        """Recommandations hybrides : fusion ponderee des 3 moteurs.

        Notes: Le poids CB est souvent 0 car seulement ~10% des livres ont
        des metadata textuelles. Les poids optimaux sont determines par
        grid search sur le test set (voir Cellule 10-ter du notebook).
        """
        if w_cb is None:
            w_cb = self.W_CB
        if w_cf is None:
            w_cf = self.W_CF
        if w_mf is None:
            w_mf = self.W_MF

        if user_idx < 0 or user_idx >= self.n_users:
            raise ValueError(f"user_idx {user_idx} hors plage")

        scores_cb = np.zeros(self.n_books)
        scores_cf = np.zeros(self.n_books)

        # MF : prediction directe
        mf_raw = self.predicted_ratings[user_idx].copy()
        scores_mf = self.minmax_normalize(mf_raw)

        # CB : similarite TF-IDF (seulement si un titre est fourni ET metadata dispo)
        ref_book_idx_hybrid = None
        if (title_query is not None and
                self.tfidf_matrix is not None and
                self.book_idx_to_row):
            query_lower = title_query.lower().strip()
            if query_lower not in self.title_to_idx:
                candidates = [t for t in self.title_to_idx if query_lower in t]
                if candidates:
                    query_lower = candidates[0]

            if query_lower in self.title_to_idx:
                ref_book_idx_hybrid = self.title_to_idx[query_lower]
                if ref_book_idx_hybrid in self.book_idx_to_row:
                    ref_row = self.book_idx_to_row[ref_book_idx_hybrid]
                    ref_vec = self.tfidf_matrix[ref_row]
                    sim_all = cosine_similarity(ref_vec, self.tfidf_matrix).flatten()
                    for i, row_data in self.df_content_reset.iterrows():
                        bidx = row_data.get("book_idx")
                        if pd.isna(bidx):
                            continue
                        bidx = int(bidx)
                        if 0 <= bidx < self.n_books:
                            scores_cb[bidx] = float(sim_all[i])

        # CF : KNN si titre de reference, sinon popularite
        if (ref_book_idx_hybrid is not None and
                ref_book_idx_hybrid < self.n_books and
                self.knn_model is not None):
            distances, indices = self.knn_model.kneighbors(
                self.interactions_matrix_T[ref_book_idx_hybrid],
                n_neighbors=min(self.N_NEIGHBORS + 1, self.n_books)
            )
            distances = distances.flatten()
            indices = indices.flatten()
            similarities = 1.0 - distances
            for sim, neighbor_idx in zip(similarities, indices):
                if neighbor_idx < self.n_books:
                    scores_cf[neighbor_idx] = float(sim)
        else:
            # Fallback : popularite
            book_counts = np.bincount(self.df["book_idx"].values, minlength=self.n_books).astype(float)
            scores_cf = self.minmax_normalize(book_counts)

        # Normalisation
        scores_cb_norm = self.minmax_normalize(scores_cb)
        scores_cf_norm = self.minmax_normalize(scores_cf)
        scores_mf_norm = scores_mf

        # Fusion
        hybrid_scores = w_cb * scores_cb_norm + w_cf * scores_cf_norm + w_mf * scores_mf_norm

        # Exclure les livres deja lus
        books_read = set(self.interactions_matrix[user_idx].nonzero()[1])
        if ref_book_idx_hybrid is not None:
            books_read.add(ref_book_idx_hybrid)
        for bidx in books_read:
            if bidx < self.n_books:
                hybrid_scores[bidx] = -np.inf

        # Top-N
        top_indices = np.argsort(-hybrid_scores)[:top_n + len(books_read)]
        results = []
        for bidx in top_indices:
            if hybrid_scores[bidx] == -np.inf:
                continue
            results.append({
                "book_idx": int(bidx),
                "title": self.idx_to_title.get(int(bidx), "Unknown"),
                "score_cb": float(scores_cb_norm[bidx]),
                "score_cf": float(scores_cf_norm[bidx]),
                "score_mf": float(scores_mf_norm[bidx]),
                "hybrid_score": float(hybrid_scores[bidx]),
            })
            if len(results) == top_n:
                break

        return pd.DataFrame(results)

    # ── 6) Infos utilitaires ──────────────────────────────────────────────────

    def get_all_titles(self) -> list:
        """Liste triee de tous les titres disponibles."""
        return sorted(set(self.idx_to_title.values()))

    def get_book_count(self) -> int:
        return self.n_books

    def get_user_count(self) -> int:
        return self.n_users

    def is_loaded(self) -> bool:
        return self._loaded

    def sort_by_metadata_quality(self, recommendations_df: pd.DataFrame) -> pd.DataFrame:
        """Trie pour afficher les livres avec metadata complete en premier."""
        if recommendations_df is None or len(recommendations_df) == 0:
            return recommendations_df
        if 'book_idx' not in recommendations_df.columns:
            return recommendations_df

        recommendations_df = recommendations_df.copy()
        recommendations_df['_has_image'] = recommendations_df['book_idx'].map(
            lambda x: 0 if (x in self.book_idx_to_image_url and
                          self.book_idx_to_image_url[x] and
                          str(self.book_idx_to_image_url[x]).strip()) else 1
        )

        quality_order = {'complete': 0, 'partial': 1, 'inferred': 2, 'missing': 3}
        if self.metadata_quality:
            recommendations_df['_quality_rank'] = recommendations_df['book_idx'].map(
                lambda x: quality_order.get(self.metadata_quality.get(x, 'missing'), 3)
            )
            recommendations_df = recommendations_df.sort_values(
                ['_has_image', '_quality_rank'], kind='mergesort'
            )
        else:
            recommendations_df = recommendations_df.sort_values('_has_image', kind='mergesort')

        recommendations_df = recommendations_df.drop(
            columns=['_has_image'] + (['_quality_rank'] if self.metadata_quality else [])
        )
        return recommendations_df

    def get_book_meta(self, book_idx: int) -> dict:
        """Retourne un dict de metadata riche pour un book_idx donne."""
        title = str(self.idx_to_title.get(book_idx, "Unknown")).strip() or "Unknown"
        author = str(self.book_idx_to_author.get(book_idx, "")).strip()
        genre = str(self.book_idx_to_genre.get(book_idx, "")).strip()
        image_url = str(self.book_idx_to_image_url.get(book_idx, "")).strip()
        goodreads_url = str(self.book_idx_to_goodreads.get(book_idx, "")).strip()
        description = str(self.book_idx_to_description.get(book_idx, "")).strip()

        has_real_image = (
            book_idx in self.book_idx_to_image_url and
            self.book_idx_to_image_url[book_idx] and
            str(self.book_idx_to_image_url[book_idx]).strip()
        )

        if self.metadata_quality:
            stored_quality = self.metadata_quality.get(book_idx, 'missing')
        else:
            if has_real_image and author and genre:
                stored_quality = 'complete'
            elif has_real_image or author or genre:
                stored_quality = 'partial'
            else:
                stored_quality = 'inferred'

        # Fallbacks intelligents
        if not author:
            author = "Auteur non disponible"
        if not genre:
            genre = "General"
        if not image_url:
            image_url = self._generate_cover_url(title, author)
        if not goodreads_url:
            query = quote_plus(f"{title} {author}".strip())
            goodreads_url = f"https://www.goodreads.com/search?q={query}"
        if not description:
            description = f"'{title}' est un livre de notre catalogue. Explorez ce titre pour en decouvrir plus."

        final_quality = stored_quality if stored_quality != 'missing' else 'inferred'

        return {
            "title": title,
            "image_url": image_url,
            "goodreads_url": goodreads_url,
            "author": author,
            "description": description,
            "genre": genre,
            "metadata_quality": final_quality,
            "has_real_image": bool(has_real_image),
        }

    def _generate_cover_url(self, title: str, author: str) -> str:
        """Genere une URL de couverture placeholder avec couleurs deterministes."""
        colors = [
            ("667eea", "764ba2"), ("f093fb", "f5576c"), ("4facfe", "00f2fe"),
            ("43e97b", "38f9d7"), ("fa709a", "fee140"), ("a18cd1", "fbc2eb"),
            ("ffecd2", "fcb69f"), ("ff9a9e", "fecfef"),
        ]
        color_idx = abs(hash(title)) % len(colors)
        color1, color2 = colors[color_idx]
        short_title = title[:30] + "..." if len(title) > 30 else title
        return f"https://dummyimage.com/320x480/{color1}/{color2}.png&text={quote_plus(short_title)}"
