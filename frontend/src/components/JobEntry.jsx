import { motion } from "framer-motion";
import { fitTier } from "../api.js";

function formatDate(iso) {
  if (!iso) return "";
  return new Date(iso + "T00:00:00").toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

export default function JobEntry({ job, index }) {
  const tier = fitTier(job.score);

  return (
    <motion.article
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.5,
        delay: Math.min(index * 0.04, 0.5),
        ease: [0.22, 1, 0.36, 1],
      }}
      className="group relative border-t border-rule"
    >
      {/* accent rule that slides in on hover */}
      <span className="absolute left-0 top-0 h-full w-[3px] bg-accent scale-y-0 group-hover:scale-y-100 origin-top transition-transform duration-300" />

      <div className="flex gap-5 sm:gap-8 py-7 pl-0 group-hover:pl-4 transition-[padding] duration-300">
        {/* Fit score — the hero */}
        <div className="shrink-0 w-[68px] sm:w-[88px] text-center">
          <div
            className={`font-display font-black leading-none tabular-nums text-[2.6rem] sm:text-[3.4rem] ${tier.className}`}
          >
            {job.score}
          </div>
          <div className="mt-1.5 font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-soft">
            {tier.label}
          </div>
          <div className="mt-2 h-[3px] w-full bg-rule overflow-hidden">
            <div
              className={`h-full ${job.score >= 75 ? "bg-accent" : "bg-ink"}`}
              style={{ width: `${job.score}%` }}
            />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-x-2 gap-y-1 font-mono text-[0.64rem] uppercase tracking-[0.1em] text-ink-soft">
            <span>{job.role_query}</span>
            <span className="text-ink-faint">/</span>
            <span>{job.location}</span>
            {job.tier_label !== "OTHER" && (
              <span className="bg-ink text-paper px-1.5 py-0.5 leading-none">
                {job.tier_label}
              </span>
            )}
            <span className="ml-auto text-ink-faint">{formatDate(job.found_date)}</span>
          </div>

          <h3 className="mt-2 font-display text-[1.45rem] sm:text-[1.7rem] leading-tight tracking-[-0.01em] text-ink">
            {job.title}
          </h3>
          <p className="mt-0.5 font-sans font-semibold text-ink">{job.company}</p>

          <p className="mt-3 font-display italic text-[1.02rem] leading-relaxed text-ink-soft max-w-2xl">
            {job.reason}
          </p>

          {job.url && (
            <a
              href={job.url}
              target="_blank"
              rel="noreferrer"
              className="group/link mt-4 inline-flex items-center gap-2 font-mono text-[0.72rem] font-semibold uppercase tracking-[0.1em] text-accent"
            >
              Read the posting
              <span className="transition-transform duration-300 group-hover/link:translate-x-1">
                →
              </span>
            </a>
          )}
        </div>
      </div>
    </motion.article>
  );
}
