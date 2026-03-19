import os
import time
import requests
import pandas as pd
import pickle
from dotenv import load_dotenv

load_dotenv()

OMDB_API_KEY  = os.getenv("OMDB_API_KEY")
OMDB_BASE_URL = os.getenv("OMDB_BASE_URL", "http://www.omdbapi.com")
MODELS_DIR    = os.path.join(os.path.dirname(__file__), "..", "models")


# ─────────────────────────────────────────
# 1. FETCH SINGLE MOVIE
# ─────────────────────────────────────────

def fetch_movie_omdb(title: str, year: str = None) -> dict:
    """
    Fetch movie data from OMDB by title.
    Returns poster, rating, awards etc.
    """
    params = {
        "t":      title,
        "apikey": OMDB_API_KEY,
        "type":   "movie",
    }
    if year:
        params["y"] = year

    try:
        response = requests.get(OMDB_BASE_URL, params=params, timeout=5)
        data = response.json()

        if data.get("Response") == "True":
            return {
                "poster":      data.get("Poster", "N/A"),
                "imdb_rating": data.get("imdbRating", "N/A"),
                "imdb_id":     data.get("imdbID", "N/A"),
                "awards":      data.get("Awards", "N/A"),
                "runtime":     data.get("Runtime", "N/A"),
                "country":     data.get("Country", "N/A"),
                "language":    data.get("Language", "N/A"),
                "box_office":  data.get("BoxOffice", "N/A"),
            }
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️ Request failed for '{title}': {e}")

    return {
        "poster":      "N/A",
        "imdb_rating": "N/A",
        "imdb_id":     "N/A",
        "awards":      "N/A",
        "runtime":     "N/A",
        "country":     "N/A",
        "language":    "N/A",
        "box_office":  "N/A",
    }


# ─────────────────────────────────────────
# 2. ENRICH FULL DATASET
# ─────────────────────────────────────────

def enrich_dataset(df: pd.DataFrame, limit: int = 100) -> pd.DataFrame:
    """
    Enrich dataframe with OMDB data.
    Fetches poster + imdb rating for each movie.

    Args:
        df:    preprocessed movies dataframe
        limit: number of movies to enrich (start small)
    """
    print(f"🎬 Enriching {limit} movies with OMDB data...")

    posters      = []
    imdb_ratings = []
    imdb_ids     = []
    runtimes     = []

    for i, row in df.head(limit).iterrows():
        title = row["title"]
        data  = fetch_movie_omdb(title)

        posters.append(data["poster"])
        imdb_ratings.append(data["imdb_rating"])
        imdb_ids.append(data["imdb_id"])
        runtimes.append(data["runtime"])

        if i % 10 == 0:
            print(f"   ✅ Fetched {i}/{limit}: {title} → {data['poster'][:40]}...")

        # Respect OMDB rate limit (1000/day free tier)
        time.sleep(0.1)

    # Fill remaining rows with N/A if limit < len(df)
    remaining = len(df) - limit
    posters      += ["N/A"] * remaining
    imdb_ratings += ["N/A"] * remaining
    imdb_ids     += ["N/A"] * remaining
    runtimes     += ["N/A"] * remaining

    df = df.copy()
    df["poster"]      = posters
    df["imdb_rating"] = imdb_ratings
    df["imdb_id"]     = imdb_ids
    df["runtime"]     = runtimes

    return df


# ─────────────────────────────────────────
# 3. SAVE ENRICHED DATASET
# ─────────────────────────────────────────

def save_enriched(df: pd.DataFrame):
    """Save enriched dataframe to disk."""
    path = os.path.join(MODELS_DIR, "movies_enriched.pkl")
    os.makedirs(MODELS_DIR, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(df, f)
    print(f"💾 Saved enriched dataset → models/movies_enriched.pkl")


def load_enriched() -> pd.DataFrame:
    """Load enriched dataframe from disk."""
    path = os.path.join(MODELS_DIR, "movies_enriched.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError("Enriched dataset not found. Run enrich_dataset() first.")
    with open(path, "rb") as f:
        return pickle.load(f)