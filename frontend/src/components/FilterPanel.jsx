import PropTypes from "prop-types";

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

        <div>
          <div className="flex items-center justify-between">
            <span className="kicker">Minimum fit</span>
            <span className="font-mono text-sm text-accent tabular-nums">
              {filters.min_score}
            </span>
          </div>
          <input
            type="range"
            aria-label="Minimum fit"
            min="0"
            max="100"
            step="5"
            value={filters.min_score}
            onChange={(e) => update({ min_score: Number(e.target.value) })}
            className="mt-3"
          />
        </div>

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
      </div>
    </section>
  );
}

FilterPanel.propTypes = {
  filters: PropTypes.object.isRequired,
  setFilters: PropTypes.func.isRequired,
  meta: PropTypes.object,
};
