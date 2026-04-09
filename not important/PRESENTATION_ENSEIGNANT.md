# Présentation Enseignant - Système de Recommandation de Livres

## 1. Pitch en 30 secondes
Notre projet construit un système de recommandation de livres capable de proposer des suggestions personnalisées à partir des interactions utilisateur-livre et des métadonnées textuelles. Nous avons comparé plusieurs approches (Baseline, Content-Based, Collaborative Filtering, Matrix Factorization) puis conçu un modèle hybride pour obtenir un meilleur compromis entre pertinence, couverture et robustesse au cold-start.

---

## 2. Problématique et objectif pédagogique
### Problème métier
Comment recommander des livres pertinents à un utilisateur quand:
- les données sont très creuses (matrice sparse),
- il existe des utilisateurs/livres avec peu d’historique,
- les notes sont biaisées vers les valeurs élevées.

### Objectif du projet
- Concevoir un pipeline complet de recommandation.
- Évaluer et comparer plusieurs modèles.
- Justifier le choix final avec des métriques et une analyse critique.

---

## 3. Données utilisées
### Sources
- `collaborative_books_df.csv`: interactions (utilisateur, livre, note)
- `collaborative_book_metadata.csv`: description, genre, auteur
- `book_id_map.csv`, `user_id_map.csv`, `book_titles.csv`: mappages pour affichage

### Préparation
- Déduplication des métadonnées sur `book_id_mapping`
- Fusion LEFT JOIN pour conserver toutes les interactions
- Construction de deux tables:
  - `df_interactions` (base collaborative)
  - `df_content` (base contenu)

### Constat EDA
- Distribution de notes majoritairement sur 4-5 (biais positif)
- Cold-start significatif sur certains utilisateurs/livres
- Matrice utilisateur-livre très sparse

---

## 4. Méthodologie (CRISP-DM)
### 1. Business Understanding
Définition du besoin: recommander des livres de manière fiable.

### 2. Data Understanding
EDA, visualisations, contrôle qualité des données.

### 3. Data Preparation
Nettoyage, jointures, gestion des doublons, structuration des tables.

### 4. Modeling
Développement de 5 approches:
- Baseline
- Content-Based (TF-IDF + cosinus)
- Collaborative Item-Based (KNN)
- Matrix Factorization (SVD)
- Hybride (fusion pondérée)

### 5. Evaluation
Comparaison qualitative + métriques quantitatives (RMSE, MAE, confusion proxy).

### 6. Deployment (partiel)
Export des recommandations consolidées (`prediction_table.csv`) et artefacts visuels.

---

## 5. Modèles implémentés et logique
## 5.1 Baseline (popularité pondérée)
- Recommande les livres globalement les plus populaires.
- Avantage: simple, stable.
- Limite: pas de personnalisation.

## 5.2 Content-Based
- Vectorisation TF-IDF des descriptions.
- Similarité cosinus entre livres.
- Avantage: fonctionne pour cold-start utilisateur.
- Limite: dépend de la qualité du texte.

## 5.3 Collaborative Filtering Item-Based
- Matrice sparse utilisateur-livre.
- KNN (cosine) sur matrice transposée (livre-utilisateur).
- Avantage: capte les préférences collectives réelles.
- Limite: sensible au manque d’interactions.

## 5.4 Matrix Factorization (SVD)
- Décomposition en facteurs latents.
- Prédiction de notes manquantes.
- Avantage: bonne personnalisation.
- Limite: cold-start et choix des hyperparamètres.

## 5.5 Modèle Hybride
Fusion pondérée des scores:
$$
Score_{hybride} = w_{CB} \cdot score_{CB} + w_{CF} \cdot score_{CF} + w_{MF} \cdot score_{MF}
$$
- Nous avons utilisé un compromis empirique (CB, CF, MF) pour maximiser robustesse et pertinence.

---

## 6. Résultats à présenter
### Résultats qualitatifs
- Recommandations cohérentes sur des livres de référence.
- Bonne complémentarité des approches.
- Le modèle hybride évite les faiblesses d’un modèle unique.

### Résultats quantitatifs
- RMSE/MAE calculés pour la composante MF.
- Matrice de confusion proxy pour lecture pédagogique.
- Tableau comparatif final des modèles dans le notebook.

### Décision finale
Le modèle recommandé pour exploitation est l’Hybride, avec SVD comme moteur de personnalisation principal et Content-Based en support cold-start.

---

## 7. Limites et axes d’amélioration
### Limites actuelles
- Données de notes biaisées vers les évaluations élevées.
- Peu de signaux implicites (clics, temps de lecture, abandon).
- Déploiement technique non industrialisé (API/monitoring non finalisés).

### Améliorations futures
- Ajouter des métriques ranking (Precision@K, Recall@K, NDCG@K).
- Mettre en place une validation temporelle et des tests offline/online.
- Déployer une API de recommandation et un suivi continu des performances.

---

## 8. Script oral conseillé (10 minutes)
### Minute 0-1: Contexte
- Problème: recommander correctement malgré sparsité et cold-start.

### Minute 1-3: Données et préparation
- Sources, jointure LEFT, nettoyage, EDA.

### Minute 3-6: Modèles
- Baseline, CB, CF, MF, puis fusion hybride.

### Minute 6-8: Résultats
- Ce qui marche, métriques, tableau comparatif.

### Minute 8-9: Choix final
- Pourquoi hybride est le meilleur compromis.

### Minute 9-10: Limites et suite
- Déploiement, monitoring, améliorations prévues.

---

## 9. Questions probables de l’enseignant (et réponses courtes)
### Q1. Pourquoi un modèle hybride ?
Parce qu’il combine la personnalisation MF, la similarité de contenu et la logique comportementale CF, donc plus robuste qu’un modèle isolé.

### Q2. Comment gérez-vous le cold-start ?
Avec Content-Based et clustering quand les interactions sont insuffisantes.

### Q3. Pourquoi RMSE/MAE seulement sur MF ?
Parce que MF produit des prédictions explicites de notes; CB/CF sont plutôt des scores de similarité. Une extension naturelle est l’évaluation ranking @K.

### Q4. Quelle est votre contribution principale ?
Un pipeline complet et cohérent, avec comparaison multicritère et décision argumentée vers une architecture hybride.

---

## 10. Conclusion (phrase de fin)
Notre projet montre qu’en recommandation, la performance ne vient pas d’un seul algorithme, mais d’une intégration intelligente de plusieurs approches, validée par l’analyse des données et des métriques adaptées.
