import { SectionLabel } from "../primitives/SectionLabel.jsx";

/** @typedef {'idle' | 'active' | 'done'} RowTone */

/**
 * @param {{ label: string, tone: RowTone }[]} rows
 */
export function StatusPanel({ rows }) {
  return (
    <div className="space-y-2.5">
      <SectionLabel>Status</SectionLabel>
      <ul className="space-y-2.5 text-[13px] leading-snug">
        {rows.map((row) => {
          const cls =
            row.tone === "active"
              ? "font-semibold text-amber-900 dark:text-amber-200"
              : row.tone === "done"
                ? "font-medium text-slate-900 dark:text-slate-100"
                : "font-medium text-slate-600 dark:text-slate-400";
          const dot =
            row.tone === "active"
              ? "bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.55)]"
              : row.tone === "done"
                ? "bg-emerald-500"
                : "bg-slate-400 dark:bg-slate-500";
          return (
            <li key={row.label} className={`flex items-center gap-2.5 ${cls}`}>
              <span className={`h-2 w-2 shrink-0 rounded-full ${dot}`} aria-hidden />
              {row.label}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
