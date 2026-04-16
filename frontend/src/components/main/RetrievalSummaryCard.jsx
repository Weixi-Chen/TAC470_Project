export function RetrievalSummaryCard({ evidence, reasoningTrace }) {
  if (!evidence.length && !reasoningTrace?.length) return null;

  const graphish = evidence.filter((e) =>
    /graph|caller|callee|neighborhood|parent|structural|lexical/i.test(
      e.relevance_reason || ""
    )
  ).length;

  return (
    <div className="rounded-2xl border border-dashed border-slate-300/80 bg-white/60 p-5 dark:border-white/[0.1] dark:bg-slate-900/40">
      <h2 className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        Retrieval summary
      </h2>
      <dl className="mt-4 grid gap-3 text-xs text-slate-600 dark:text-slate-400 sm:grid-cols-3">
        <div>
          <dt className="text-slate-500 dark:text-slate-500">Evidence selected</dt>
          <dd className="mt-0.5 font-mono text-sm font-medium text-slate-900 dark:text-slate-100">
            {evidence.length}
          </dd>
        </div>
        <div>
          <dt className="text-slate-500 dark:text-slate-500">Graph / context hints</dt>
          <dd className="mt-0.5 font-mono text-sm font-medium text-slate-900 dark:text-slate-100">
            {graphish}
          </dd>
        </div>
        <div>
          <dt className="text-slate-500 dark:text-slate-500">Reasoning steps</dt>
          <dd className="mt-0.5 font-mono text-sm font-medium text-slate-900 dark:text-slate-100">
            {reasoningTrace?.length ?? 0}
          </dd>
        </div>
      </dl>
      {reasoningTrace?.length ? (
        <div className="mt-4 border-t border-slate-200/80 pt-4 dark:border-white/[0.06]">
          <h3 className="text-[10px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-500">
            Reasoning path
          </h3>
          <ol className="mt-2 list-decimal space-y-1 pl-4 text-xs leading-relaxed text-slate-600 dark:text-slate-400">
            {reasoningTrace.map((line, i) => (
              <li key={i}>{line}</li>
            ))}
          </ol>
        </div>
      ) : null}
    </div>
  );
}
