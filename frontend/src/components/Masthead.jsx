import { motion } from "framer-motion";
import ThemeToggle from "./ThemeToggle.jsx";

const FULL_DATE = new Date().toLocaleDateString("en-US", {
  weekday: "long",
  year: "numeric",
  month: "long",
  day: "numeric",
});

export default function Masthead({ total }) {
  return (
    <header className="border-b border-rule pb-5">
      <div className="flex items-center justify-between border-b border-rule pb-2">
        <span className="kicker">Est. MMXXVI · Raleigh, N.C.</span>
        <span className="kicker hidden sm:block">Edition № {total || "—"}</span>
        <div className="flex items-center gap-3">
          <span className="kicker hidden sm:block">{FULL_DATE}</span>
          <ThemeToggle />
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        className="pt-5 text-center"
      >
        <h1 className="font-sans font-black leading-[1.05] tracking-[-0.04em] text-ink text-[clamp(2.8rem,10vw,7rem)]">
          Dispatch
        </h1>
        <p className="kicker mt-5 !tracking-[0.16em]">
          Roles worth your morning, ranked by fit
        </p>
      </motion.div>
    </header>
  );
}
