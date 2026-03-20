import SkeletonCard from "./SkeletonCard";

export default function SkeletonGrid({ count = 10 }) {
  return (
    <div className="mt-8">
      <div className="h-6 bg-gray-700 rounded w-48 mb-4 animate-pulse" />
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4
                      lg:grid-cols-5 gap-4">
        {Array.from({ length: count }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    </div>
  );
}