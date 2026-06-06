import { useEffect, useRef, useState } from "react";
import {
  fetchJobs,
  fetchMeta,
  triggerRefresh,
  triggerRescore,
  getStatus,
} from "./api.js";
import Masthead from "./components/Masthead.jsx";
import StatsRail from "./components/StatsRail.jsx";
import FilterPanel from "./components/FilterPanel.jsx";
import JobEntry from "./components/JobEntry.jsx";
import ResumeUpload from "./components/ResumeUpload.jsx";

export default function App() {
  const [meta, setMeta] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    q: "",
    min_score: 0,
    role: "",
    sort: "priority",
  });
  const [refreshing, setRefreshing] = useState(false);
  const [busyLabel, setBusyLabel] = useState("Fetch new jobs");
  const [refreshMsg, setRefreshMsg] = useState("");
  const [prog, setProg] = useState({ stage: "", percent: 0 });
  const [bucket, setBucket] = useState("new");
  const filtersRef = useRef(filters);
  filtersRef.current = filters;

  useEffect(() => {
    fetchMeta().then(setMeta).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const handle = setTimeout(() => {
      fetchJobs(filters)
        .then(setJobs)
        .catch(() => setJobs([]))
        .finally(() => setLoading(false));
    }, 150);
    return () => clearTimeout(handle);
  }, [filters]);

  async function runTask(trigger, label) {
    if (refreshing) return;
    setRefreshing(true);
    setBusyLabel(label);
    setRefreshMsg("");
    setProg({ stage: "Starting…", percent: 2 });
    try {
      await trigger();
    } catch {
      setRefreshing(false);
      setRefreshMsg("Couldn't reach the server.");
      return;
    }
    const poll = setInterval(async () => {
      const s = await getStatus().catch(() => null);
      if (!s) return;
      setProg({ stage: s.stage, percent: s.percent });
      if (!s.running) {
        clearInterval(poll);
        setRefreshing(false);
        setRefreshMsg(s.message || "Done.");
        fetchMeta().then(setMeta).catch(() => {});
        fetchJobs(filtersRef.current).then(setJobs).catch(() => {});
      }
    }, 1000);
  }

  const handleRefresh = () => runTask(triggerRefresh, "Fetching new jobs…");
  const handleRescore = () => runTask(triggerRescore, "Re-scoring…");

  // "New" = jobs from the most recent fetch; "This week" = last 7 days.
  const latestDate = meta?.dates?.[0];
  const weekAgo = new Date(Date.now() - 7 * 864e5).toISOString().slice(0, 10);
  const inBucket = (job, b) => {
    if (b === "all") return true;
    if (b === "new") return latestDate ? job.found_date === latestDate : true;
    return job.found_date >= weekAgo;
  };
  const counts = {
    new: jobs.filter((j) => inBucket(j, "new")).length,
    week: jobs.filter((j) => inBucket(j, "week")).length,
    all: jobs.length,
  };
  const displayed = jobs.filter((j) => inBucket(j, bucket));

  return (
    <div className="min-h-screen">
      <div className="grain" />

      <div className="mx-auto max-w-6xl px-5 sm:px-8 py-8 sm:py-12">
        <Masthead total={meta?.total} />

        <div className="mt-7 grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-10 lg:gap-14">
          {/* Sidebar */}
          <aside className="lg:sticky lg:top-10 self-start flex flex-col gap-10">
            <div>
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="w-full rounded-lg bg-accent text-paper font-sans font-semibold text-sm py-3 px-4 flex items-center justify-center gap-2 hover:bg-accent-deep transition-colors disabled:opacity-70 disabled:cursor-wait"
              >
                <span
                  className={`text-base leading-none ${refreshing ? "animate-spin" : ""}`}
                >
                  ↻
                </span>
                {refreshing ? busyLabel : "Fetch new jobs"}
              </button>
              {refreshing && (
                <div className="mt-3">
                  <div className="flex items-baseline justify-between font-sans text-xs text-ink-soft">
                    <span>{prog.stage}</span>
                    <span className="tabular-nums text-accent">{prog.percent}%</span>
                  </div>
                  <div className="mt-1.5 h-1.5 w-full bg-rule overflow-hidden">
                    <div
                      className="h-full bg-accent transition-all duration-700 ease-out"
                      style={{ width: `${prog.percent}%` }}
                    />
                  </div>
                </div>
              )}
              {!refreshing && refreshMsg && (
                <p className="mt-2 font-sans text-xs text-accent">{refreshMsg}</p>
              )}
            </div>
            <ResumeUpload appBusy={refreshing} onUploaded={handleRescore} />
            <StatsRail meta={meta} />
            <FilterPanel filters={filters} setFilters={setFilters} meta={meta} />
            <p className="font-mono text-[0.6rem] leading-relaxed uppercase tracking-[0.15em] text-ink-faint border-t border-rule pt-4">
              Pulled from Adzuna and scored against your résumé by Claude, on demand.
            </p>
          </aside>

          {/* Main column */}
          <main>
            <div className="flex flex-wrap items-end gap-x-6 gap-y-2 border-b border-rule mb-4">
              <h2 className="kicker pb-2">The Listings</h2>
              <div className="ml-auto flex gap-5">
                {[
                  { id: "new", label: "New" },
                  { id: "week", label: "This week" },
                  { id: "all", label: "All" },
                ].map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setBucket(t.id)}
                    className={`-mb-px border-b-2 pb-2 font-sans text-sm transition-colors ${
                      bucket === t.id
                        ? "border-accent text-ink font-semibold"
                        : "border-transparent text-ink-soft hover:text-ink"
                    }`}
                  >
                    {t.label}{" "}
                    <span className="font-mono text-xs tabular-nums text-ink-faint">
                      {counts[t.id]}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {loading && (
              <p className="kicker py-20 text-center">setting type…</p>
            )}

            {!loading && displayed.length === 0 && (
              <p className="py-20 text-center font-display italic text-xl text-ink-soft">
                {bucket === "new"
                  ? "Nothing new since your last fetch."
                  : "No dispatches match your refinements."}
              </p>
            )}

            {!loading && (
              <div className="flex flex-col gap-3">
                {displayed.map((job, i) => (
                  <JobEntry key={job.id} job={job} index={i} />
                ))}
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}
