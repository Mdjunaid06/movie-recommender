export default function SkeletonCard() {
  return (
    <div className="bg-card rounded-xl overflow-hidden border
                    border-gray-800 flex flex-col animate-pulse">
      {/* Poster placeholder */}
      <div className="w-full h-64 bg-gray-700" />

      {/* Content placeholder */}
      <div className="p-4 flex flex-col gap-3">
        {/* Title */}
        <div className="h-4 bg-gray-700 rounded w-3/4" />
        {/* Rating */}
        <div className="h-3 bg-gray-700 rounded w-1/4" />
        {/* Genres */}
        <div className="flex gap-2">
          <div className="h-3 bg-gray-700 rounded w-16" />
          <div className="h-3 bg-gray-700 rounded w-16" />
        </div>
        {/* Director */}
        <div className="h-3 bg-gray-700 rounded w-1/2" />
        {/* Overview lines */}
        <div className="h-3 bg-gray-700 rounded w-full" />
        <div className="h-3 bg-gray-700 rounded w-5/6" />
        <div className="h-3 bg-gray-700 rounded w-4/6" />
      </div>
    </div>
  );
}