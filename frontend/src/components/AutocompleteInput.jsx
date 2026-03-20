import { useState, useRef, useEffect } from "react";
import { FaPlus, FaTimes } from "react-icons/fa";

export default function AutocompleteInput({
  value,
  onChange,
  onAdd,
  placeholder,
  suggestions = [],
  tags = [],
  onRemoveTag,
}) {
  const [showDropdown, setShowDropdown] = useState(false);
  const wrapperRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handler = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleSelect = (item) => {
    onAdd(item);
    setShowDropdown(false);
  };

  return (
    <div ref={wrapperRef} className="relative">
      <div className="flex gap-2">
        <input
          type="text"
          value={value}
          onChange={(e) => {
            onChange(e.target.value);
            setShowDropdown(true);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              onAdd(value);
              setShowDropdown(false);
            }
            if (e.key === "Escape") setShowDropdown(false);
          }}
          onFocus={() => value.length >= 2 && setShowDropdown(true)}
          placeholder={placeholder}
          className="flex-1 bg-gray-800 text-white rounded-lg px-4 py-2.5
                     border border-gray-700 focus:border-primary
                     focus:outline-none text-sm placeholder-gray-500"
        />
        <button
          onClick={() => { onAdd(value); setShowDropdown(false); }}
          className="bg-primary hover:bg-red-700 text-white px-3
                     rounded-lg transition"
        >
          <FaPlus size={12} />
        </button>
      </div>

      {/* Dropdown */}
      {showDropdown && suggestions.length > 0 && (
        <ul className="absolute z-50 w-full mt-1 bg-gray-800 border
                       border-gray-700 rounded-lg shadow-xl max-h-48
                       overflow-y-auto">
          {suggestions.map((s) => (
            <li
              key={s}
              onMouseDown={() => handleSelect(s)}
              className="px-4 py-2.5 text-sm text-white hover:bg-gray-700
                         cursor-pointer border-b border-gray-700
                         last:border-0 transition"
            >
              {s}
            </li>
          ))}
        </ul>
      )}

      {/* Tags */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          {tags.map((tag) => (
            <span key={tag}
              className="bg-gray-700 text-white text-xs px-3 py-1
                         rounded-full flex items-center gap-1">
              {tag}
              <FaTimes
                className="cursor-pointer hover:text-primary ml-1"
                onClick={() => onRemoveTag(tag)}
              />
            </span>
          ))}
        </div>
      )}
    </div>
  );
}