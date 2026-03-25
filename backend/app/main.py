from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.recommender import load_model, recommend_weighted, search_movies
from app.omdb_client import fetch_movie_omdb

# ─────────────────────────────────────────
# LIFESPAN
# ─────────────────────────────────────────

ml_model = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
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
    description="Hybrid movie recommendation system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────

class RecommendRequest(BaseModel):
    movies:    list[str] = Field(default=[])
    actors:    list[str] = Field(default=[])
    directors: list[str] = Field(default=[])
    genres:    list[str] = Field(default=[])
    top_n:     int       = Field(default=10, ge=1, le=50)

class MovieCard(BaseModel):
    title:        str
    score:        float = 0.0
    score_pct:    str = ""
    genres:       list[str]
    cast:         list[str]
    director:     list[str]
    vote_average: float
    overview:     str
    explanation:  str = ""
    poster:       str = "N/A"
    imdb_rating:  str = "N/A"

class RecommendResponse(BaseModel):
    results:    list[MovieCard]
    total:      int
    query_info: dict


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
        "status":       "healthy",
        "model_loaded": "df" in ml_model,
        "total_movies": len(ml_model["df"]) if "df" in ml_model else 0,
    }


@app.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest):
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
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No recommendations found. Try different inputs."
        )

    enriched = []
    for r in results:
        omdb = fetch_movie_omdb(r["title"])
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
            poster=omdb.get("poster", "N/A"),
            imdb_rating=omdb.get("imdb_rating", "N/A"),
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
    q:     str = Query(..., min_length=1),
    top_n: int = Query(default=10, ge=1, le=50),
):
    df = ml_model["df"]
    results = search_movies(query=q, df=df, top_n=top_n)

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No movies found matching '{q}'"
        )

    return {"query": q, "total": len(results), "results": results}


@app.get("/movie/{title}")
def get_movie(title: str):
    df = ml_model["df"]

    matches = df[df["title"].str.lower() == title.strip().lower()]
    if matches.empty:
        matches = df[df["title"].str.lower().str.contains(title.strip().lower())]
    if matches.empty:
        raise HTTPException(status_code=404, detail=f"Movie '{title}' not found")

    row  = matches.iloc[0]
    omdb = fetch_movie_omdb(row["title"])

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
    df = ml_model["df"]
    all_genres = set()
    for genres in df["genres_list"]:
        all_genres.update(genres)
    return {"genres": sorted(list(all_genres))}


@app.get("/movies/popular")
def get_popular(top_n: int = Query(default=20, ge=1, le=100)):
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
        omdb = fetch_movie_omdb(row["title"])
        results.append({
            "title":           row["title"],
            "vote_average":    row["vote_average"],
            "weighted_rating": round(row["weighted_rating"], 2),
            "genres":          row["genres_list"],
            "cast":            row["cast_list"],
            "director":        row["director_list"],
            "overview":        row["overview"][:200] + "...",
            "poster":          omdb.get("poster", "N/A"),
            "imdb_rating":     omdb.get("imdb_rating", "N/A"),
        })

    return {"total": len(results), "results": results}


@app.get("/suggest/actors")
def suggest_actors(q: str = Query(..., min_length=1)):
    df = ml_model["df"]
    q_lower = q.strip().lower()

    starts_with = set()
    contains    = set()

    for cast_list in df["cast_list"]:
        for actor in cast_list:
            actor_lower = actor.lower()
            if actor_lower.startswith(q_lower):
                starts_with.add(actor)
            elif q_lower in actor_lower:
                contains.add(actor)

    # Names starting with query come first
    results = sorted(starts_with)[:8] + sorted(contains)[:4]
    return {"suggestions": results[:10]}


@app.get("/suggest/directors")
def suggest_directors(q: str = Query(..., min_length=1)):
    df = ml_model["df"]
    q_lower = q.strip().lower()

    starts_with = set()
    contains    = set()

    for director_list in df["director_list"]:
        for director in director_list:
            director_lower = director.lower()
            if director_lower.startswith(q_lower):
                starts_with.add(director)
            elif q_lower in director_lower:
                contains.add(director)

    results = sorted(starts_with)[:8] + sorted(contains)[:4]
    return {"suggestions": results[:10]}

@app.get("/ping")
def ping():
    return "ok"