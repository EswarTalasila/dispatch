import { motion } from "framer-motion";
import PropTypes from "prop-types";
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
  const strong = job.score >= 75;

  return (
    <motion.article
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.5,
        delay: Math.min(index * 0.04, 0.5),
        ease: [0.22, 1, 0.36, 1],
      }}
      className="group rounded-2xl border border-rule bg-paper-2/70 backdrop-blur-sm p-5 sm:p-6 transition-all duration-300 hover:-translate-y-0.5 hover:border-accent/40 hover:bg-paper-2 hover:shadow-[0_14px_44px_-16px_rgba(0,0,0,0.8)]"
    >
      <div className="flex gap-5 sm:gap-6">
        {/* Fit score */}
        <div className="shrink-0 w-[64px] sm:w-[80px] text-center">
          <div
            className={`font-display font-black leading-none tabular-nums text-[2.4rem] sm:text-[3rem] ${tier.className}`}
          >
            {job.score}
          </div>
          <div className="mt-1.5 font-mono text-[0.58rem] uppercase tracking-[0.14em] text-ink-faint">
            {tier.label}
          </div>
          <div className="mt-2.5 h-1 w-full rounded-full bg-paper-3 overflow-hidden">
            <div
              className={`h-full rounded-full ${strong ? "bg-ink" : "bg-ink-faint"}`}
              style={{ width: `${job.score}%` }}
            />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-x-2 gap-y-1 font-mono text-[0.62rem] uppercase tracking-[0.1em] text-ink-faint">
            <span>{job.role_query}</span>
            <span className="opacity-40">/</span>
            <span>{job.location}</span>
            {job.tier_label !== "OTHER" && (
              <span className="rounded-full border border-rule bg-paper-3 px-2 py-0.5 leading-none text-ink-soft">
                {job.tier_label}
              </span>
            )}
            <span className="ml-auto opacity-70">{formatDate(job.found_date)}</span>
          </div>

          <h3 className="mt-2 font-display text-[1.4rem] sm:text-[1.6rem] leading-tight tracking-[-0.01em] text-ink">
            {job.title}
          </h3>
          <p className="mt-0.5 font-sans font-semibold text-ink-soft">{job.company}</p>

          <p className="mt-3 font-sans text-[0.95rem] leading-relaxed text-ink-soft max-w-2xl">
            {job.reason}
          </p>

          {job.url && (
            <a
              href={job.url}
              target="_blank"
              rel="noreferrer"
              className="group/link mt-4 inline-flex items-center gap-1.5 font-mono text-[0.7rem] font-semibold uppercase tracking-[0.1em] text-accent"
            >
              Read the posting{" "}
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

JobEntry.propTypes = {
  job: PropTypes.object.isRequired,
  index: PropTypes.number,
};
