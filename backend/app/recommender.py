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

MODELS_DIR      = os.path.join(os.path.dirname(__file__), "..", "models")
SIMILARITY_PATH = os.path.join(MODELS_DIR, "similarity.pkl")
DATAFRAME_PATH  = os.path.join(MODELS_DIR, "movies_df.pkl")


# ─────────────────────────────────────────
# 1. BUILD & SAVE MODEL
# ─────────────────────────────────────────

def build_model():
    """Full pipeline: Load → Preprocess → TF-IDF → Cosine Similarity → Save"""
    print("📦 Loading and preprocessing data...")
    movies_df, credits_df = load_raw_data()
    df = merge_datasets(movies_df, credits_df)
    df = basic_clean(df)
    df = build_tags(df)
    df = select_final_columns(df)

    print("🔤 Applying TF-IDF Vectorizer...")
    tfidf = TfidfVectorizer(
        max_features=10000,
        stop_words="english",
        ngram_range=(1, 2),
    )
    tfidf_matrix = tfidf.fit_transform(df["tags"])
    print(f"   ✅ TF-IDF matrix shape: {tfidf_matrix.shape}")

    print("📐 Computing cosine similarity matrix...")
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
        raise FileNotFoundError("Model not found. Run build_model() first.")

    with open(SIMILARITY_PATH, "rb") as f:
        similarity_matrix = pickle.load(f)
    with open(DATAFRAME_PATH, "rb") as f:
        df = pickle.load(f)

    return df, similarity_matrix


# ─────────────────────────────────────────
# 3. SCORE HELPERS
# ─────────────────────────────────────────

def get_movie_score(
    movie_titles: list[str],
    df: pd.DataFrame,
    similarity_matrix: np.ndarray,
) -> np.ndarray:
    """
    Average cosine similarity scores across all input movies.
    Returns array of shape (n_movies,)
    """
    scores = np.zeros(len(df))
    matched = 0

    for title in movie_titles:
        title_lower = title.strip().lower()
        matches = df[df["title"].str.lower() == title_lower]

        if matches.empty:
            matches = df[df["title"].str.lower().str.contains(title_lower)]

        if matches.empty:
            print(f"   ⚠️  Movie not found: '{title}'")
            continue

        idx = matches.index[0]
        scores += similarity_matrix[idx]
        matched += 1

    if matched > 0:
        scores /= matched

    return scores


def get_actor_score(
    actors: list[str],
    df: pd.DataFrame,
) -> np.ndarray:
    """
    Score each movie by how many input actors appear in its cast.
    Normalized to [0, 1].
    """
    scores = np.zeros(len(df))

    for i, row in df.iterrows():
        cast_lower = [c.lower() for c in row["cast_list"]]
        match_count = sum(
            1 for actor in actors
            if actor.strip().lower() in cast_lower
        )
        scores[i] = match_count

    max_score = scores.max()
    if max_score > 0:
        scores /= max_score

    return scores


def get_director_score(
    directors: list[str],
    df: pd.DataFrame,
) -> np.ndarray:
    """
    Score 1.0 if movie's director matches any input director, else 0.
    """
    scores = np.zeros(len(df))

    for i, row in df.iterrows():
        director_lower = [d.lower() for d in row["director_list"]]
        for director in directors:
            if director.strip().lower() in director_lower:
                scores[i] = 1.0
                break

    return scores


def get_genre_score(
    genres: list[str],
    df: pd.DataFrame,
) -> np.ndarray:
    """
    Score each movie by genre overlap with input genres.
    Normalized to [0, 1].
    """
    scores = np.zeros(len(df))

    for i, row in df.iterrows():
        genre_lower = [g.lower() for g in row["genres_list"]]
        match_count = sum(
            1 for genre in genres
            if genre.strip().lower() in genre_lower
        )
        scores[i] = match_count

    max_score = scores.max()
    if max_score > 0:
        scores /= max_score

    return scores


# ─────────────────────────────────────────
# 4. POPULARITY HELPERS
# ─────────────────────────────────────────

def normalize_ratings(df: pd.DataFrame) -> np.ndarray:
    """
    Normalize vote_average to [0, 1] range.
    Uses IMDB weighted rating formula to penalize
    movies with very few votes.

    Formula: weighted = (v/(v+m)) * R + (m/(v+m)) * C
    Where:
        v = vote count for the movie
        m = minimum votes threshold (25th percentile)
        R = movie's average rating
        C = mean rating across all movies
    """
    v = df["vote_count"].values
    R = df["vote_average"].values
    C = df["vote_average"].mean()
    m = df["vote_count"].quantile(0.25)

    # IMDB weighted rating
    weighted = (v / (v + m)) * R + (m / (v + m)) * C

    # Normalize to [0, 1]
    min_w = weighted.min()
    max_w = weighted.max()
    normalized = (weighted - min_w) / (max_w - min_w)

    return normalized


