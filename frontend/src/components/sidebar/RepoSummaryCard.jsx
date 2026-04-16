import { repoDisplayName } from "../../lib/paths.js";

export function RepoSummaryCard({
  resolvedRepoPath,
  fileCount,
  indexedChunks,
  graphSummary,
  lastUpdatedLabel,
}) {
  if (!resolvedRepoPath) return null;
  const name = repoDisplayName(resolvedRepoPath);
  return (
    <div className="rounded-xl border border-slate-300 bg-white p-4 text-sm shadow-md dark:border-slate-700 dark:bg-slate-900 dark:shadow-lg dark:shadow-black/30">
      <div className="text-[15px] font-bold tracking-tight text-slate-950 dark:text-slate-50">{name}</div>
      <dl className="mt-3 space-y-2 text-[13px]">
        <div className="flex justify-between gap-2">
          <dt className="text-slate-700 dark:text-slate-400">Manifest files</dt>
          <dd className="font-mono font-semibold text-slate-950 dark:text-slate-100">{fileCount ?? "—"}</dd>
        </div>
        <div className="flex justify-between gap-2">
          <dt className="text-slate-700 dark:text-slate-400">Parsed chunks</dt>
          <dd className="font-mono font-semibold text-slate-950 dark:text-slate-100">{indexedChunks ?? "—"}</dd>
        </div>
        {graphSummary ? (
          <div className="border-t border-slate-200 pt-2 text-[12px] text-slate-700 dark:border-slate-700 dark:text-slate-400">
            {graphSummary}
          </div>
        ) : null}
      </dl>
      {lastUpdatedLabel ? (
        <p className="mt-3 border-t border-slate-200 pt-2.5 text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:border-slate-700 dark:text-slate-400">
          {lastUpdatedLabel}
        </p>
      ) : null}
      <span className="mt-3 inline-flex rounded-md border border-emerald-600/25 bg-emerald-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-emerald-900 dark:border-emerald-500/30 dark:bg-emerald-950/80 dark:text-emerald-300">
        Repository indexed
      </span>
    </div>
  );
}
