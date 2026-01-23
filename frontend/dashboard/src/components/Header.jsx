function Header({ lastUpdated, onRefresh }) {
  return (
    <header className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between pb-3 border-b border-white/10">
      <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
        🌿SmartPot Dashboard
      </h1>

      <div className="flex items-center gap-3">
        <div className="rounded-xl border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/70">
          Last update:{" "}
          <span className="font-mono">
            {lastUpdated ? lastUpdated.toLocaleTimeString() : "—"}
          </span>
        </div>

        <button
          onClick={onRefresh}
          className="rounded-xl border border-white/10 bg-white/20 px-3 py-1 text-sm text-white/80 hover:bg-white/30 transition"
        >
          Refresh
        </button>
      </div>
    </header>
  );
}
export default Header;