def apply_popularity_boost(
    scores: np.ndarray,
    df: pd.DataFrame,
    similarity_weight: float = 0.7,
    popularity_weight: float = 0.3,
) -> np.ndarray:
    """
    Combine similarity scores with popularity scores.
    Final Score = (similarity × 0.7) + (popularity × 0.3)
    """
    popularity_scores = normalize_ratings(df)
    final = (similarity_weight * scores) + (popularity_weight * popularity_scores)
    return final


# ─────────────────────────────────────────
# 5. MULTI-INPUT WEIGHTED RECOMMEND
# ─────────────────────────────────────────

def recommend_weighted(
    df: pd.DataFrame,
    similarity_matrix: np.ndarray,
    movies:    list[str] = [],
    actors:    list[str] = [],
    directors: list[str] = [],
    genres:    list[str] = [],
    top_n:     int = 10,
    weights:   dict = None,
) -> list[dict]:
    """
    Multi-input weighted recommendation engine.

    Weights (default):
        movies    → 50%
        actors    → 20%
        directors → 15%
        genres    → 15%

    Then applies popularity boost:
        Final Score = (weighted_score × 0.7) + (popularity × 0.3)
    """
    if weights is None:
        weights = {
            "movies":    0.50,
            "actors":    0.20,
            "directors": 0.15,
            "genres":    0.15,
        }

    # Validate at least one input
    if not any([movies, actors, directors, genres]):
        raise ValueError("Provide at least one input: movies, actors, directors, or genres.")

    # Cap movies at 10
    movies = movies[:10]

    # ── Compute individual scores ──────────────
    final_scores = np.zeros(len(df))

    if movies:
        movie_scores = get_movie_score(movies, df, similarity_matrix)
        final_scores += weights["movies"] * movie_scores
        print(f"   🎬 Movie scores computed for: {movies}")

    if actors:
        actor_scores = get_actor_score(actors, df)
        final_scores += weights["actors"] * actor_scores
        print(f"   🎭 Actor scores computed for: {actors}")

    if directors:
        director_scores = get_director_score(directors, df)
        final_scores += weights["directors"] * director_scores
        print(f"   🎥 Director scores computed for: {directors}")

    if genres:
        genre_scores = get_genre_score(genres, df)
        final_scores += weights["genres"] * genre_scores
        print(f"   🎞️  Genre scores computed for: {genres}")

    # ── Apply popularity boost ─────────────────
    final_scores = apply_popularity_boost(final_scores, df)

    # ── Exclude input movies from results ──────
    input_indices = set()
    for title in movies:
        title_lower = title.strip().lower()
        matches = df[df["title"].str.lower() == title_lower]
        if not matches.empty:
            input_indices.add(matches.index[0])

    # ── Rank results ───────────────────────────
    scored = [
        (i, score)
        for i, score in enumerate(final_scores)
        if i not in input_indices
    ]
    scored = sorted(scored, key=lambda x: x[1], reverse=True)
    scored = scored[:top_n]

    # ── Build explanation ──────────────────────
    reasons = []
    if movies:
        reasons.append(f"movies like {', '.join(movies[:2])}")
    if actors:
        reasons.append(f"actor(s) {', '.join(actors[:2])}")
    if directors:
        reasons.append(f"director {', '.join(directors[:1])}")
    if genres:
        reasons.append(f"{', '.join(genres[:2])} genre")

    explanation = "Recommended because you liked " + " | ".join(reasons)

    # ── Build output ───────────────────────────
    results = []
    for idx, score in scored:
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
            "explanation":  explanation,
        })

    return results


# ─────────────────────────────────────────
# 6. SIMPLE SINGLE-MOVIE RECOMMEND
# ─────────────────────────────────────────

def recommend(
    movie_title: str,
    df: pd.DataFrame,
    similarity_matrix: np.ndarray,
    top_n: int = 10,
) -> list[dict]:
    """Wrapper around recommend_weighted for single movie input."""
    return recommend_weighted(
        df=df,
        similarity_matrix=similarity_matrix,
        movies=[movie_title],
        top_n=top_n,
    )


# ─────────────────────────────────────────
# 7. SEARCH
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