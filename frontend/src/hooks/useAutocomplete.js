import { useState, useEffect } from "react";
import { searchMovies } from "../api";

export function useMovieAutocomplete(query) {
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    if (query.trim().length < 2) {
      setSuggestions([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const data = await searchMovies(query);
        setSuggestions(data.results?.map((r) => r.title) || []);
      } catch {
        setSuggestions([]);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  return suggestions;
}