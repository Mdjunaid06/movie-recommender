import { FaFilm } from "react-icons/fa";

export default function Navbar() {
  return (
    <nav className="bg-dark border-b border-gray-800 px-6 py-4 flex items-center gap-3 sticky top-0 z-50">
      <FaFilm className="text-primary text-2xl" />
      <h1 className="text-xl font-bold text-white tracking-wide">
        Movie<span className="text-primary">Rec</span>
      </h1>
    </nav>
  );
}