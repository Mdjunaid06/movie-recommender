from app.recommender import load_model, recommend_weighted
from app.omdb_client import enrich_dataset, save_enriched


def main():
    print("📂 Loading saved model...")
    df, similarity_matrix = load_model()
    print("✅ Model loaded!\n")

    # Enrich first 100 movies with OMDB data
    print("🌐 Fetching OMDB data...")
    df_enriched = enrich_dataset(df, limit=100)
    save_enriched(df_enriched)

    # Show sample enriched data
    print("\n📋 Sample enriched movies:")
    sample = df_enriched[["title", "poster", "imdb_rating", "runtime"]].head(5)
    for _, row in sample.iterrows():
        print(f"  🎬 {row['title']:<40} ⭐ {row['imdb_rating']}  🕐 {row['runtime']}")
        print(f"     🖼️  {row['poster'][:60]}...")

    print("\n✅ OMDB integration complete!")


if __name__ == "__main__":
    main()