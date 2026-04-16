import { fileNameFromPath } from "../../lib/paths.js";

function dirnameHint(path) {
  const parts = path.split("/").filter(Boolean);
  if (parts.length <= 1) return "";
  const dir = parts.slice(0, -1).join("/");
  return dir.length > 42 ? `…/${dir.slice(-36)}` : dir;
}

export function RelatedFilesCard({ filePaths, fileToEvidenceDomId }) {
  if (!filePaths.length) return null;

  const scrollTo = (filePath) => {
    const id = fileToEvidenceDomId.get(filePath);
    if (!id) return;
    const el = document.getElementById(id);
    el?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="rounded-2xl border border-slate-200/90 bg-white/95 p-5 shadow-card dark:border-white/[0.08] dark:bg-slate-900/80 dark:shadow-card-dark">
      <h2 className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        Related files
      </h2>
      <ul className="mt-3 space-y-0.5">
        {filePaths.map((fp) => {
          const hint = dirnameHint(fp);
          return (
            <li key={fp}>
              <button
                type="button"
                onClick={() => scrollTo(fp)}
                className="w-full rounded-lg px-2.5 py-2 text-left text-sm text-slate-800 transition hover:bg-blue-500/[0.06] hover:text-slate-900 dark:text-slate-200 dark:hover:bg-blue-500/10 dark:hover:text-white"
              >
                <span className="font-medium">{fileNameFromPath(fp)}</span>
                {hint ? (
                  <span className="mt-0.5 block truncate font-mono text-[11px] text-slate-500 dark:text-slate-500">
                    {hint}
                  </span>
                ) : null}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
