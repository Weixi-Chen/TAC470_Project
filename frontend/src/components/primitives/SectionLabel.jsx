export function SectionLabel({ children, className = "" }) {
  return (
    <h2
      className={`text-[11px] font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 ${className}`}
    >
      {children}
    </h2>
  );
}
