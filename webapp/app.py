# =============================================================================
# app.py — Interface de recommandation de livres (Streamlit)
# =============================================================================
# Lancer avec : streamlit run webapp/app.py
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
from urllib.parse import quote_plus
from recommender import BookRecommender

# ── Configuration de la page ──────────────────────────────────────────────────
st.set_page_config(
    page_title="BookMatch — Decouvrez votre prochain livre favori",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personnalisé ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fc 100%);
    }
    .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1280px; }

    /* Hero */
    .hero {
        background: linear-gradient(135deg, #eef0fb 0%, #e8ecf8 50%, #dde3f0 100%);
        border-radius: 24px; padding: 3rem 2.5rem; margin-bottom: 2rem;
        text-align: center; position: relative; overflow: hidden;
        box-shadow: 0 8px 30px rgba(102,126,234,0.12);
    }
    .hero::before {
        content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(102,126,234,0.08) 0%, transparent 50%),
                    radial-gradient(circle at 70% 50%, rgba(118,75,162,0.06) 0%, transparent 50%);
        animation: heroGlow 8s ease-in-out infinite alternate;
    }
    @keyframes heroGlow { 0% { transform: translate(0, 0); } 100% { transform: translate(30px, -20px); } }
    .hero-title { font-size: 2.8rem; font-weight: 800; color: #1a202c; margin: 0 0 0.75rem 0; letter-spacing: -0.02em; position: relative; z-index: 1; }
    .hero-subtitle { font-size: 1.15rem; color: #4a5568; margin: 0 0 2.5rem 0; position: relative; z-index: 1; max-width: 600px; margin-left: auto; margin-right: auto; }
    .hero-steps { display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; position: relative; z-index: 1; }
    .hero-step { background: rgba(255,255,255,0.7); border: 1px solid rgba(102,126,234,0.15); border-radius: 16px; padding: 1.25rem 1.5rem; min-width: 160px; backdrop-filter: blur(10px); transition: transform 0.2s ease; }
    .hero-step:hover { transform: translateY(-4px); background: rgba(255,255,255,0.9); }
    .hero-step .step-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .hero-step .step-label { font-size: 0.85rem; color: #2d3748; font-weight: 500; margin: 0; }

    /* Stats bar */
    .stats-bar { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
    .stat-pill { background: white; border: 1px solid #e2e8f0; border-radius: 50px; padding: 0.6rem 1.2rem; display: flex; align-items: center; gap: 0.6rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); font-size: 0.9rem; font-weight: 600; color: #2d3748; }
    .stat-pill .stat-icon { font-size: 1.1rem; }
    .stat-pill .stat-num { color: #667eea; }

    /* Book Card */
    .book-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.94) 100%);
        border-radius: 16px; padding: 1.25rem 1.5rem; margin-bottom: 0.85rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
        border: 1px solid rgba(102,126,234,0.12);
        transition: transform 0.2s ease, box-shadow 0.2s ease; position: relative;
    }
    .book-card:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(15, 23, 42, 0.14); }
    .book-card-rank { position: absolute; top: 1.1rem; right: 1.2rem; font-size: 1.6rem; font-weight: 800; color: #eef0f8; }
    .book-title { font-size: 1.05rem; font-weight: 700; color: #1a202c; margin: 0 2rem 0.25rem 0; line-height: 1.3; }
    .book-author { font-size: 0.85rem; color: #718096; margin: 0 0 0.6rem 0; }
    .stars { color: #f6ad55; font-size: 0.95rem; letter-spacing: 1px; }
    .rating-num { font-size: 0.85rem; font-weight: 600; color: #4a5568; }
    .reason-tag { display: inline-block; font-size: 0.72rem; font-weight: 600; padding: 0.2rem 0.6rem; border-radius: 20px; letter-spacing: 0.02em; }
    .tag-popular { background: #fef3c7; color: #92400e; }
    .tag-similar { background: #e0f2fe; color: #0c4a6e; }
    .tag-personal { background: #f0fdf4; color: #166534; }

    /* Sections */
    .section-header { font-size: 1.5rem; font-weight: 700; color: #1a202c; margin: 0 0 0.3rem 0; }
    .section-sub { font-size: 0.9rem; color: #718096; margin: 0 0 1.5rem 0; }
    .empty-state { text-align: center; padding: 3rem 2rem; color: #a0aec0; }
    .empty-state .empty-icon { font-size: 3.5rem; margin-bottom: 1rem; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important; border: none; border-radius: 12px;
        padding: 0.7rem 2rem; font-size: 1rem; font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.35); width: 100%;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(102, 126, 234, 0.5); }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; background: #f7f8fc; padding: 6px; border-radius: 12px; margin-bottom: 1.5rem; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 0.5rem 1.2rem; font-weight: 500; font-size: 0.9rem; color: #4a5568; background: transparent; border: none; }
    .stTabs [aria-selected="true"] { background: white !important; color: #667eea !important; box-shadow: 0 2px 8px rgba(0,0,0,0.08); font-weight: 600; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background: #f7f8fc !important; border-right: 1px solid #e2e8f0; }
    section[data-testid="stSidebar"] * { color: #4a5568 !important; }
    section[data-testid="stSidebar"] .stSelectbox > div > div { background: white !important; border-color: #e2e8f0 !important; border-radius: 10px !important; color: #2d3748 !important; }

    /* Chart caption */
    .chart-caption { background: #f7f8fc; border-left: 3px solid #667eea; padding: 0.6rem 1rem; border-radius: 0 8px 8px 0; font-size: 0.85rem; color: #4a5568; margin-bottom: 1rem; }

    /* Style card */
    .style-card { background: #f7f8fc; border: 2px solid #e2e8f0; border-radius: 14px; padding: 1.2rem; text-align: center; cursor: pointer; transition: all 0.2s ease; }
    .style-card.active { border-color: #667eea; background: #eef0fb; }
    .style-card .sc-icon { font-size: 2rem; margin-bottom: 0.4rem; }
    .style-card .sc-title { font-weight: 600; font-size: 0.9rem; color: #2d3748; margin: 0; }
    .style-card .sc-desc { font-size: 0.75rem; color: #718096; margin: 0.25rem 0 0 0; }

    /* FAQ */
    .faq-item { background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.9rem 1rem; margin-bottom: 0.5rem; }
    .faq-q { font-weight: 600; font-size: 0.85rem; color: #2d3748 !important; margin: 0 0 0.35rem 0; }
    .faq-a { font-size: 0.8rem; color: #718096 !important; margin: 0; line-height: 1.5; }

    h1, h2, h3, h4, h5, h6 { color: #1a202c; }
    .stMarkdown p { color: #4a5568; }

    /* Book cover */
    .book-cover { width: 64px; min-width: 64px; height: 90px; object-fit: cover; border-radius: 8px; box-shadow: 0 4px 14px rgba(15,23,42,0.18); background: linear-gradient(135deg, #edf2f7, #dbeafe); }
    .book-cover-placeholder { width: 64px; min-width: 64px; height: 90px; border-radius: 8px; background: linear-gradient(135deg, rgba(102,126,234,0.18), rgba(118,75,162,0.12)); display: flex; align-items: center; justify-content: center; font-size: 2rem; color: #8794ff; }
    .book-card a { text-decoration: none; color: inherit; }
    .goodreads-btn { display: inline-block; font-size: 0.72rem; font-weight: 600; padding: 3px 10px; border-radius: 20px; background: #f0eaff; color: #5a3da8; text-decoration: none; margin-top: 6px; }
    .goodreads-btn:hover { background: #e0d5ff; }
</style>
""", unsafe_allow_html=True)


# ── Fonctions auxiliaires ─────────────────────────────────────────────────────

def stars_html(avg_rating: float) -> str:
    """Convertit une note en etoiles visuelles (sur 5)."""
    r5 = avg_rating / 2.0 if avg_rating > 5 else avg_rating
    full = int(r5)
    half = 1 if (r5 - full) >= 0.5 else 0
    empty = 5 - full - half
    return ("\u2605" * full) + ("\u00BD" if half else "") + ("\u2606" * empty)


def book_card_html(title: str, author: str = None, genre: str = None,
                   avg_rating: float = None, n_ratings: int = None,
                   match_score: float = None, reason_tag: str = None,
                   tag_color: str = "#fef3c7", tag_text_color: str = "#92400e",
                   rank: int = None, image_url: str = None,
                   goodreads_url: str = None, metadata_quality: str = None) -> str:
    """Genere une carte livre en HTML."""
    # Sanitize inputs (pandas NaN/NaN can leak as "nan"/"undefined")
    import math
    if title is None or (isinstance(title, float) and math.isnan(title)):
        title = "Livre inconnu"
    else:
        title = str(title).strip() or "Livre inconnu"
    if author is not None and isinstance(author, float) and math.isnan(author):
        author = None
    if genre is not None and isinstance(genre, float) and math.isnan(genre):
        genre = None
    if goodreads_url is not None and isinstance(goodreads_url, float) and math.isnan(goodreads_url):
        goodreads_url = None

    rank_part = f'<span style="position:absolute;top:12px;right:14px;font-size:1.3rem;font-weight:800;color:#e2e8f0;">#{rank}</span>' if rank else ''

    link_url = goodreads_url if goodreads_url else f"https://www.goodreads.com/search?q={quote_plus(title)}"

    safe_title = quote_plus(title[:24])
    safe_image_url = image_url if image_url else f"https://dummyimage.com/128x192/e2e8f0/334155.png&text={safe_title}"

    img_part = (
        f'<img src="{safe_image_url}" class="book-cover" alt="{title}" loading="lazy" '
        f'onerror="this.onerror=null;this.outerHTML=\'<div class=&quot;book-cover-placeholder&quot;>📚</div>\';"/>'
    )

    author_value = author if author and str(author).strip() else "Auteur non disponible"
    genre_value = genre if genre and str(genre).strip() else "Genre non disponible"

    quality_badge = ''
    if metadata_quality == 'inferred':
        quality_badge = '<span style="font-size:0.65rem;color:#a0aec0;margin-left:6px;" title="Metadata inferée">⚙️ Inférée</span>'
    elif metadata_quality == 'partial':
        quality_badge = '<span style="font-size:0.65rem;color:#f6ad55;margin-left:6px;" title="Metadata partielle">⚠️ Partielle</span>'

    author_part = f'<span style="font-size:0.8rem;color:#718096;">✍️ {author_value}{quality_badge}</span>'
    genre_part = f'<span style="font-size:0.8rem;color:#4a5568;">🏷️ {genre_value}</span>'

    rating_part = ''
    if avg_rating is not None:
        s = stars_html(avg_rating)
        rating_part = f'<span style="color:#f6ad55;">{s}</span>&nbsp;<span style="font-size:0.82rem;font-weight:600;color:#4a5568;">{avg_rating:.1f}</span>'
        if n_ratings:
            rating_part += f'<span style="font-size:0.75rem;color:#a0aec0;"> &middot; {n_ratings:,} notes</span>'

    match_part = ''
    if match_score is not None:
        pct = min(max(int(match_score * 100), 4), 100)
        match_part = (f'<span style="font-size:0.7rem;color:#a0aec0;">Score&nbsp;</span>'
                      f'<span style="display:inline-block;width:70px;height:5px;background:#edf2f7;border-radius:5px;vertical-align:middle;">'
                      f'<span style="display:block;width:{pct}%;height:100%;background:#667eea;border-radius:5px;"></span></span>'
                      f'&nbsp;<span style="font-size:0.75rem;font-weight:600;color:#4a5568;">{pct}%</span>')

    tag_part = f'<span style="display:inline-block;font-size:0.7rem;font-weight:600;padding:2px 9px;border-radius:20px;background:{tag_color};color:{tag_text_color};">{reason_tag}</span>' if reason_tag else ''

    meta_items = [p for p in [rating_part, match_part] if p]
    meta_part = '<br>'.join(meta_items) if meta_items else ''

    text_col = (f'<div style="flex:1;min-width:0;">'
                f'{rank_part}'
                f'<p style="font-size:1rem;font-weight:700;color:#1a202c;margin:0 40px 2px 0;line-height:1.3;">{title}</p>'
                f'<p style="margin:2px 0 6px 0;">{author_part}</p>'
                f'<p style="margin:0 0 6px 0;">{genre_part}</p>'
                f'<p style="margin:0 0 6px 0;">{meta_part}</p>'
                f'<p style="margin:0;">{tag_part}</p>'
                f'</div>')

    card_content = (f'<div class="book-card" style="position:relative;display:flex;gap:14px;align-items:flex-start;">'
                    f'{img_part}{text_col}</div>')

    return f'<a href="{link_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:inherit; display:block;">{card_content}</a>'


# ── Chargement des modeles ────────────────────────────────────────────────────
@st.cache_resource
def load_recommender():
    try:
        return BookRecommender()
    except Exception as e:
        st.error(f"Impossible de charger le moteur de recommandation : {e}")
        st.info("Assurez-vous d'avoir execute le notebook pour generer les modeles dans le dossier 'models/'.")
        st.stop()

with st.spinner('Demarrage de BookMatch...'):
    time.sleep(0.5)
    recommender = load_recommender()

n_books = recommender.get_book_count()
n_users = recommender.get_user_count()
all_titles = recommender.get_all_titles()
# Books with TF-IDF metadata available for content-based similarity
available_for_similar = sorted([
    title for title in all_titles
    if recommender.title_to_idx.get(title.lower().strip()) in recommender.book_idx_to_row
])


# ── Section Hero ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <p class="hero-title">📚 BookMatch</p>
    <p class="hero-subtitle">Decouvrez votre prochain livre favori — propulse par une IA qui apprend vos gouts.</p>
    <div class="hero-steps">
        <div class="hero-step">
            <div class="step-icon">🔍</div>
            <p class="step-label">Recherchez un livre<br>que vous aimez</p>
        </div>
        <div class="hero-step">
            <div class="step-icon">✨</div>
            <p class="step-label">Notre IA trouve<br>des livres similaires</p>
        </div>
        <div class="hero-step">
            <div class="step-icon">📖</div>
            <p class="step-label">Decouvrez votre<br>prochaine lecture</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Barre de statistiques ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="stats-bar">
    <div class="stat-pill"><span class="stat-icon">📚</span><span>Catalogue de <span class="stat-num">{n_books:,}</span> livres</span></div>
    <div class="stat-pill"><span class="stat-icon">👥</span><span><span class="stat-num">{n_users:,}</span> lecteurs dans la communaute</span></div>
    <div class="stat-pill"><span class="stat-icon">🤖</span><span>Recommandations par IA</span></div>
    <div class="stat-pill"><span class="stat-icon">🎯</span><span>Personnalise pour vous</span></div>
</div>
""", unsafe_allow_html=True)


# ── Barre laterale ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 BookMatch")
    st.markdown("---")

    st.markdown("### COMMENT CA MARCHE")
    st.markdown("""
<div class="faq-item">
    <p class="faq-q">🔥 Tendances</p>
    <p class="faq-a">Les livres les plus apprecies de la communaute, classes par qualite et nombre de lecteurs.</p>
</div>
<div class="faq-item">
    <p class="faq-q">🔎 Livres similaires</p>
    <p class="faq-a">Choisissez un livre aime, nous trouvons des livres avec des themes et auteurs similaires.</p>
</div>
<div class="faq-item">
    <p class="faq-q">✨ Pour vous</p>
    <p class="faq-a">Selectionnez votre profil lecteur pour obtenir des recommandations personnalisees.</p>
</div>
<div class="faq-item">
    <p class="faq-q">📈 Statistiques</p>
    <p class="faq-a">Explorez les tendances et statistiques de notre communaute de lecteurs.</p>
</div>
<div class="faq-item">
    <p class="faq-q">🗂️ Parcourir</p>
    <p class="faq-a">Recherchez dans le catalogue complet de livres.</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### A PROPOS")
    st.markdown("""
<div class="faq-item">
    <p class="faq-q">Comment fonctionne l'IA ?</p>
    <p class="faq-a">BookMatch combine 3 techniques : analyse de contenu (themes et descriptions), comportement communautaire (lecteurs similaires), et predictions de gouts personnels — le meilleur des 3 mondes.</p>
</div>
<div class="faq-item">
    <p class="faq-q">Mes donnees sont-elles privees ?</p>
    <p class="faq-a">Les recommandations sont basees sur des habitudes de lecture anonymes. Aucune information personnelle n'est stockee.</p>
</div>
<div class="faq-item">
    <p class="faq-q">Methodes utilisees</p>
    <p class="faq-a">Filtrage collaboratif (KNN), factorisation matricielle (SVD), analyse de contenu (TF-IDF), et modele hybride avec optimisation des poids par grid search.</p>
</div>
""", unsafe_allow_html=True)


# ── Onglets ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔥 Tendances",
    "🔎 Livres similaires",
    "✨ Pour vous",
    "📈 Statistiques",
    "🗂️ Parcourir",
])


# ═══════════════════════════════════════════════════════════
# ONGLET 1 — TENDANCES
# ═══════════════════════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-header">🔥 Tendances</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Les livres les plus apprecies de la communaute — classes par qualite globale et nombre de lecteurs.</p>', unsafe_allow_html=True)

    c1, c2 = st.columns([1, 3])
    with c1:
        top_n_pop = st.slider("Nombre de livres a afficher", 5, 30, 10, key="pop_slider")
        confidence = st.select_slider(
            "Inclure les livres avec",
            options=["N'importe quel nombre de notes", "Au moins quelques notes", "Bien notes seulement", "Tres populaires seulement"],
            value="Bien notes seulement",
            key="conf_slider",
        )
        confidence_map = {
            "N'importe quel nombre de notes": 0,
            "Au moins quelques notes": 30,
            "Bien notes seulement": 60,
            "Tres populaires seulement": 85,
        }
        min_conf = confidence_map[confidence]

    popular = recommender.get_popular_recommendations(top_n=top_n_pop, min_confidence_percentile=min_conf)
    popular = recommender.sort_by_metadata_quality(popular)

    with c2:
        fig = px.bar(
            popular, x='title', y='score', color='avg_rating',
            hover_data=['n_ratings', 'avg_rating'], color_continuous_scale='Blues',
            labels={'title': 'Livre', 'score': 'Score de popularite', 'avg_rating': 'Note moyenne'},
        )
        fig.update_layout(
            xaxis_tickangle=-40, height=360, plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=100),
            font=dict(family='Inter', size=12), coloraxis_showscale=False,
            xaxis_title=None, yaxis_title="Score", title_text="",
        )
        fig.update_traces(hovertemplate='<b>%{x}</b><br>Note: %{customdata[1]:.1f}/10<br>Lecteurs: %{customdata[0]:,}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

    # Cartes livres
    books_with_images = []
    books_without_images = []

    for _, row in popular.iterrows():
        meta = recommender.get_book_meta(int(row['book_idx']))
        if meta.get('has_real_image', False):
            books_with_images.append((row, meta))
        else:
            books_without_images.append((row, meta))

    if books_with_images:
        st.markdown(f'<p style="font-size:0.9rem;font-weight:600;color:#166534;margin:1rem 0 0.5rem 0;">📸 Livres avec couverture ({len(books_with_images)})</p>', unsafe_allow_html=True)
        for rank, (row, meta) in enumerate(books_with_images, 1):
            st.markdown(book_card_html(
                title=row['title'], author=meta['author'] or None, genre=meta['genre'] or None,
                avg_rating=row['avg_rating'], n_ratings=int(row['n_ratings']),
                match_score=row['score'], reason_tag="🔥 Tendance",
                tag_color="#fef3c7", tag_text_color="#92400e", rank=rank,
                image_url=meta['image_url'] or None, goodreads_url=meta['goodreads_url'] or None,
                metadata_quality=meta.get('metadata_quality'),
            ), unsafe_allow_html=True)

    if books_without_images:
        if books_with_images:
            st.markdown('<hr style="border:none;border-top:2px dashed #e2e8f0;margin:1.5rem 0;">', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:0.9rem;font-weight:600;color:#6b7280;margin:0 0 0.5rem 0;">🎨 Livres avec couverture generee ({len(books_without_images)})</p>', unsafe_allow_html=True)
        for rank, (row, meta) in enumerate(books_without_images, 1):
            st.markdown(book_card_html(
                title=row['title'], author=meta['author'] or None, genre=meta['genre'] or None,
                avg_rating=row['avg_rating'], n_ratings=int(row['n_ratings']),
                match_score=row['score'], reason_tag="🔥 Tendance",
                tag_color="#fef3c7", tag_text_color="#92400e", rank=rank,
                image_url=meta['image_url'] or None, goodreads_url=meta['goodreads_url'] or None,
                metadata_quality=meta.get('metadata_quality'),
            ), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# ONGLET 2 — LIVRES SIMILAIRES
# ═══════════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-header">🔎 Livres similaires</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Choisissez un livre que vous avez aime, nous trouverons des livres aux themes et communautes similaires.</p>', unsafe_allow_html=True)

    selected_title = st.selectbox(
        "Choisissez un livre que vous avez lu et aime :",
        available_for_similar, key="similar_select",
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 📝 Livres aux themes similaires")
        st.markdown('<p style="font-size:0.82rem;color:#a0aec0;margin-top:-0.5rem;margin-bottom:1rem;">Base sur les descriptions, genres et style d\'ecriture</p>', unsafe_allow_html=True)
        try:
            cb_recs = recommender.get_content_recommendations(selected_title, top_n=8)
            if len(cb_recs) > 0:
                cb_recs = recommender.sort_by_metadata_quality(cb_recs)
                max_sim = cb_recs['similarity_score'].max()
                min_sim = cb_recs['similarity_score'].min()
                score_range = max_sim - min_sim if max_sim != min_sim else 1.0

                for rank, (_, row) in enumerate(cb_recs.iterrows(), 1):
                    norm_score = (row['similarity_score'] - min_sim) / score_range
                    meta = recommender.get_book_meta(int(row['book_idx']))
                    st.markdown(book_card_html(
                        title=row['title'], author=meta.get('author') or None,
                        genre=meta.get('genre') or None, match_score=norm_score,
                        reason_tag="📝 Themes similaires", tag_color="#e0f2fe", tag_text_color="#0c4a6e",
                        rank=rank, image_url=meta.get('image_url') or None,
                        goodreads_url=meta.get('goodreads_url') or None,
                        metadata_quality=meta.get('metadata_quality'),
                    ), unsafe_allow_html=True)
            else:
                st.markdown('<div class="empty-state"><div class="empty-icon">📭</div><p>Aucun livre similaire trouve par theme.</p></div>', unsafe_allow_html=True)
        except ValueError:
            st.warning("Ce livre n'a pas assez de metadata pour la recherche par theme. Essayez un autre titre !")

    with c2:
        st.markdown("#### 👥 Livres aimes par des lecteurs similaires")
        st.markdown('<p style="font-size:0.82rem;color:#a0aec0;margin-top:-0.5rem;margin-bottom:1rem;">Base sur les habitudes de lecture des lecteurs aux gouts similaires</p>', unsafe_allow_html=True)
        title_lower = selected_title.lower().strip()
        if title_lower in recommender.title_to_idx:
            book_idx = recommender.title_to_idx[title_lower]
            try:
                cf_recs = recommender.get_collaborative_recommendations(book_idx, top_n=8)
                if len(cf_recs) > 0:
                    cf_recs = recommender.sort_by_metadata_quality(cf_recs)
                    max_sim = cf_recs['similarity_score'].max()
                    min_sim = cf_recs['similarity_score'].min()
                    score_range = max_sim - min_sim if max_sim != min_sim else 1.0

                    for rank, (_, row) in enumerate(cf_recs.iterrows(), 1):
                        norm_score = (row['similarity_score'] - min_sim) / score_range
                        meta = recommender.get_book_meta(int(row['book_idx']))
                        st.markdown(book_card_html(
                            title=row['title'], genre=meta.get('genre') or None,
                            match_score=norm_score, reason_tag="👥 Apprecie aussi",
                            tag_color="#f0fdf4", tag_text_color="#166534", rank=rank,
                            image_url=meta.get('image_url') or None,
                            goodreads_url=meta.get('goodreads_url') or None,
                            metadata_quality=meta.get('metadata_quality'),
                        ), unsafe_allow_html=True)
                else:
                    st.markdown('<div class="empty-state"><div class="empty-icon">📭</div><p>Aucune recommandation communautaire pour ce livre.</p></div>', unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Impossible de charger les recommandations communautaires : {e}")
        else:
            st.info("Ce livre n'est pas dans notre base de donnees de lecture, mais vous pouvez trouver des livres similaires par theme a gauche !")


# ═══════════════════════════════════════════════════════════
# ONGLET 3 — POUR VOUS (Hybride)
# ═══════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-header">✨ Recommandations pour vous</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Une liste de lecture personnalisee — combinant tendances communautaires, analyse de contenu et votre historique de lecture.</p>', unsafe_allow_html=True)

    # --- Construire des profils lecteurs reels a partir des donnees ---
    PRESET_USER_IDS = [0, 5, 12, 25, 42, 67, 88, 100, 150, 200]

    def build_profile_display(idx):
        """Construit un profil lecteur descriptif a partir des donnees reelles."""
        user_data = recommender.df[recommender.df['user_idx'] == idx]
        n_books_read = len(user_data)
        avg_rating = user_data['rating'].mean() if n_books_read > 0 else 0

        # Determiner le profil de lecture
        if avg_rating >= 4.5:
            personality = "Enthousiaste"
            emoji = "🌟"
            desc = "Note generalement haut — aime ce qu'il lit"
        elif avg_rating >= 3.8:
            personality = "Equilibre"
            emoji = "⚖️"
            desc = "Apprecie une variete de styles et genres"
        elif avg_rating >= 3.0:
            personality = "Selectif"
            emoji = "🎯"
            desc = "Note avec discernement, gouts affirmes"
        else:
            personality = "Exigeant"
            emoji = "🔍"
            desc = "Difficile a impressionner, standards eleves"

        if n_books_read >= 10:
            activity = "Grand lecteur"
            activity_emoji = "📚"
        elif n_books_read >= 5:
            activity = "Lecteur regulier"
            activity_emoji = "📖"
        else:
            activity = "Lecteur occasionnel"
            activity_emoji = "📕"

        # Top genres du user
        user_book_indices = user_data['book_idx'].tolist()
        genres_found = []
        for bidx in user_book_indices:
            g = recommender.book_idx_to_genre.get(bidx, '')
            if g and str(g).strip():
                genres_found.append(str(g).lower().strip())

        top_genre = "General"
        if genres_found:
            from collections import Counter
            genre_counts = Counter(genres_found)
            top_genre = genre_counts.most_common(1)[0][0].title()

        return {
            "label": f"{emoji} {personality} — {activity} ({n_books_read} livres, moy. {avg_rating:.1f}/5)",
            "personality": personality,
            "activity": activity,
            "n_books": n_books_read,
            "avg_rating": avg_rating,
            "top_genre": top_genre,
            "desc": f"{activity_emoji} {activity} · {emoji} {personality} · Prefere: {top_genre}",
        }

    profiles = {}
    for uid in PRESET_USER_IDS:
        profiles[uid] = build_profile_display(uid)

    profile_labels = {uid: profiles[uid]["label"] for uid in PRESET_USER_IDS}

    st.markdown("#### 👤 Qui etes-vous ?")
    st.markdown('<p style="font-size:0.85rem;color:#718096;margin:-0.5rem 0 1rem 0;">Choisissez le profil qui ressemble le plus a vos habitudes de lecture.</p>', unsafe_allow_html=True)

    selected_label = st.selectbox(
        "Selectionnez votre profil lecteur",
        list(profile_labels.values()),
        key="profile_select",
    )

    # Trouver l'user_idx correspondant
    user_idx = None
    for uid, label in profile_labels.items():
        if label == selected_label:
            user_idx = uid
            break

    # Afficher la carte du profil selectionne
    if user_idx is not None:
        p = profiles[user_idx]
        st.markdown(f"""
<div style="background:linear-gradient(135deg,#f7f8fc,#eef0fb);border-radius:14px;padding:1rem 1.25rem;margin:0.5rem 0 1.5rem 0;border:1px solid #e2e8f0;">
    <div style="display:flex;gap:1rem;align-items:center;flex-wrap:wrap;">
        <div style="font-size:2.5rem;line-height:1;">👤</div>
        <div style="flex:1;min-width:200px;">
            <div style="font-weight:700;font-size:1.05rem;color:#1a202c;">Profil : {p['personality']}</div>
            <div style="font-size:0.85rem;color:#4a5568;">{p['desc']}</div>
        </div>
        <div style="text-align:right;font-size:0.85rem;color:#718096;">
            <div>📚 {p['n_books']} livres notes</div>
            <div>⭐ Moyenne : {p['avg_rating']:.1f}/5</div>
            <div>🏷️ Genre prefere : {p['top_genre']}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    c2, c3 = st.columns([2, 1])
    with c2:
        ref_title = st.selectbox(
            "📖 Base sur un livre precis ? (optionnel)",
            ["— Aucun livre precis —"] + all_titles, key="hybrid_title",
        )

    with c3:
        top_n_hybrid = st.slider("Resultats", 5, 20, 10, key="hybrid_slider")

    # Style de recommandation
    st.markdown("#### 🎛️ Quel type de recommandations souhaitez-vous ?")

    # Bouton d'aide avec popover native Streamlit
    with st.popover("❓ Comment ça marche ?", help="Cliquez pour comprendre chaque style"):
        st.markdown("##### 🌟 Equilibre")
        st.markdown("Un mélange de **communauté** (lecteurs similaires) et de **vos goûts personnels** (prédictions SVD). Le choix idéal si vous hésitez.")
        st.caption("Poids : Contenu 0% · Communauté 40% · Vos goûts 60%")
        st.markdown("##### 👥 Communautaire")
        st.markdown("Se base sur les **habitudes de lecteurs similaires à vous**. Parfait pour découvrir des pépites que la communauté adore.")
        st.caption("Poids : Contenu 0% · Communauté 65% · Vos goûts 35%")
        st.markdown("##### 📝 Par contenu")
        st.markdown("Analyse les **thèmes, genres et descriptions** via TF-IDF. Utile quand vous sélectionnez un **livre de référence** ci-dessus.")
        st.caption("Poids : Contenu 35% · Communauté 30% · Vos goûts 35%")

    rec_style = st.radio(
        "Choisissez un style",
        ["🌟 Equilibre", "👥 Communautaire", "📝 Par contenu"],
        horizontal=True, key="rec_style", label_visibility="collapsed",
    )

    # Poids hybrides — alignes avec les resultats du grid search du notebook
    # Les poids par defaut sont CF=0.4, MF=0.6 (CB=0 car metadata limitee)
    weights_map = {
        "🌟 Equilibre":         (0.0, 0.40, 0.60),
        "👥 Communautaire":     (0.0, 0.65, 0.35),
        "📝 Par contenu":       (0.35, 0.30, 0.35),
    }
    w_cb, w_cf, w_mf = weights_map[rec_style]

    title_query = ref_title if ref_title != "— Aucun livre precis —" else None

    if st.button("✨ Obtenir mes recommandations", key="hybrid_btn"):
        with st.spinner("Recherche des meilleurs livres pour vous..."):
            try:
                hybrid_recs = recommender.get_hybrid_recommendations(
                    user_idx=user_idx, title_query=title_query,
                    top_n=top_n_hybrid, w_cb=w_cb, w_cf=w_cf, w_mf=w_mf,
                )
                hybrid_recs = recommender.sort_by_metadata_quality(hybrid_recs)

                st.success(f"Voici **{len(hybrid_recs)} selections personnalisees** pour le profil **{p['personality']}** !")

                max_score = hybrid_recs['hybrid_score'].max()
                min_score = hybrid_recs['hybrid_score'].min()
                score_range = max_score - min_score if max_score != min_score else 1.0

                hyb_with_images = []
                hyb_without_images = []

                for _, row in hybrid_recs.iterrows():
                    norm_score = (row['hybrid_score'] - min_score) / score_range
                    meta = recommender.get_book_meta(int(row['book_idx']))
                    if meta.get('has_real_image', False):
                        hyb_with_images.append((row, meta))
                    else:
                        hyb_without_images.append((row, meta))

                if hyb_with_images:
                    for rank, (row, meta) in enumerate(hyb_with_images, 1):
                        norm_score = (row['hybrid_score'] - min_score) / score_range
                        st.markdown(book_card_html(
                            title=row['title'], author=meta.get('author') or None,
                            genre=meta.get('genre') or None, match_score=norm_score,
                            reason_tag="✨ Pour vous", tag_color="#f0fdf4", tag_text_color="#166534",
                            rank=rank, image_url=meta.get('image_url') or None,
                            goodreads_url=meta.get('goodreads_url') or None,
                            metadata_quality=meta.get('metadata_quality'),
                        ), unsafe_allow_html=True)

                if hyb_without_images:
                    if hyb_with_images:
                        st.markdown('<hr style="border:none;border-top:2px dashed #e2e8f0;margin:1.5rem 0;">', unsafe_allow_html=True)
                        st.markdown(f'<p style="font-size:0.85rem;font-weight:600;color:#6b7280;margin:0 0 0.75rem 0;">🎨 Livres avec couverture generee ({len(hyb_without_images)})</p>', unsafe_allow_html=True)
                    for rank, (row, meta) in enumerate(hyb_without_images, 1):
                        norm_score = (row['hybrid_score'] - min_score) / score_range
                        st.markdown(book_card_html(
                            title=row['title'], author=meta.get('author') or None,
                            genre=meta.get('genre') or None, match_score=norm_score,
                            reason_tag="✨ Pour vous", tag_color="#f0fdf4", tag_text_color="#166534",
                            rank=rank, image_url=meta.get('image_url') or None,
                            goodreads_url=meta.get('goodreads_url') or None,
                            metadata_quality=meta.get('metadata_quality'),
                        ), unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")


# ═══════════════════════════════════════════════════════════
# ONGLET 4 — STATISTIQUES
# ═══════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-header">📈 Statistiques de la communaute</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Explorez les tendances et habitudes de lecture de notre communaute.</p>', unsafe_allow_html=True)

    # Distribution des notes
    st.markdown("#### Comment les lecteurs notent-ils les livres ?")
    st.markdown('<div class="chart-caption">📊 La plupart des lecteurs ont tendance a noter positivement les livres qu\'ils terminent.</div>', unsafe_allow_html=True)

    ratings_data = recommender.df['rating'].value_counts().sort_index().reset_index()
    ratings_data.columns = ['Note', 'Nombre']
    fig_ratings = px.bar(
        ratings_data, x='Note', y='Nombre', color='Nombre',
        color_continuous_scale='Blues', labels={'Note': 'Note', 'Nombre': 'Nombre de notes'},
        text='Nombre',
    )
    fig_ratings.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        height=320, margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_showscale=False, font=dict(family='Inter'),
    )
    fig_ratings.update_traces(texttemplate='%{text:,}', textposition='outside')
    st.plotly_chart(fig_ratings, use_container_width=True)

    st.markdown("---")

    # Livres les plus lus
    st.markdown("#### Livres les plus lus de la communaute")
    st.markdown('<div class="chart-caption">📚 Les livres que le plus grand nombre de personnes ont lus et notes.</div>', unsafe_allow_html=True)

    book_counts = recommender.df.groupby('book_idx').size().reset_index(name='Nombre de lecteurs')
    book_counts['Livre'] = book_counts['book_idx'].map(recommender.idx_to_title)
    top_15 = book_counts.nlargest(15, 'Nombre de lecteurs')

    fig_pop = px.bar(
        top_15, x='Livre', y='Nombre de lecteurs', color='Nombre de lecteurs',
        color_continuous_scale='Purples', text='Nombre de lecteurs',
    )
    fig_pop.update_layout(
        xaxis_tickangle=-40, height=420, plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=110),
        coloraxis_showscale=False, font=dict(family='Inter'), xaxis_title=None,
    )
    fig_pop.update_traces(texttemplate='%{text:,}', textposition='outside', cliponaxis=False)
    st.plotly_chart(fig_pop, use_container_width=True)

    # Treemap des clusters
    cluster_data = getattr(recommender, 'cluster_to_book_idxs', None)
    if cluster_data and len(cluster_data) > 0:
        st.markdown("---")
        st.markdown("#### Comment les livres sont-ils groupes ?")
        st.markdown('<div class="chart-caption">🗂️ Notre IA regroupe les livres en clusters bases sur les themes et le comportement des lecteurs.</div>', unsafe_allow_html=True)
        # Sort clusters by size for cleaner display
        sorted_clusters = sorted(cluster_data.items(), key=lambda x: len(x[1]), reverse=True)
        cluster_sizes = [len(v) for _, v in sorted_clusters]
        cluster_names = [f"Groupe {k+1} ({s} livres)" for k, s in sorted_clusters]
        fig_cluster = px.treemap(
            names=cluster_names,
            values=cluster_sizes,
            color=cluster_sizes,
            color_continuous_scale='Teal',
        )
        fig_cluster.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig_cluster, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# ONGLET 5 — PARCOURIR
# ═══════════════════════════════════════════════════════════
with tab5:
    st.markdown('<p class="section-header">🗂️ Parcourir le catalogue</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Recherchez dans notre catalogue complet. Cliquez sur un titre dans n\'importe quel onglet pour explorer.</p>', unsafe_allow_html=True)

    bc1, bc2 = st.columns([3, 1])
    with bc1:
        search_query = st.text_input("🔍 Rechercher par titre...", key="explore_search",
                                     placeholder="ex. Harry Potter, Le Petit Prince...")
    with bc2:
        max_results = st.selectbox("Afficher", [25, 50, 100], index=0, key="max_browse")

    titles_filtered = [t for t in all_titles if search_query.lower() in t.lower()] if search_query else all_titles
    total = len(titles_filtered)
    st.markdown(f'<p style="font-size:0.9rem;color:#718096;margin-bottom:1rem;">Affichage de <strong>{min(max_results, total)}</strong> sur <strong>{total}</strong> livres{" correspondant a <em>" + search_query + "</em>" if search_query else ""}</p>', unsafe_allow_html=True)

    if total == 0:
        st.markdown('<div class="empty-state"><div class="empty-icon">🔍</div><p>Aucun livre trouve. Essayez un autre mot-cle.</p></div>', unsafe_allow_html=True)
    else:
        browse_data = []
        for title in titles_filtered[:max_results]:
            title_lower = title.lower().strip()
            avg_r, n_r = None, None
            b_idx = None
            if title_lower in recommender.title_to_idx:
                b_idx = recommender.title_to_idx[title_lower]
                book_data = recommender.df[recommender.df['book_idx'] == b_idx]
                if len(book_data) > 0:
                    avg_r = book_data['rating'].mean()
                    n_r = len(book_data)
            meta = recommender.get_book_meta(b_idx) if b_idx is not None else {}
            browse_data.append({
                'title': title, 'book_idx': b_idx, 'avg_rating': avg_r,
                'n_ratings': n_r, 'meta': meta,
                'has_image': meta.get('has_real_image', False),
            })

        browse_df = pd.DataFrame(browse_data).sort_values('has_image', ascending=False)

        books_with_images = browse_df[browse_df['has_image'] == True]
        books_without_images = browse_df[browse_df['has_image'] == False]

        if len(books_with_images) > 0:
            st.markdown(f'<p style="font-size:0.9rem;font-weight:600;color:#166534;margin:1rem 0 0.5rem 0;">📸 Livres avec couverture ({len(books_with_images)})</p>', unsafe_allow_html=True)
            for rank, (_, row) in enumerate(books_with_images.iterrows(), 1):
                st.markdown(book_card_html(
                    title=row['title'], author=row['meta'].get('author') or None,
                    genre=row['meta'].get('genre') or None, avg_rating=row['avg_rating'],
                    n_ratings=row['n_ratings'], rank=rank,
                    image_url=row['meta'].get('image_url') or None,
                    goodreads_url=row['meta'].get('goodreads_url') or None,
                    metadata_quality=row['meta'].get('metadata_quality'),
                ), unsafe_allow_html=True)

        if len(books_without_images) > 0:
            if len(books_with_images) > 0:
                st.markdown('<hr style="border:none;border-top:2px dashed #e2e8f0;margin:1.5rem 0;">', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size:0.9rem;font-weight:600;color:#6b7280;margin:0 0 0.5rem 0;">🎨 Livres avec couverture generee ({len(books_without_images)})</p>', unsafe_allow_html=True)
            for rank, (_, row) in enumerate(books_without_images.iterrows(), 1):
                st.markdown(book_card_html(
                    title=row['title'], author=row['meta'].get('author') or None,
                    genre=row['meta'].get('genre') or None, avg_rating=row['avg_rating'],
                    n_ratings=row['n_ratings'], rank=rank,
                    image_url=row['meta'].get('image_url') or None,
                    goodreads_url=row['meta'].get('goodreads_url') or None,
                    metadata_quality=row['meta'].get('metadata_quality'),
                ), unsafe_allow_html=True)
