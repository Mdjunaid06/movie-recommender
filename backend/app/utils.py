import pandas as pd
import numpy as np
import ast
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


# ─────────────────────────────────────────
# 1. LOADING
# ─────────────────────────────────────────

def load_raw_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    movies_path = os.path.join(DATA_DIR, "tmdb_5000_movies.csv")
    credits_path = os.path.join(DATA_DIR, "tmdb_5000_credits.csv")

    if not os.path.exists(movies_path) or not os.path.exists(credits_path):
        raise FileNotFoundError(
            "Dataset files not found."
        )

    movies_df = pd.read_csv(movies_path)
    credits_df = pd.read_csv(credits_path)
    return movies_df, credits_df


def merge_datasets(movies_df: pd.DataFrame, credits_df: pd.DataFrame) -> pd.DataFrame:
    credits_df = credits_df.rename(columns={"movie_id": "id"})
    merged = movies_df.merge(credits_df, on="id")

    if "title_y" in merged.columns:
        merged = merged.drop(columns=["title_y"])
        merged = merged.rename(columns={"title_x": "title"})

    return merged


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    essential_cols = ["title", "overview", "genres", "cast", "crew", "vote_average", "vote_count"]
    df = df.dropna(subset=essential_cols)
    df = df.drop_duplicates(subset=["title"])
    df = df.reset_index(drop=True)
    return df


# ─────────────────────────────────────────
# 2. PARSING HELPERS
# ─────────────────────────────────────────

def safe_parse(obj):
    """Safely parse a stringified Python list/dict."""
    try:
        return ast.literal_eval(obj)
    except (ValueError, SyntaxError):
        return []


def extract_genres(genres_str: str) -> list[str]:
    """Extract genre names → ['Action', 'Adventure']"""
    parsed = safe_parse(genres_str)
    return [g["name"] for g in parsed if "name" in g]


def extract_top_cast(cast_str: str, top_n: int = 3) -> list[str]:
    """Extract top N actor names from cast JSON."""
    parsed = safe_parse(cast_str)
    # Sort by order (lower = more prominent)
    parsed = sorted(parsed, key=lambda x: x.get("order", 99))
    return [p["name"] for p in parsed[:top_n] if "name" in p]


def extract_director(crew_str: str) -> list[str]:
    """Extract the director's name from crew JSON."""
    parsed = safe_parse(crew_str)
    directors = [p["name"] for p in parsed if p.get("job") == "Director"]
    return directors[:1]  # Return as list for consistency


def extract_keywords(keywords_str: str) -> list[str]:
    """Extract keyword names."""
    parsed = safe_parse(keywords_str)
    return [k["name"] for k in parsed if "name" in k]


# ─────────────────────────────────────────
# 3. TEXT NORMALIZATION
# ─────────────────────────────────────────

def collapse_spaces(name: str) -> str:
    """
    'James Cameron' → 'JamesCameron'
    Prevents TF-IDF from treating 'James' and 'Cameron' as separate tokens.
    """
    return name.replace(" ", "")


def normalize_list(items: list[str]) -> list[str]:
    """Lowercase + collapse spaces on each item."""
    return [collapse_spaces(item).lower() for item in items]


def tokenize_overview(text: str) -> list[str]:
    """Lowercase the overview and split into words."""
    if not isinstance(text, str):
        return []
    return text.lower().split()


# ─────────────────────────────────────────
# 4. FEATURE ENGINEERING
# ─────────────────────────────────────────

def build_tags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main preprocessing pipeline.
    Adds individual feature columns and a combined 'tags' column.
    """
    df = df.copy()

    # Parse each feature column
    df["genres_list"]   = df["genres"].apply(extract_genres)
    df["cast_list"]     = df["cast"].apply(extract_top_cast)
    df["director_list"] = df["crew"].apply(extract_director)
    df["keywords_list"] = df["keywords"].apply(extract_keywords)

    # Normalize (collapse spaces + lowercase)
    df["genres_norm"]   = df["genres_list"].apply(normalize_list)
    df["cast_norm"]     = df["cast_list"].apply(normalize_list)
    df["director_norm"] = df["director_list"].apply(normalize_list)
    df["keywords_norm"] = df["keywords_list"].apply(normalize_list)
    df["overview_norm"] = df["overview"].apply(tokenize_overview)

    # Combine all features into one 'tags' string
    # Director gets repeated 2x to give it more weight in TF-IDF
    df["tags"] = df.apply(
        lambda row: " ".join(
            row["overview_norm"]
            + row["genres_norm"]
            + row["cast_norm"]
            + row["director_norm"] * 2
            + row["keywords_norm"]
        ),
        axis=1,
    )

    return df


def select_final_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only the columns needed downstream."""
    cols = [
        "id", "title", "overview",
        "genres_list", "cast_list", "director_list", "keywords_list",
        "vote_average", "vote_count",
        "tags",
    ]
    return df[cols].reset_index(drop=True)


# ─────────────────────────────────────────
# 5. INSPECTION
# ─────────────────────────────────────────

def inspect_data(df: pd.DataFrame) -> None:
    print(f"\n✅ Shape: {df.shape}")
    print(f"\n📋 Columns: {list(df.columns)}")
    sample = df[["title", "genres_list", "cast_list", "director_list"]].head(3)
    print(f"\n🎬 Sample rows:\n{sample.to_string(index=False)}")
    print(f"\n🏷️  Sample tags (first movie):\n{df['tags'][0][:300]}...")