import MovieCard from "./MovieCard";

export default function MovieGrid({ movies, title }) {
  if (!movies || movies.length === 0) return null;

  return (
    <div className="mt-8">
      {title && (
        <h2 className="text-white text-xl font-bold mb-4">
          {title}
        </h2>
      )}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4
                      lg:grid-cols-5 gap-4">
        {movies.map((movie, i) => (
          <MovieCard key={`${movie.title}-${i}`} movie={movie} />
        ))}
      </div>
    </div>
  );
}