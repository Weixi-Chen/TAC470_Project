import { MetadataRow } from "../primitives/MetadataRow.jsx";

function SkeletonLine({ className = "" }) {
  return (
    <div
      className={`skeleton-bar h-3 animate-shimmer ${className}`}
      aria-hidden
    />
  );
}

export function AnswerCard({
  answer,
  chunkCount,
  crossFileReasoning,
  isLoading,
}) {
  if (isLoading) {
    return (
      <div className="rounded-2xl border border-blue-500/25 bg-white p-8 shadow-answer dark:border-blue-400/30 dark:bg-slate-900/90 dark:shadow-answer-dark">
        <h2 className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Answer
        </h2>
        <div className="mt-6 space-y-2.5">
          <SkeletonLine className="w-full" />
          <SkeletonLine className="w-[92%]" />
          <SkeletonLine className="w-4/5" />
        </div>
        <p className="mt-6 text-xs font-medium text-blue-600/90 dark:text-blue-400/90">
          Retrieving evidence & generating answer…
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-blue-500/30 bg-white p-8 shadow-answer ring-1 ring-blue-500/10 dark:border-blue-400/35 dark:bg-slate-900/95 dark:shadow-answer-dark dark:ring-blue-400/15">
      <h2 className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        Answer
      </h2>
      <div className="mt-5 whitespace-pre-wrap text-[16px] font-normal leading-[1.65] text-slate-900 dark:text-slate-100">
        {answer || "—"}
      </div>
      <MetadataRow className="mt-6 border-t border-slate-200/90 pt-5 dark:border-white/[0.06]">
        <span>Based on {chunkCount} retrieved code chunks</span>
        <span aria-hidden className="text-slate-300 dark:text-slate-600">
          ·
        </span>
        <span>Evidence-backed</span>
        <span aria-hidden className="text-slate-300 dark:text-slate-600">
          ·
        </span>
        <span>Cross-file reasoning: {crossFileReasoning ? "Yes" : "No"}</span>
      </MetadataRow>
    </div>
  );
}
