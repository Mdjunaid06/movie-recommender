from app.recommender import load_model, recommend_weighted
from app.omdb_client import enrich_dataset, save_enriched, load_enriched


def main():
    print("📂 Loading saved model...")
    df, similarity_matrix = load_model()
    print("✅ Model loaded!\n")

    print("=" * 55)
    print("TEST 1: Popularity boost comparison")
    print("=" * 55)

    # Without popularity — raw similarity
    print("\n🎬 Top 5 for 'Inception' (with popularity boost):")
    results = recommend_weighted(
        df=df,
        similarity_matrix=similarity_matrix,
        movies=["Inception"],
        top_n=5,
    )
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['title']:<40} Score: {r['score_pct']}  ⭐ {r['vote_average']}")

    print("\n" + "=" * 55)
    print("TEST 2: Multi-input with popularity boost")
    print("=" * 55)

    results2 = recommend_weighted(
        df=df,
        similarity_matrix=similarity_matrix,
        movies=["The Dark Knight", "Inception"],
        actors=["Christian Bale"],
        genres=["Action", "Thriller"],
        top_n=5,
    )
    print(f"\n🎬 Dark Knight + Inception + Bale + Action/Thriller:")
    for i, r in enumerate(results2, 1):
        print(f"  {i}. {r['title']:<40} Score: {r['score_pct']}  ⭐ {r['vote_average']}")
    print(f"\n💡 {results2[0]['explanation']}")

    print("\n✅ Phase 5 complete!")


if __name__ == "__main__":
    main()