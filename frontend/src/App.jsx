import { useState, useEffect, useRef } from "react";
import Navbar from "./components/Navbar";
import SearchBar from "./components/SearchBar";
import MovieGrid from "./components/MovieGrid";
import SkeletonGrid from "./components/SkeletonGrid";
import EmptyState from "./components/EmptyState";
import ErrorMessage from "./components/ErrorMessage";
import QuerySummary from "./components/QuerySummary";
import { getRecommendations, getPopularMovies } from "./api";

export default function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [popularMovies,   setPopularMovies]   = useState([]);
  const [popularLoading,  setPopularLoading]  = useState(true);
  const [loading,         setLoading]         = useState(false);
  const [error,           setError]           = useState("");
  const [hasSearched,     setHasSearched]     = useState(false);
  const [queryInfo,       setQueryInfo]       = useState(null);
  const resultsRef = useRef(null);

  useEffect(() => {
    const fetchPopular = async () => {
      try {
        setPopularLoading(true);
        const data = await getPopularMovies(20);
        setPopularMovies(data.results || []);
      } catch (err) {
        console.error("Failed to load popular movies:", err);
      } finally {
        setPopularLoading(false);
      }
    };
    fetchPopular();
  }, []);

  const handleRecommend = async (payload) => {
    setLoading(true);
    setError("");
    setRecommendations([]);
    setQueryInfo(null);

    try {
      const data = await getRecommendations(payload);
      setRecommendations(data.results || []);
      setQueryInfo(data.query_info);
      setHasSearched(true);

      setTimeout(() => {
        resultsRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }, 100);

    } catch (err) {
      const status = err.response?.status;
      const detail = err.response?.data?.detail;
      setHasSearched(true);

      if (status === 404) {
        setError(detail || "No results found. Try different movies or genres.");
      } else if (status === 400) {
        setError("Please enter at least one movie or select a genre.");
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark">
      <Navbar />

      <main className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 py-6 md:py-10">

        {/* Hero */}
        <div className="text-center mb-6 md:mb-10">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold
                         text-white mb-3">
            Find Your Next{" "}
            <span className="text-primary">Favorite Movie</span>
          </h2>
        </div>

        {/* Search */}
        <SearchBar onRecommend={handleRecommend} loading={loading} />

        {/* Query Summary */}
        {hasSearched && !loading && queryInfo && (
          <QuerySummary queryInfo={queryInfo} total={recommendations.length} />
        )}

        {/* Error */}
        <ErrorMessage message={error} />

        {/* Results section */}
        <div ref={resultsRef}>

          {/* Loading skeletons */}
          {loading && <SkeletonGrid count={10} />}

          {/* Recommendations */}
          {!loading && hasSearched && recommendations.length > 0 && (
            <MovieGrid
              movies={recommendations}
              title={`Recommendations (${recommendations.length})`}
            />
          )}

          {/* Empty state */}
          {!loading && hasSearched && recommendations.length === 0 && !error && (
            <EmptyState message="No recommendations found. Try different inputs." />
          )}

        </div>

        {/* Popular Movies */}
        {!hasSearched && (
          <>
            {popularLoading
              ? <SkeletonGrid count={10} />
              : <MovieGrid movies={popularMovies} title="Popular Movies" />
            }
          </>
        )}

      </main>
    </div>
  );
}