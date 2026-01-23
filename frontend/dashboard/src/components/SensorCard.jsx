function SensorCard({ label, value, status }) {
  const statusClass =
    {
      optimal: "border-emerald-500/30 bg-emerald-500/10 text-emerald-200",
      moderate: "border-amber-500/30 bg-amber-500/10 text-amber-200",
      bad: "border-red-500/30 bg-red-500/10 text-red-200",
      dry: "border-amber-500/30 bg-amber-500/10 text-amber-200",
      unknown: "border-white/10 bg-white/5 text-white/70",
    }[status] ?? "border-white/10 bg-white/5 text-white/70";

  function formatSensorValue(value) {
    if (!value || value.startsWith("--")) return "—";
    return value.endsWith("C") ? `${value.slice(0, -1)}°C` : value;
  }

  return (
    <div className="rounded-2xl border-t border-white/20 bg-white/5 p-4 shadow-xl">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-sm text-white/60">{label}</div>
          <div className="mt-1 text-2xl font-semibold text-white">
            {formatSensorValue(value)}
          </div>
        </div>

        {status && (
          <span
            className={`rounded-full border px-2.5 py-1 text-xs capitalize ${statusClass}`}
          >
            {status}
          </span>
        )}
      </div>
    </div>
  );
}

export default SensorCard;