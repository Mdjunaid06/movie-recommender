import { FaFilm } from "react-icons/fa";

export default function EmptyState({ message }) {
  return (
    <div className="flex flex-col items-center justify-center
                    py-20 text-center">
      <FaFilm className="text-gray-700 text-6xl mb-4" />
      <h3 className="text-gray-400 text-lg font-semibold mb-2">
        No Results Found
      </h3>
      <p className="text-gray-600 text-sm max-w-md">
        {message || "Try searching for a different movie, actor, or genre."}
      </p>
    </div>
  );
}