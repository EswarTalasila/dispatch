function Stat({ label, value }) {
  return (
    <div className="flex items-baseline gap-2">
      <span className="font-sans text-sm text-ink-soft whitespace-nowrap">
        {label}
      </span>
      <span className="flex-1 border-b border-dotted border-rule translate-y-[-3px]" />
      <span className="font-mono text-base text-ink tabular-nums">{value}</span>
    </div>
  );
}

export default function StatsRail({ meta }) {
  if (!meta) return null;
  return (
    <section>
      <h2 className="kicker border-b border-ink pb-2 mb-4">The Numbers</h2>
      <div className="flex flex-col gap-3">
        <Stat label="Roles on file" value={meta.total} />
        <Stat label="Average fit" value={meta.avg_score} />
        <Stat label="Best fit" value={meta.top_score} />
        <Stat label="In North Carolina" value={meta.nc_count} />
        <Stat label="In Texas" value={meta.tx_count} />
      </div>
    </section>
  );
}
