import { useState, useEffect } from "react";
import { FaSearch } from "react-icons/fa";
import AutocompleteInput from "./AutocompleteInput";
import { searchMovies, suggestActors, suggestDirectors } from "../api";

// ─────────────────────────────────────────
// Autocomplete hook — defined outside component
// ─────────────────────────────────────────
function useSuggestions(query, fetchFn) {
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    if (query.trim().length < 2) { setSuggestions([]); return; }
    const timer = setTimeout(async () => {
      try {
        const data = await fetchFn(query);
        setSuggestions(
          data.results?.map((r) => r.title) ||
          data.suggestions || []
        );
      } catch { setSuggestions([]); }
    }, 300);
    return () => clearTimeout(timer);
  }, [query]); // eslint-disable-line react-hooks/exhaustive-deps

  return suggestions;
}

const GENRES = [
  "Action","Adventure","Animation","Comedy","Crime",
  "Documentary","Drama","Family","Fantasy","Horror",
  "Mystery","Romance","Science Fiction","Thriller","War",
];

export default function SearchBar({ onRecommend, loading }) {
  const [movieInput,    setMovieInput]    = useState("");
  const [movies,        setMovies]        = useState([]);
  const [actorInput,    setActorInput]    = useState("");
  const [actors,        setActors]        = useState([]);
  const [directorInput, setDirectorInput] = useState("");
  const [directors,     setDirectors]     = useState([]);
  const [genre,         setGenre]         = useState("");
  const [showAdvanced,  setShowAdvanced]  = useState(false);

  // Autocomplete suggestions
  const movieSuggestions    = useSuggestions(movieInput,    searchMovies);
  const actorSuggestions    = useSuggestions(actorInput,    suggestActors);
  const directorSuggestions = useSuggestions(directorInput, suggestDirectors);

  const addItem = (value, list, setList, setInput) => {
    const trimmed = value.trim();
    if (trimmed && !list.includes(trimmed)) setList((p) => [...p, trimmed]);
    setInput("");
  };

  const removeItem = (item, setList) =>
    setList((p) => p.filter((i) => i !== item));

  const handleSubmit = () => {
    const finalMovies = [...movies];
    if (movieInput.trim() && !finalMovies.includes(movieInput.trim()))
      finalMovies.push(movieInput.trim());

    const finalActors = [...actors];
    if (actorInput.trim() && !finalActors.includes(actorInput.trim()))
      finalActors.push(actorInput.trim());

    const finalDirectors = [...directors];
    if (directorInput.trim() && !finalDirectors.includes(directorInput.trim()))
      finalDirectors.push(directorInput.trim());

    onRecommend({
      movies:    finalMovies,
      actors:    finalActors,
      directors: finalDirectors,
      genres:    genre ? [genre] : [],
      top_n:     10,
    });
  };

  const hasInput =
    movies.length > 0    || movieInput.trim() !== "" ||
    actors.length > 0    || actorInput.trim() !== "" ||
    directors.length > 0 || directorInput.trim() !== "" ||
    genre !== "";

  return (
    <div className="bg-card rounded-2xl p-4 md:p-6 shadow-lg border
                    border-gray-800 max-w-3xl mx-auto">

      {/* Movie Input */}
      <div className="mb-4">
        <label className="text-gray-300 text-sm font-medium mb-2 block">
          🎬 Movies you liked
        </label>
        <AutocompleteInput
          value={movieInput}
          onChange={setMovieInput}
          onAdd={(v) => addItem(v, movies, setMovies, setMovieInput)}
          placeholder="e.g. Inception, The Dark Knight..."
          suggestions={movieSuggestions}
          tags={movies}
          onRemoveTag={(t) => removeItem(t, setMovies)}
        />
      </div>

      {/* Genre */}
      <div className="mb-4">
        <label className="text-gray-300 text-sm font-medium mb-2 block">
          🎞️ Genre{" "}
          <span className="text-gray-500 font-normal">(optional)</span>
        </label>
        <select
          value={genre}
          onChange={(e) => setGenre(e.target.value)}
          className="w-full bg-gray-800 text-white rounded-lg px-4 py-2.5
                     border border-gray-700 focus:border-primary
                     focus:outline-none text-sm"
        >
          <option value="">Any genre</option>
          {GENRES.map((g) => (
            <option key={g} value={g}>{g}</option>
          ))}
        </select>
      </div>

      {/* Advanced toggle */}
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="text-gray-400 hover:text-primary text-xs mb-4 transition"
      >
        {showAdvanced ? "▲ Hide filters" : "▼ Add actor / director (optional)"}
      </button>

      {/* Advanced filters */}
      {showAdvanced && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="text-gray-300 text-sm font-medium mb-2 block">
              🎭 Actor
            </label>
            <AutocompleteInput
              value={actorInput}
              onChange={setActorInput}
              onAdd={(v) => addItem(v, actors, setActors, setActorInput)}
              placeholder="e.g. Leonardo DiCaprio"
              suggestions={actorSuggestions}
              tags={actors}
              onRemoveTag={(t) => removeItem(t, setActors)}
            />
          </div>
          <div>
            <label className="text-gray-300 text-sm font-medium mb-2 block">
              🎥 Director
            </label>
            <AutocompleteInput
              value={directorInput}
              onChange={setDirectorInput}
              onAdd={(v) => addItem(v, directors, setDirectors, setDirectorInput)}
              placeholder="e.g. Christopher Nolan"
              suggestions={directorSuggestions}
              tags={directors}
              onRemoveTag={(t) => removeItem(t, setDirectors)}
            />
          </div>
        </div>
      )}

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={!hasInput || loading}
        className="w-full bg-primary hover:bg-red-700 disabled:bg-gray-700
                   disabled:cursor-not-allowed text-white font-semibold
                   py-3 rounded-xl transition flex items-center
                   justify-center gap-2 text-sm mt-2"
      >
        {loading ? (
          <>
            <div className="w-4 h-4 border-2 border-white
                            border-t-transparent rounded-full animate-spin" />
            Finding movies...
          </>
        ) : (
          <><FaSearch size={12} /> Get Recommendations</>
        )}
      </button>
    </div>
  );
}