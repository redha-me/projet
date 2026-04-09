Based on my analysis of the notebook code, here are the columns you can safely remove from each dataset:

📊 Columns Analysis
✅ collaborative_books_df.csv (ratings)
USED columns:

user_id_mapping - for collaborative filtering
book_id_mapping - join key with metadata
title - for display and lookups
Actual Rating - ground truth for recommendations
❌ REMOVE these columns:

Unnamed: 0 - just an index
book_id - redundant (we use book_id_mapping)
Predicted Rating - from a previous model, not used
✅ collaborative_book_metadata.csv (books_meta)
USED columns:

book_id_mapping - join key
title - content-based + display
name (author) - TF-IDF feature
genre - TF-IDF feature
description - TF-IDF feature
❌ REMOVE these columns:

Unnamed: 0 - just an index
book_id - redundant
image_url - not used in recommendation logic
url - external link, not needed
num_pages - could be useful but not used
ratings_count - popularity signal but not used
✅ user_id_map.csv
⚠️ NOT USED AT ALL - This file is loaded but never actually used in any recommendation computation! You could:

Remove it entirely from the notebook, OR
Keep it only if you need traceability to original user IDs for auditing
Recommendation: I can update the notebook to load only the necessary columns, which will:

Reduce memory usage
Speed up data loading
Make the code cleaner
Would you like me to update the notebook to load only the essential columns?


first
# 📚 Système intelligent de recommandation de livres
### Projet complet (Content-Based + Collaborative + Hybrid)

Ce notebook construit un système de recommandation **pas à pas** à partir du dataset Kaggle :
- https://www.kaggle.com/datasets/thedevastator/book-recommender-system-itembased

## 🎯 Objectifs
1. Générer des recommandations personnalisées pour chaque utilisateur.
2. Identifier les livres similaires pour proposer des suggestions pertinentes.
3. Construire un moteur hybride combinant contenu + comportement utilisateur.

---
**Approche retenue :**
- Filtrage basé sur le contenu (`metadata`).
- Filtrage collaboratif item-based (`ratings`).
- Fusion hybride pondérée.

second
## 1) Choix des données (SSOT)

Nous utilisons **3 fichiers principaux** :
- `Dataset/collaborative_books_df.csv` : interactions utilisateur-livre (`Actual Rating`).
- `Dataset/collaborative_book_metadata.csv` : métadonnées livres (titre, auteur, genre, description).
- `Dataset/user_id_map.csv` : mapping utilisateur (utile pour traçabilité).

Nous **n'utilisons pas** dans le pipeline principal :
- `book_id_map.csv` (très volumineux, redondant ici).
- `book_titles.csv` (redondant avec `metadata.title`).

Cette stratégie simplifie les jointures et réduit le risque d'incohérences.


end 
## 5) Conclusion et prochaines étapes

### ✅ Ce que le système fait
- Recommandations **livre similaire** (content-based).
- Recommandations **livre similaire** (collaborative item-based).
- Recommandations **hybrides** plus robustes.
- Recommandations **personnalisées par utilisateur**.

### 🚀 Améliorations possibles
- Ajuster `alpha` automatiquement par validation.
- Ajouter un modèle matriciel (SVD/ALS) pour comparaison.
- Déployer via API (FastAPI) + interface web (Streamlit).
- Ajouter diversité/novelty pour éviter recommandations trop similaires.




missing values
duplicates
 mappings
rating range
sparsity
activity filtering
metadata coverage
consistency checks
 
filtrage minimum
Garder utilisateurs avec ≥ 3 notes
Garder livres avec ≥ 3 notes