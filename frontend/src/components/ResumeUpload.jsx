import { useEffect, useRef, useState } from "react";

export default function ResumeUpload({ appBusy, onChanged }) {
  const [resumes, setResumes] = useState([]);
  const [parsing, setParsing] = useState(false);
  const [msg, setMsg] = useState("");
  const [drag, setDrag] = useState(false);
  const inputRef = useRef(null);

  const locked = parsing || appBusy;
  const activeId = resumes.find((r) => r.active)?.id ?? "";

  function load() {
    return fetch("/api/resumes")
      .then((r) => r.json())
      .then((d) => setResumes(d.resumes || []))
      .catch(() => {});
  }

  useEffect(() => {
    load();
  }, []);

  async function activate(id) {
    if (locked || !id) return;
    setMsg("");
    await fetch(`/api/resumes/${id}/activate`, { method: "POST" }).catch(() => {});
    await load();
    onChanged?.();
  }

  async function remove(id) {
    if (locked || !id || resumes.length <= 1) return;
    await fetch(`/api/resumes/${id}`, { method: "DELETE" }).catch(() => {});
    await load();
    onChanged?.();
  }

  async function upload(file) {
    if (!file || locked) return;
    if (!/\.(pdf|docx)$/i.test(file.name)) {
      setMsg("Please upload a PDF or DOCX.");
      return;
    }
    setParsing(true);
    setMsg("");
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch("/api/resume", { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed.");
      await load();
      setMsg("Added — re-scoring your jobs against it…");
      onChanged?.();
    } catch (e) {
      setMsg(e.message);
    } finally {
      setParsing(false);
    }
  }

  return (
    <section>
      <h2 className="kicker border-b border-rule pb-2 mb-4">Résumés</h2>

      {resumes.length > 0 && (
        <div className="mb-3 flex items-center gap-2">
          <select
            value={activeId}
            disabled={locked}
            onChange={(e) => activate(Number(e.target.value))}
            className="flex-1 rounded-lg bg-paper-2 border border-rule px-3 py-2 font-sans text-sm text-ink focus:outline-none focus:border-accent disabled:opacity-60"
          >
            {resumes.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name} ({r.chars})
              </option>
            ))}
          </select>
          <button
            onClick={() => remove(activeId)}
            disabled={locked || resumes.length <= 1}
            title="Delete this résumé"
            className="rounded-lg border border-rule px-3 py-2 text-ink-faint hover:text-accent hover:border-accent/40 transition-colors disabled:opacity-40 disabled:hover:text-ink-faint disabled:hover:border-rule"
          >
            ✕
          </button>
        </div>
      )}

      <div
        onDragOver={(e) => {
          e.preventDefault();
          if (!locked) setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          upload(e.dataTransfer.files[0]);
        }}
        onClick={() => !locked && inputRef.current?.click()}
        className={`rounded-xl border border-dashed px-4 py-5 text-center transition-colors ${
          drag ? "border-accent bg-accent/10" : "border-rule hover:border-ink-soft"
        } ${locked ? "cursor-wait opacity-70" : "cursor-pointer"}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => upload(e.target.files[0])}
        />
        <p className="font-sans text-sm text-ink-soft leading-snug">
          {parsing
            ? "Parsing with Claude…"
            : resumes.length
              ? "Add another résumé (PDF or DOCX)"
              : "Drag a PDF or DOCX here, or click to browse"}
        </p>
      </div>

      {msg && <p className="mt-2 font-sans text-xs text-accent">{msg}</p>}
    </section>
  );
}
