import { useEffect, useRef, useState } from "react";

export default function ResumeUpload({ appBusy, onUploaded }) {
  const [info, setInfo] = useState(null);
  const [parsing, setParsing] = useState(false);
  const [msg, setMsg] = useState("");
  const [drag, setDrag] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    fetch("/api/resume")
      .then((r) => r.json())
      .then(setInfo)
      .catch(() => {});
  }, []);

  const locked = parsing || appBusy;

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
      setInfo({ present: true, chars: data.chars });
      setMsg("Parsed — re-scoring your jobs against it…");
      onUploaded?.();
    } catch (e) {
      setMsg(e.message);
    } finally {
      setParsing(false);
    }
  }

  return (
    <section>
      <h2 className="kicker border-b border-rule pb-2 mb-4">Résumé</h2>

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
        className={`rounded-xl border border-dashed px-4 py-6 text-center transition-colors ${
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
          {parsing ? "Parsing with Claude…" : "Drag a PDF or DOCX here, or click to browse"}
        </p>
      </div>

      {info?.present && !parsing && (
        <p className="mt-2 font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-faint">
          On file · {info.chars} chars
        </p>
      )}
      {msg && <p className="mt-2 font-sans text-xs text-accent">{msg}</p>}
    </section>
  );
}
