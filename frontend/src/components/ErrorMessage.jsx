export default function ErrorMessage({ message }) {
  if (!message) return null;
  return (
    <div className="bg-red-900/20 border border-red-800 text-red-400
                    rounded-xl p-4 mt-4 text-sm max-w-3xl mx-auto">
      ⚠️ {message}
    </div>
  );
}