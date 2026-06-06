export async function fetchJobs(params) {
  const qs = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== "" && v !== 0),
  );
  const res = await fetch(`/api/jobs?${qs}`);
  if (!res.ok) throw new Error("Failed to load jobs");
  return res.json();
}

export async function fetchMeta() {
  const res = await fetch("/api/meta");
  if (!res.ok) throw new Error("Failed to load meta");
  return res.json();
}

export async function triggerRefresh() {
  const res = await fetch("/api/refresh", { method: "POST" });
  return res.json();
}

export async function getStatus() {
  const res = await fetch("/api/status");
  return res.json();
}

export function fitTier(score) {
  if (score >= 75) return { label: "Strong", className: "text-accent" };
  if (score >= 60) return { label: "Solid", className: "text-ink" };
  return { label: "Stretch", className: "text-ink-soft" };
}
