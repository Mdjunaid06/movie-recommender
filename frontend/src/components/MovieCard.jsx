import { FaStar, FaUser, FaFilm, FaClock, FaTrophy } from "react-icons/fa";

const FALLBACK = "https://placehold.co/300x450/1f1f1f/E50914?text=No+Poster";

export default function MovieCard({ movie }) {
  const poster = movie.poster && movie.poster !== "N/A"
    ? movie.poster : FALLBACK;

  return (
    <div className="bg-card rounded-xl overflow-hidden border border-gray-800
                    hover:border-primary transition-all duration-300
                    hover:shadow-xl hover:shadow-red-900/20 hover:-translate-y-1
                    flex flex-col group">

      {/* Poster */}
      <div className="relative overflow-hidden">
        <img
          src={poster}
          alt={movie.title}
          className="w-full h-64 object-cover group-hover:scale-105
                     transition-transform duration-500"
          onError={(e) => { e.target.src = FALLBACK; }}
        />

        {/* Score badge — only for recommendations */}
        {movie.score_pct && (
          <div className="absolute top-2 right-2 bg-primary text-white
                          text-xs font-bold px-2 py-1 rounded-full
                          shadow-lg">
            {movie.score_pct}
          </div>
        )}

        {/* IMDb badge */}
        {movie.imdb_rating && movie.imdb_rating !== "N/A" && (
          <div className="absolute top-2 left-2 bg-yellow-500 text-black
                          text-xs font-bold px-2 py-1 rounded-full
                          flex items-center gap-1 shadow-lg">
            <FaStar className="text-xs" />
            {movie.imdb_rating}
          </div>
        )}

        {/* Dark gradient overlay */}
        <div className="absolute bottom-0 left-0 right-0 h-16
                        bg-gradient-to-t from-card to-transparent" />
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col flex-1">

        {/* Title */}
        <h3 className="text-white font-bold text-sm mb-2 line-clamp-2
                       leading-tight">
          {movie.title}
        </h3>

        {/* Ratings row */}
        <div className="flex items-center gap-3 mb-2">
          <div className="flex items-center gap-1">
            <FaStar className="text-yellow-400 text-xs" />
            <span className="text-yellow-400 text-xs font-semibold">
              {movie.vote_average?.toFixed(1)}
            </span>
            <span className="text-gray-600 text-xs">/10</span>
          </div>
          {movie.runtime && movie.runtime !== "N/A" && (
            <div className="flex items-center gap-1">
              <FaClock className="text-gray-600 text-xs" />
              <span className="text-gray-500 text-xs">{movie.runtime}</span>
            </div>
          )}
        </div>

        {/* Genres */}
        <div className="flex flex-wrap gap-1 mb-2">
          {movie.genres?.slice(0, 2).map((g) => (
            <span key={g}
              className="bg-gray-800 text-gray-300 text-xs
                         px-2 py-0.5 rounded-full border border-gray-700">
              {g}
            </span>
          ))}
        </div>

        {/* Director */}
        {movie.director?.length > 0 && (
          <div className="flex items-center gap-1.5 mb-1">
            <FaFilm className="text-gray-600 text-xs flex-shrink-0" />
            <span className="text-gray-400 text-xs truncate">
              {movie.director[0]}
            </span>
          </div>
        )}

        {/* Cast */}
        {movie.cast?.length > 0 && (
          <div className="flex items-center gap-1.5 mb-2">
            <FaUser className="text-gray-600 text-xs flex-shrink-0" />
            <span className="text-gray-400 text-xs truncate">
              {movie.cast?.slice(0, 2).join(", ")}
            </span>
          </div>
        )}

        {/* Awards */}
        {movie.awards && movie.awards !== "N/A" &&
         movie.awards.toLowerCase().includes("oscar") && (
          <div className="flex items-center gap-1.5 mb-2">
            <FaTrophy className="text-yellow-500 text-xs flex-shrink-0" />
            <span className="text-yellow-500 text-xs truncate">
              {movie.awards.split(".")[0]}
            </span>
          </div>
        )}

        {/* Overview */}
        <p className="text-gray-500 text-xs line-clamp-3 flex-1
                      leading-relaxed mt-1">
          {movie.overview}
        </p>

        {/* Explanation */}
        {movie.explanation && (
          <div className="mt-3 pt-3 border-t border-gray-800">
            <p className="text-primary text-xs italic line-clamp-2">
              💡 {movie.explanation}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}