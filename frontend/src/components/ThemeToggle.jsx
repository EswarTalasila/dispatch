import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [theme, setTheme] = useState(
    () => document.documentElement.dataset.theme || "light",
  );

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <button
      onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
      title="Toggle light / dark"
      className="rounded border border-rule px-2 py-1 font-mono text-[0.6rem] uppercase tracking-[0.13em] text-ink-soft hover:text-ink hover:border-ink-soft transition-colors"
    >
      {theme === "dark" ? "Light" : "Dark"}
    </button>
  );
}
