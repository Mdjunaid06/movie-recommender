export default function QuerySummary({ queryInfo, total }) {
  if (!queryInfo) return null;

  const parts = [];
  if (queryInfo.movies?.length > 0)
    parts.push(`🎬 ${queryInfo.movies.join(", ")}`);
  if (queryInfo.actors?.length > 0)
    parts.push(`🎭 ${queryInfo.actors.join(", ")}`);
  if (queryInfo.directors?.length > 0)
    parts.push(`🎥 ${queryInfo.directors.join(", ")}`);
  if (queryInfo.genres?.length > 0)
    parts.push(`🎞️ ${queryInfo.genres.join(", ")}`);

  if (parts.length === 0) return null;

  return (
    <div className="max-w-3xl mx-auto mt-4 bg-gray-800/50 border
                    border-gray-700 rounded-xl px-4 py-3">
      <div className="flex flex-wrap items-center gap-2 text-sm">
        <span className="text-gray-400">Showing</span>
        <span className="text-primary font-semibold">{total} results</span>
        <span className="text-gray-400">for:</span>
        {parts.map((p, i) => (
          <span key={i} className="bg-gray-700 text-white
                                   px-3 py-1 rounded-full text-xs">
            {p}
          </span>
        ))}
      </div>
    </div>
  );
}