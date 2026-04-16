import { SectionLabel } from "../primitives/SectionLabel.jsx";

export function QuestionComposer({
  question,
  onQuestionChange,
  onAsk,
  askLoading,
  disabledAsk,
}) {
  const handleKeyDown = (e) => {
    if (e.key !== "Enter") return;
    if (e.shiftKey) return;
    if (e.metaKey || e.ctrlKey) {
      e.preventDefault();
      if (!disabledAsk && !askLoading && question.trim()) onAsk();
    }
  };

  return (
    <div className="space-y-2.5">
      <SectionLabel>Ask</SectionLabel>
      <label htmlFor="question" className="sr-only">
        Question about the repository
      </label>
      <textarea
        id="question"
        rows={4}
        placeholder="Ask about repository structure, functionality, or entry points"
        value={question}
        onChange={(e) => onQuestionChange(e.target.value)}
        onKeyDown={handleKeyDown}
        className="w-full resize-y rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm font-medium leading-relaxed text-slate-900 shadow-sm placeholder:text-slate-600 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/25 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100 dark:placeholder:text-slate-400 dark:focus:border-blue-400 dark:focus:ring-blue-400/30"
      />
      <p className="text-[11px] font-medium text-slate-600 dark:text-slate-400">
        ⌘ Enter or Ctrl+Enter to submit
      </p>
      <button
        type="button"
        onClick={onAsk}
        disabled={disabledAsk || askLoading}
        className="w-full rounded-lg bg-blue-600 px-3 py-2.5 text-sm font-semibold text-white shadow-md shadow-blue-600/25 transition hover:scale-[1.02] hover:bg-blue-500 active:scale-[0.99] active:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100"
      >
        {askLoading ? "Working…" : "Ask"}
      </button>
    </div>
  );
}
