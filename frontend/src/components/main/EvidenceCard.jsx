import { useEffect, useState } from "react";
import { CodeSnippetBlock } from "./CodeSnippetBlock.jsx";

function Chevron({ open }) {
  return (
    <svg
      className={`h-4 w-4 shrink-0 text-slate-400 transition-transform duration-200 ease-out dark:text-slate-500 ${
        open ? "rotate-180" : "rotate-0"
      }`}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      aria-hidden
    >
      <path d="M6 9l6 6 6-6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function EvidenceCard({ item, domId, defaultExpanded }) {
  const [open, setOpen] = useState(defaultExpanded);

  useEffect(() => {
    setOpen(defaultExpanded);
  }, [defaultExpanded, item.chunk_id]);

  return (
    <article
      id={domId}
      className="scroll-mt-28 overflow-hidden rounded-xl border border-slate-200/90 bg-white shadow-card transition duration-200 ease-out hover:-translate-y-0.5 hover:shadow-lift dark:border-white/[0.08] dark:bg-slate-900/85 dark:shadow-card-dark dark:hover:shadow-lift-dark"
    >
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="flex w-full items-start justify-between gap-3 px-4 py-3.5 text-left transition hover:bg-slate-50/90 dark:hover:bg-slate-800/50"
      >
        <div className="min-w-0 flex-1 space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[15px] font-semibold text-slate-900 dark:text-slate-100">
              {item.symbol_name}
            </span>
            <span className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-[10px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-400">
              {Number(item.score).toFixed(3)}
            </span>
          </div>
          <div className="truncate font-mono text-[11px] text-slate-500 dark:text-slate-500">
            {item.file_path}
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-500">
            Lines {item.start_line}–{item.end_line}
          </div>
        </div>
        <Chevron open={open} />
      </button>
      <div
        className="grid transition-[grid-template-rows] duration-200 ease-out motion-reduce:transition-none"
        style={{ gridTemplateRows: open ? "1fr" : "0fr" }}
      >
        <div className="min-h-0 overflow-hidden">
          <div className="space-y-3 border-t border-slate-100 px-4 pb-4 pt-3 dark:border-white/[0.06]">
            <CodeSnippetBlock code={item.snippet || ""} />
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-500">
                Why this is relevant
              </p>
              <p className="mt-1.5 text-sm leading-relaxed text-slate-700 dark:text-slate-300">
                {item.relevance_reason}
              </p>
            </div>
          </div>
        </div>
      </div>
    </article>
  );
}
