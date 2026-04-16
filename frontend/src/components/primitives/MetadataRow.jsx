export function MetadataRow({ children, className = "" }) {
  return (
    <div
      className={`flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500 dark:text-slate-400 ${className}`}
    >
      {children}
    </div>
  );
}
