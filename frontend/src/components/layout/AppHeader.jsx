import { repoDisplayName } from "../../lib/paths.js";
import { ThemeToggle } from "./ThemeToggle.jsx";

export function AppHeader({ resolvedRepoPath, repoReady }) {
  const name = repoDisplayName(resolvedRepoPath);
  return (
    <header className="flex h-[52px] shrink-0 items-center justify-between border-b border-slate-200/90 bg-white/75 px-5 shadow-sm backdrop-blur-md dark:border-white/[0.06] dark:bg-slate-950/70">
      <div className="min-w-0 pr-4">
        <h1 className="text-[15px] font-semibold tracking-tight text-slate-900 dark:text-slate-100">
          Repo Understanding Tool
        </h1>
        <p className="mt-0.5 text-[11px] leading-tight text-slate-500 dark:text-slate-400">
          Evidence-backed answers for Python repositories
        </p>
      </div>
      <div className="flex shrink-0 items-center gap-3">
        <ThemeToggle />
        {repoReady && name ? (
          <div className="flex items-center gap-2 rounded-lg border border-slate-200/80 bg-slate-50/80 py-1 pl-2.5 pr-1.5 dark:border-white/10 dark:bg-slate-900/80">
            <span className="max-w-[180px] truncate text-xs font-medium text-slate-700 dark:text-slate-200">
              {name}
            </span>
            <span className="rounded-md bg-emerald-500/15 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400">
              Indexed
            </span>
          </div>
        ) : (
          <span className="text-[11px] font-medium text-slate-600 dark:text-slate-400">No repository loaded</span>
        )}
      </div>
    </header>
  );
}
