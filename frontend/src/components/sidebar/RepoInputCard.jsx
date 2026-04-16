import { SectionLabel } from "../primitives/SectionLabel.jsx";

export function RepoInputCard({
  repoPath,
  onRepoPathChange,
  onIngest,
  loading,
  disabledIngest,
  loadedBadgeName,
}) {
  return (
    <div className="space-y-2.5">
      <SectionLabel>Repository</SectionLabel>
      <label htmlFor="repo-path" className="sr-only">
        Local repository path or GitHub URL
      </label>
      <input
        id="repo-path"
        type="text"
        autoComplete="off"
        placeholder="Enter a local repo path or GitHub URL"
        value={repoPath}
        onChange={(e) => onRepoPathChange(e.target.value)}
        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm font-medium text-slate-900 shadow-sm placeholder:text-slate-600 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/25 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100 dark:placeholder:text-slate-400 dark:focus:border-blue-400 dark:focus:ring-blue-400/30"
      />
      <button
        type="button"
        onClick={onIngest}
        disabled={disabledIngest || loading}
        className="w-full rounded-lg bg-blue-600 px-3 py-2.5 text-sm font-semibold text-white shadow-md shadow-blue-600/25 transition hover:scale-[1.02] hover:bg-blue-500 active:scale-[0.99] active:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100"
      >
        {loading ? "Indexing repository…" : "Ingest Repository"}
      </button>
      {loadedBadgeName ? (
        <p className="text-xs text-slate-700 dark:text-slate-300">
          <span className="font-semibold text-slate-900 dark:text-slate-100">Loaded:</span>{" "}
          <span className="rounded-md border border-slate-300 bg-white px-2 py-0.5 font-mono text-[11px] font-medium text-slate-900 shadow-sm dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100">
            {loadedBadgeName}
          </span>
        </p>
      ) : null}
    </div>
  );
}
