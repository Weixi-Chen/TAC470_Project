export function InlineAlert({ variant = "error", children }) {
  const styles =
    variant === "error"
      ? "border-red-300 bg-red-50 text-red-950 dark:border-red-500/40 dark:bg-red-950/70 dark:text-red-100"
      : "border-slate-300 bg-slate-50 text-slate-900 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100";
  return (
    <div
      role="alert"
      className={`rounded-lg border px-3 py-2 text-sm leading-snug shadow-sm ${styles}`}
    >
      {children}
    </div>
  );
}
