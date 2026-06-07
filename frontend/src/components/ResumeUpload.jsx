import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

export default function ResumeUpload({ appBusy, onChanged }) {
  const [resumes, setResumes] = useState([]);
  const [parsing, setParsing] = useState(false);
  const [msg, setMsg] = useState("");
  const [drag, setDrag] = useState(false);
  const [preview, setPreview] = useState(null); // { name, text }
  const inputRef = useRef(null);

  const locked = parsing || appBusy;
  const activeId = resumes.find((r) => r.active)?.id ?? "";

  function load() {
    return fetch("/api/resumes")
      .then((r) => r.json())
      .then((d) => {
        const list = d.resumes || [];
        setResumes(list);
        return list;
      })
      .catch(() => []);
  }

  useEffect(() => {
    load();
  }, []);

  // Close the preview modal on Escape.
  useEffect(() => {
    if (!preview) return;
    const onKey = (e) => e.key === "Escape" && setPreview(null);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [preview]);

  async function activate(id) {
    if (locked || !id) return;
    setMsg("");
    await fetch(`/api/resumes/${id}/activate`, { method: "POST" }).catch(() => {});
    await load();
    onChanged?.();
  }

  async function showPreview(id) {
    if (!id) return;
    setMsg("");
    try {
      const res = await fetch(`/api/resumes/${id}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Couldn't load résumé.");
      setPreview({ name: data.name, text: data.text });
    } catch (e) {
      setMsg(e.message);
    }
  }

  async function remove(id) {
    if (locked || !id) return;
    if (!window.confirm("Delete this résumé? This can't be undone.")) return;
    setMsg("");
    await fetch(`/api/resumes/${id}`, { method: "DELETE" }).catch(() => {});
    const list = await load();
    // The ✕ deletes the active résumé; if another became active, re-score
    // against it. If none remain, leave existing scores untouched.
    if (list.some((r) => r.active)) onChanged?.();
    else setMsg("Résumé deleted. Add one to re-score your jobs.");
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
        <div className="mb-3">
          <div className="flex items-center gap-2">
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
              disabled={locked}
              title="Delete this résumé"
              className="rounded-lg border border-rule px-3 py-2 text-ink-faint hover:text-accent hover:border-accent/40 transition-colors disabled:opacity-40 disabled:hover:text-ink-faint disabled:hover:border-rule"
            >
              ✕
            </button>
          </div>
          <button
            onClick={() => showPreview(activeId)}
            disabled={!activeId}
            className="mt-2 font-mono text-[0.62rem] uppercase tracking-[0.12em] text-ink-soft hover:text-accent transition-colors disabled:opacity-40"
          >
            Preview active résumé →
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
        role="button"
        tabIndex={locked ? -1 : 0}
        aria-label="Add a résumé (PDF or DOCX)"
        onKeyDown={(e) => {
          if (!locked && (e.key === "Enter" || e.key === " ")) {
            e.preventDefault();
            inputRef.current?.click();
          }
        }}
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

      {preview && createPortal(
        <div
          onClick={(e) => e.target === e.currentTarget && setPreview(null)}
          onKeyDown={(e) => e.key === "Enter" && setPreview(null)}
          role="button"
          tabIndex={0}
          aria-label="Close preview"
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm"
        >
          <div
            className="flex max-h-[80vh] w-full max-w-2xl flex-col rounded-2xl border border-rule bg-paper-2 shadow-2xl"
          >
            <div className="flex items-center justify-between border-b border-rule px-5 py-3">
              <h3 className="font-sans text-sm font-semibold text-ink">
                {preview.name}
              </h3>
              <button
                onClick={() => setPreview(null)}
                className="text-ink-faint hover:text-accent transition-colors"
              >
                ✕
              </button>
            </div>
            <div className="overflow-y-auto px-5 py-4">
              <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-ink-soft">
                {preview.text}
              </pre>
            </div>
          </div>
        </div>,
        document.body,
      )}
    </section>
  );
}
