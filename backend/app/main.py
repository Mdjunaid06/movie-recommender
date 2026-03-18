from app.utils import (
    load_raw_data,
    merge_datasets,
    basic_clean,
    build_tags,
    select_final_columns,
    inspect_data,
)


def build_dataset() -> object:
    """Full preprocessing pipeline. Returns clean dataframe."""
    print("📦 Loading raw data...")
    movies_df, credits_df = load_raw_data()

    print("🔗 Merging datasets...")
    df = merge_datasets(movies_df, credits_df)

    print("🧹 Basic cleaning...")
    df = basic_clean(df)

    print("🏗️  Engineering features + building tags...")
    df = build_tags(df)
    df = select_final_columns(df)

    inspect_data(df)
    print("\n✅ Phase 2 complete. Data is ready for ML.")
    return df


if __name__ == "__main__":
    build_dataset()