export default function FilterPanel({ filters, setFilters, meta }) {
  const update = (patch) => setFilters((f) => ({ ...f, ...patch }));

  return (
    <section>
      <h2 className="kicker border-b border-rule pb-2 mb-4">Refine</h2>

      <div className="flex flex-col gap-6">
        <label className="block">
          <span className="kicker">Search</span>
          <input
            type="text"
            value={filters.q}
            onChange={(e) => update({ q: e.target.value })}
            placeholder="title or company…"
            className="mt-2 w-full bg-transparent border-b border-rule pb-1 font-display text-lg text-ink placeholder:text-ink-faint placeholder:font-sans placeholder:text-base focus:outline-none focus:border-accent transition-colors"
          />
        </label>

        <label className="block">
          <div className="flex items-center justify-between">
            <span className="kicker">Minimum fit</span>
            <span className="font-mono text-sm text-accent tabular-nums">
              {filters.min_score}
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            step="5"
            value={filters.min_score}
            onChange={(e) => update({ min_score: Number(e.target.value) })}
            className="mt-3"
          />
        </label>

        <label className="block">
          <span className="kicker">Role search</span>
          <select
            value={filters.role}
            onChange={(e) => update({ role: e.target.value })}
            className="mt-2 w-full rounded-lg bg-paper-2 border border-rule px-3 py-2 font-sans text-sm text-ink focus:outline-none focus:border-accent"
          >
            <option value="">All roles</option>
            {meta?.roles.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </label>

        <div>
          <span className="kicker">Order by</span>
          <div className="mt-2 grid grid-cols-2 gap-px bg-rule border border-rule rounded-lg overflow-hidden">
            {[
              { key: "priority", label: "Fit + Place" },
              { key: "score", label: "Fit only" },
            ].map((opt) => (
              <button
                key={opt.key}
                onClick={() => update({ sort: opt.key })}
                className={`py-2 font-mono text-[0.7rem] uppercase tracking-widest transition-colors ${
                  filters.sort === opt.key
                    ? "bg-accent text-paper"
                    : "bg-paper-2 text-ink-soft hover:text-ink"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
