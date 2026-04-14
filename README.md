# BookMatch — Système de Recommandation de Livres

[![Deploy on Render](https://img.shields.io/badge/Deploy-Render-blue?logo=render)](https://render.com)
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-yellow)](https://huggingface.co/spaces/redh2601/bookmatch?logs=container)

## 📖 Description

**BookMatch** est un système intelligent de recommandation de livres qui combine plusieurs approches de Machine Learning pour offrir des recommandations personnalisées et précises. Le projet suit la méthodologie **CRISP-DM** (Cross-Industry Standard Process for Data Mining).

🚀 **Application en ligne :** [BookMatch sur Hugging Face Spaces](https://huggingface.co/spaces/redh2601/bookmatch?logs=container)

## ✨ Fonctionnalités

- **Recommandation hybride** combinant 4 approches :
  - **Baseline** : recommandation basée sur la popularité
  - **Content-Based** : filtrage basé sur le contenu (TF-IDF)
  - **Collaborative Filtering** : filtrage collaboratif (KNN)
  - **Matrix Factorization** : factorisation de matrices (SVD)
  
- **Interface web interactive** développée avec Streamlit
- **API REST** pour l'intégration avec d'autres applications
- **Évaluation rigoureuse** avec métriques standard (RMSE, Recall@K)

## 🏗️ Architecture du Projet

```
projet/
├── Dataset/                          # Données brutes
│   ├── book_id_map.csv              # Mapping des identifiants de livres
│   ├── book_titles.csv              # Titres des livres
│   ├── collaborative_book_metadata.csv  # Métadonnées des livres
│   ├── collaborative_books_df.csv   # Interactions utilisateurs
│   └── user_id_map.csv              # Mapping des identifiants utilisateurs
├── models/                          # Modèles entraînés et sérialisés
│   ├── book_bias.npy               # Biais des livres (MF)
│   ├── book_embeddings.npy         # Embeddings des livres
│   ├── cluster_svd.joblib          # Clustering SVD
│   ├── config.json                 # Configuration du modèle
│   ├── df_content_reset.parquet    # Données content filtrées
│   ├── df_interactions.parquet     # Matrice d'interactions
│   └── interactions_matrix.npz     # Matrice clairsemée
├── webapp/                          # Application web
│   ├── app.py                       # Application Streamlit principale
│   ├── api.py                       # API REST
│   ├── recommender.py              # Moteur de recommandation
│   └── requirements.txt            # Dépendances Python
├── bookrecommendation.ipynb         # Notebook d'analyse et d'entraînement
├── Dockerfile                       # Configuration Docker
├── render.yaml                      # Configuration de déploiement Render
└── README.md                        # Ce fichier
```

## 🛠️ Technologies Utilisées

- **Python 3.11**
- **Data Science** : NumPy, Pandas, SciPy, scikit-learn, Surprise
- **Visualisation** : Matplotlib, Seaborn
- **NLP** : TF-IDF (scikit-learn)
- **Web** : Streamlit, FastAPI
- **Déploiement** : Docker, Render, Hugging Face Spaces

## 🚀 Installation et Utilisation

### Prérequis

- Python 3.11 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation Locale

1. **Cloner le repository**
```bash
git clone https://github.com/redha-me/projet.git
cd projet
```

2. **Installer les dépendances**
```bash
pip install -r webapp/requirements.txt
```

3. **Lancer l'application web**
```bash
streamlit run webapp/app.py --server.port 7860
```

4. **Accéder à l'application**
   
Ouvrez votre navigateur et accédez à : `http://localhost:7860`

## 🐳 Déploiement avec Docker

### Construire l'image Docker

```bash
docker build -t bookmatch .
```

### Exécuter le conteneur

```bash
docker run -p 7860:7860 bookmatch
```

L'application sera accessible sur `http://localhost:7860`

## ☁️ Déploiement sur Render

Le fichier `render.yaml` est déjà configuré pour un déploiement automatique sur Render :

1. Connectez-vous à [Render](https://render.com)
2. Importez votre repository
3. Render détectera automatiquement la configuration dans `render.yaml`
4. Déployez !

## 📊 Méthodologie CRISP-DM

Le projet suit les 6 phases de la méthodologie CRISP-DM :

| Phase | Description |
|-------|-------------|
| **1. Compréhension des données** | Chargement, exploration et audit qualité des fichiers CSV |
| **2. Préparation des données** | Nettoyage, détection de doublons, filtrage qualité |
| **3. Exploration (EDA)** | Analyses visuelles : distribution des notes, livres populaires, cold start |
| **4. Modélisation** | 4 approches : Baseline, Content-Based, Collaborative, Matrix Factorization |
| **5. Évaluation** | Train/test split, métriques standard (RMSE, Recall@K), optimisation hybride |
| **6. Déploiement** | Sérialisation des modèles, application web Streamlit, API REST |

## 📈 Données

Le dataset comprend :

- **196 296 interactions** utilisateur-livre
- **876 145 utilisateurs** uniques
- **917 livres** avec métadonnées
- Notes de 1 à 5 étoiles

### Architecture des Données

| Couche | Fichier(s) | Rôle |
|--------|------------|------|
| **Interactions (CF)** | `collaborative_books_df.csv` | Table centrale — notes réelles + mappings |
| **Métadonnées (CB)** | `collaborative_book_metadata.csv` | Texte riche pour TF-IDF (description, genre, auteur) |
| **Décodage identités** | `user_id_map.csv`, `book_id_map.csv`, `book_titles.csv` | Rétablir UUIDs / titres en sortie finale |

## 🎯 Modèles de Recommandation

### 1. Baseline (Popularité)
Recommande les livres les plus populaires et les mieux notés.

### 2. Content-Based (TF-IDF)
Utilise les descriptions, genres et auteurs pour trouver des livres similaires.

### 3. Collaborative Filtering (KNN)
Trouve des utilisateurs similaires et recommande leurs livres préférés.

### 4. Matrix Factorization (SVD)
Décompose la matrice d'interactions pour capturer les préférences latentes.

### Approche Hybride
Combine les 4 modèles avec des poids optimisés par grid search pour maximiser la qualité des recommandations.

## 🔌 API REST

Une API REST est disponible via `webapp/api.py` pour intégrer le système de recommandation dans d'autres applications.

### Exemple d'utilisation

```python
import requests

# Obtenir des recommandations pour un utilisateur
response = requests.post("http://localhost:8000/recommend", json={
    "user_id": 123,
    "num_recommendations": 10
})

recommendations = response.json()
```

## 📝 Auteur

Projet développé dans le cadre d'un projet de système de recommandation.

## 📄 Licence

Ce projet est open-source.

## 🤝 Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer votre branche (`git checkout -b feature/AmazingFeature`)
3. Commiter vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Pusher vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📞 Support

Pour toute question ou problème, n'hésitez pas à ouvrir une issue ou à contacter l'auteur.

---

⭐ **Si ce projet vous a été utile, merci de lui donner une étoile !**
