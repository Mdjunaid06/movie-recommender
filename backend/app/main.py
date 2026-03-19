from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd

from app.recommender import load_model, recommend_weighted, search_movies
from app.omdb_client import fetch_movie_omdb

# ─────────────────────────────────────────
# LIFESPAN — Load model once at startup
# ─────────────────────────────────────────

ml_model = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML model into memory when API starts."""
    print("🚀 Loading ML model...")
    df, similarity_matrix = load_model()
    ml_model["df"] = df
    ml_model["similarity_matrix"] = similarity_matrix
    print("✅ Model loaded and ready!")
    yield
    ml_model.clear()


# ─────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────

app = FastAPI(
    title="🎬 Movie Recommender API",
    description="Hybrid movie recommendation system with multi-input weighted scoring",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — Allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: ["https://your-frontend.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────

class RecommendRequest(BaseModel):
    movies:    list[str] = Field(default=[], max_length=10, description="Up to 10 movie titles")
    actors:    list[str] = Field(default=[], description="Actor names")
    directors: list[str] = Field(default=[], description="Director names")
    genres:    list[str] = Field(default=[], description="Genre names")
    top_n:     int       = Field(default=10, ge=1, le=50, description="Number of results")

class MovieCard(BaseModel):
    title:        str
    score:        float
    score_pct:    str
    genres:       list[str]
    cast:         list[str]
    director:     list[str]
    vote_average: float
    overview:     str
    explanation:  str
    poster:       str = "N/A"
    imdb_rating:  str = "N/A"

class RecommendResponse(BaseModel):
    results:     list[MovieCard]
    total:       int
    query_info:  dict


# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "🎬 Movie Recommender API is running!",
        "docs":    "/docs",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status":      "healthy",
        "model_loaded": "df" in ml_model,
        "total_movies": len(ml_model["df"]) if "df" in ml_model else 0,
    }


@app.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest):
    """
    Get movie recommendations based on multiple inputs.

    - **movies**: list of movie titles you liked (up to 10)
    - **actors**: list of actor names you like
    - **directors**: list of director names you like
    - **genres**: list of genres you prefer
    - **top_n**: number of recommendations to return
    """
    # Validate at least one input provided
    if not any([request.movies, request.actors, request.directors, request.genres]):
        raise HTTPException(
            status_code=400,
            detail="Provide at least one of: movies, actors, directors, genres"
        )

    df                = ml_model["df"]
    similarity_matrix = ml_model["similarity_matrix"]

    try:
        results = recommend_weighted(
            df=df,
            similarity_matrix=similarity_matrix,
            movies=request.movies,
            actors=request.actors,
            directors=request.directors,
            genres=request.genres,
            top_n=request.top_n,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No recommendations found. Try different inputs."
        )

    # Enrich top 10 results with OMDB poster
    enriched = []
    for r in results[:10]:
        omdb_data = fetch_movie_omdb(r["title"])
        enriched.append(MovieCard(
            title=r["title"],
            score=r["score"],
            score_pct=r["score_pct"],
            genres=r["genres"],
            cast=r["cast"],
            director=r["director"],
            vote_average=r["vote_average"],
            overview=r["overview"],
            explanation=r["explanation"],
            poster=omdb_data.get("poster", "N/A"),
            imdb_rating=omdb_data.get("imdb_rating", "N/A"),
        ))

    return RecommendResponse(
        results=enriched,
        total=len(enriched),
        query_info={
            "movies":    request.movies,
            "actors":    request.actors,
            "directors": request.directors,
            "genres":    request.genres,
        }
    )


@app.get("/search")
def search(
    q:     str = Query(..., min_length=1, description="Search query"),
    top_n: int = Query(default=10, ge=1, le=50),
):
    """Search movies by title."""
    df = ml_model["df"]

    results = search_movies(query=q, df=df, top_n=top_n)

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No movies found matching '{q}'"
        )

    return {
        "query":   q,
        "total":   len(results),
        "results": results,
    }


@app.get("/movie/{title}")
def get_movie(title: str):
    """Get details of a single movie by title."""
    df = ml_model["df"]

    matches = df[df["title"].str.lower() == title.strip().lower()]

    if matches.empty:
        matches = df[df["title"].str.lower().str.contains(title.strip().lower())]

    if matches.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Movie '{title}' not found"
        )

    row      = matches.iloc[0]
    omdb     = fetch_movie_omdb(row["title"])

    return {
        "title":        row["title"],
        "overview":     row["overview"],
        "genres":       row["genres_list"],
        "cast":         row["cast_list"],
        "director":     row["director_list"],
        "vote_average": row["vote_average"],
        "vote_count":   row["vote_count"],
        "poster":       omdb.get("poster", "N/A"),
        "imdb_rating":  omdb.get("imdb_rating", "N/A"),
        "runtime":      omdb.get("runtime", "N/A"),
        "awards":       omdb.get("awards", "N/A"),
        "box_office":   omdb.get("box_office", "N/A"),
    }


@app.get("/genres")
def get_genres():
    """Get all unique genres in the dataset."""
    df = ml_model["df"]
    all_genres = set()
    for genres in df["genres_list"]:
        all_genres.update(genres)
    return {"genres": sorted(list(all_genres))}


@app.get("/movies/popular")
def get_popular(top_n: int = Query(default=20, ge=1, le=100)):
    """Get top popular movies by weighted rating."""
    df = ml_model["df"]

    v = df["vote_count"]
    R = df["vote_average"]
    C = R.mean()
    m = v.quantile(0.25)

    df = df.copy()
    df["weighted_rating"] = (v / (v + m)) * R + (m / (v + m)) * C
    top = df.nlargest(top_n, "weighted_rating")

    results = []
    for _, row in top.iterrows():
        results.append({
            "title":           row["title"],
            "vote_average":    row["vote_average"],
            "weighted_rating": round(row["weighted_rating"], 2),
            "genres":          row["genres_list"],
            "director":        row["director_list"],
        })

    return {"total": len(results), "results": results}