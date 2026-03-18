from app.recommender import load_model, recommend_weighted, search_movies


def main():
    print("📂 Loading saved model...")
    df, similarity_matrix = load_model()
    print("✅ Model loaded!\n")

    print("=" * 55)
    print("TEST 1: Single movie input")
    print("=" * 55)
    results = recommend_weighted(
        df=df,
        similarity_matrix=similarity_matrix,
        movies=["Inception"],
        top_n=5,
    )
    print(f"\n🎬 Recommendations for 'Inception':")
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['title']:<40} Score: {r['score_pct']}  ⭐ {r['vote_average']}")
    print(f"\n💡 {results[0]['explanation']}\n")

    print("=" * 55)
    print("TEST 2: Multiple movies + actor")
    print("=" * 55)
    results2 = recommend_weighted(
        df=df,
        similarity_matrix=similarity_matrix,
        movies=["Inception", "Interstellar"],
        actors=["Leonardo DiCaprio"],
        top_n=5,
    )
    print(f"\n🎬 Recommendations for Inception + Interstellar + DiCaprio:")
    for i, r in enumerate(results2, 1):
        print(f"  {i}. {r['title']:<40} Score: {r['score_pct']}  ⭐ {r['vote_average']}")
    print(f"\n💡 {results2[0]['explanation']}\n")

    print("=" * 55)
    print("TEST 3: Director + Genre only")
    print("=" * 55)
    results3 = recommend_weighted(
        df=df,
        similarity_matrix=similarity_matrix,
        directors=["Christopher Nolan"],
        genres=["Action", "Thriller"],
        top_n=5,
    )
    print(f"\n🎬 Recommendations for Nolan + Action/Thriller:")
    for i, r in enumerate(results3, 1):
        print(f"  {i}. {r['title']:<40} Score: {r['score_pct']}  ⭐ {r['vote_average']}")
    print(f"\n💡 {results3[0]['explanation']}\n")

    print("✅ Phase 4 complete!")


if __name__ == "__main__":
    main()