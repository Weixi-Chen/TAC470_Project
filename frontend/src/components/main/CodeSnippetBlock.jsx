export function CodeSnippetBlock({ code }) {
  return (
    <pre className="max-h-52 overflow-x-auto overflow-y-auto rounded-lg border border-slate-800/80 bg-[#0b1220] p-4 font-mono text-[12px] leading-relaxed text-slate-300 shadow-inner dark:border-slate-700/50 dark:bg-[#060b14]">
      {code}
    </pre>
  );
}
