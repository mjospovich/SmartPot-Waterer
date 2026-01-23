import { useEffect, useState } from "react";

const QUICK_SELECT = [5, 10, 20];

function WateringPanel({ onWater }) {
  const [duration, setDuration] = useState(5);
  const [feedback, setFeedback] = useState("");
  const [remaining, setRemaining] = useState(0);

  const isWatering = remaining > 0;

  const progress = isWatering
    ? Math.round(((duration - remaining) / duration) * 100)
    : 0;

  function showFeedback(message, timeout = 5000) {
    setFeedback(message);
    setTimeout(() => setFeedback(""), timeout);
  }

  async function startWatering() {
    setFeedback("");
    setRemaining(duration);

    try {
      const result = await onWater(duration);
      const message =
        typeof result === "string"
          ? result
          : result?.message || "Watering started";

      showFeedback(message);
    } catch (e) {
      showFeedback(e?.message || "Watering failed", 5000);
      setRemaining(0);
    }
  }

  useEffect(() => {
    if (!isWatering) return;

    const id = setInterval(() => {
      setRemaining((r) => Math.max(0, r - 1));
    }, 1000);

    return () => clearInterval(id);
  }, [isWatering]);

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 h-full shadow-xl">
      <div className="text-xl font-semibold text-white">💧 Water the plant</div>

      <div className="mt-4 flex gap-2">
        {QUICK_SELECT.map((seconds) => (
          <button
            key={seconds}
            disabled={isWatering}
            onClick={() => setDuration(seconds)}
            className={`rounded-xl border px-3 py-1.5 text-sm transition ${
              duration === seconds
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-200"
                : "border-white/10 bg-white/5 text-white/70 hover:bg-white/10"
            }`}
          >
            {seconds}s
          </button>
        ))}
      </div>

      <div className="mt-4">
        <div className="mb-2 flex justify-between text-xs text-white/60">
          <span>Duration</span>
          <span className="font-mono">{duration}s</span>
        </div>
        <input
          type="range"
          min="1"
          max="30"
          value={duration}
          onChange={(e) => setDuration(Number(e.target.value))}
          disabled={isWatering}
          className="w-full"
        />
      </div>

      <div className="mt-3">
        <div className="mb-2 flex justify-between text-xs text-white/60">
          <span>Status</span>
          <span className="font-mono">
            {isWatering ? `${remaining}s remaining` : ""}
          </span>
        </div>
        <div className="h-2 w-full rounded-full bg-white/10">
          <div
            className="h-2 rounded-full bg-emerald-500/60 transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <button
        onClick={startWatering}
        disabled={isWatering}
        className="mt-4 w-full rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-2.5 text-sm font-semibold text-emerald-100 hover:bg-emerald-500/15 disabled:opacity-60"
      >
        {isWatering ? "Watering in progress…" : "💧 Water now"}
      </button>

      {feedback && (
        <div className="mt-3 p-2 text-sm text-white/80">{feedback}</div>
      )}
    </div>
  );
}

export default WateringPanel;