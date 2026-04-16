export function MainEmptyState({ phase }) {
  if (phase === "no-repo") {
    return (
      <div className="flex min-h-[340px] flex-col justify-center rounded-2xl border border-slate-200/90 bg-white/90 p-12 text-center shadow-card dark:border-white/[0.08] dark:bg-slate-900/70 dark:shadow-card-dark">
        <p className="text-base font-semibold tracking-tight text-slate-900 dark:text-slate-100">
          Understand a Python repository with evidence
        </p>
        <p className="mx-auto mt-4 max-w-md text-sm leading-relaxed text-slate-600 dark:text-slate-400">
          Enter a local path on this machine, then{" "}
          <strong className="font-semibold text-slate-800 dark:text-slate-200">Ingest Repository</strong>{" "}
          to scan, chunk, and index the codebase. Answers cite real file and line ranges—nothing
          chatbot-style.
        </p>
      </div>
    );
  }

  if (phase === "repo-ready") {
    return (
      <div className="flex min-h-[300px] flex-col justify-center rounded-2xl border border-slate-200/90 bg-white/90 p-12 text-center shadow-card dark:border-white/[0.08] dark:bg-slate-900/70 dark:shadow-card-dark">
        <p className="text-base font-semibold tracking-tight text-slate-900 dark:text-slate-100">
          Ask a question to explore this repository
        </p>
        <p className="mx-auto mt-4 max-w-md text-sm leading-relaxed text-slate-600 dark:text-slate-400">
          Use the sidebar or try an{" "}
          <strong className="font-semibold text-slate-800 dark:text-slate-200">example prompt</strong>{" "}
          to inspect structure, entry points, and implementation—with collapsible evidence you can
          trust.
        </p>
      </div>
    );
  }

  return null;
}
