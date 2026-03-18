from app.recommender import build_model, recommend, search_movies


def main():
    # Build and save model
    df, similarity_matrix = build_model()

    print("\n" + "="*50)
    print(" Testing recommend() function...")
    print("="*50)

    # Test 1: Single movie recommendation
    results = recommend("Avatar", df, similarity_matrix, top_n=5)
    print(f"\n🎬 Movies similar to 'Avatar':")
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['title']:<40} Score: {r['score_pct']}  ⭐ {r['vote_average']}")

    print("\n" + "="*50)

    # Test 2: Another movie
    results2 = recommend("The Dark Knight", df, similarity_matrix, top_n=5)
    print(f"\n🎬 Movies similar to 'The Dark Knight':")
    for i, r in enumerate(results2, 1):
        print(f"  {i}. {r['title']:<40} Score: {r['score_pct']}  ⭐ {r['vote_average']}")

    print("\n" + "="*50)

    # Test 3: Search
    print(f"\n🔍 Search results for 'dark':")
    search_results = search_movies("dark", df, top_n=5)
    for r in search_results:
        print(f"  - {r['title']}")

    print("\n✅ Phase 3 complete!")


if __name__ == "__main__":
    main()