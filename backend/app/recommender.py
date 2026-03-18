import os
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.utils import (
    load_raw_data,
    merge_datasets,
    basic_clean,
    build_tags,
    select_final_columns,
)

# ─────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
SIMILARITY_PATH = os.path.join(MODELS_DIR, "similarity.pkl")
DATAFRAME_PATH  = os.path.join(MODELS_DIR, "movies_df.pkl")


# ─────────────────────────────────────────
# 1. BUILD & SAVE MODEL
# ─────────────────────────────────────────

def build_model():
    """
    Full pipeline:
    Load data → Preprocess → TF-IDF → Cosine Similarity → Save to disk
    """
    print("📦 Loading and preprocessing data...")
    movies_df, credits_df = load_raw_data()
    df = merge_datasets(movies_df, credits_df)
    df = basic_clean(df)
    df = build_tags(df)
    df = select_final_columns(df)

    print("🔤 Applying TF-IDF Vectorizer...")
    tfidf = TfidfVectorizer(
        max_features=10000,   # top 10k words only
        stop_words="english", # remove 'the', 'is', 'and' etc
        ngram_range=(1, 2),   # include single words AND bigrams
    )

    # Shape: (4797, 10000)
    tfidf_matrix = tfidf.fit_transform(df["tags"])
    print(f"   ✅ TF-IDF matrix shape: {tfidf_matrix.shape}")

    print("📐 Computing cosine similarity matrix...")
    # Shape: (4797, 4797) — every movie vs every movie
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    print(f"   ✅ Similarity matrix shape: {similarity_matrix.shape}")

    print("💾 Saving model to disk...")
    os.makedirs(MODELS_DIR, exist_ok=True)

    with open(SIMILARITY_PATH, "wb") as f:
        pickle.dump(similarity_matrix, f)

    with open(DATAFRAME_PATH, "wb") as f:
        pickle.dump(df.reset_index(drop=True), f)

    print("   ✅ Saved similarity.pkl and movies_df.pkl")
    return df, similarity_matrix


# ─────────────────────────────────────────
# 2. LOAD SAVED MODEL
# ─────────────────────────────────────────

def load_model() -> tuple[pd.DataFrame, np.ndarray]:
    """Load precomputed model from disk."""
    if not os.path.exists(SIMILARITY_PATH) or not os.path.exists(DATAFRAME_PATH):
        raise FileNotFoundError(
            "Model not found. Run build_model() first."
        )

    with open(SIMILARITY_PATH, "rb") as f:
        similarity_matrix = pickle.load(f)

    with open(DATAFRAME_PATH, "rb") as f:
        df = pickle.load(f)

    return df, similarity_matrix


# ─────────────────────────────────────────
# 3. CORE RECOMMEND FUNCTION
# ─────────────────────────────────────────

def recommend(
    movie_title: str,
    df: pd.DataFrame,
    similarity_matrix: np.ndarray,
    top_n: int = 10,
) -> list[dict]:
    """
    Given a movie title, return top N similar movies.

    Args:
        movie_title: exact or partial movie title
        df: preprocessed movies dataframe
        similarity_matrix: cosine similarity matrix
        top_n: number of recommendations to return

    Returns:
        List of dicts with title, score, genres, cast, director
    """
    # Case-insensitive title matching
    title_lower = movie_title.strip().lower()
    matches = df[df["title"].str.lower() == title_lower]

    if matches.empty:
        # Try partial match
        matches = df[df["title"].str.lower().str.contains(title_lower)]

    if matches.empty:
        return []

    # Get index of first match
    movie_idx = matches.index[0]

    # Get similarity scores for this movie vs all others
    sim_scores = list(enumerate(similarity_matrix[movie_idx]))

    # Sort by score descending, skip the movie itself (score = 1.0)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = [s for s in sim_scores if s[0] != movie_idx]
    sim_scores = sim_scores[:top_n]

    # Build result list
    results = []
    for idx, score in sim_scores:
        row = df.iloc[idx]
        results.append({
            "title":        row["title"],
            "score":        round(float(score), 4),
            "score_pct":    f"{round(float(score) * 100, 1)}%",
            "genres":       row["genres_list"],
            "cast":         row["cast_list"],
            "director":     row["director_list"],
            "vote_average": row["vote_average"],
            "overview":     row["overview"][:200] + "...",
        })

    return results


# ─────────────────────────────────────────
# 4. SEARCH FUNCTION
# ─────────────────────────────────────────

def search_movies(query: str, df: pd.DataFrame, top_n: int = 10) -> list[dict]:
    """Search movies by partial title match."""
    query_lower = query.strip().lower()
    matches = df[df["title"].str.lower().str.contains(query_lower)]
    matches = matches.head(top_n)

    results = []
    for _, row in matches.iterrows():
        results.append({
            "title":        row["title"],
            "genres":       row["genres_list"],
            "cast":         row["cast_list"],
            "director":     row["director_list"],
            "vote_average": row["vote_average"],
            "overview":     row["overview"][:200] + "...",
        })

    return results