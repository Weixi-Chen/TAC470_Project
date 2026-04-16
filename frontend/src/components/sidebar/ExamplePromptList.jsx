import { SectionLabel } from "../primitives/SectionLabel.jsx";

const DEFAULT_EXAMPLES = [
  "Where is the entry point?",
  "How is authentication implemented?",
  "What happens during startup?",
  "Which files are most important for onboarding?",
  "Where is database configuration defined?",
];

export function ExamplePromptList({ prompts = DEFAULT_EXAMPLES, onSelect }) {
  return (
    <div className="space-y-2.5">
      <SectionLabel>Examples</SectionLabel>
      <ul className="flex flex-col gap-2">
        {prompts.map((text) => (
          <li key={text}>
            <button
              type="button"
              onClick={() => onSelect(text)}
              className="w-full rounded-full border border-slate-300 bg-white px-3 py-2 text-left text-xs font-medium leading-snug text-slate-900 shadow-sm transition hover:scale-[1.01] hover:border-blue-500/50 hover:bg-blue-50 hover:text-slate-950 active:scale-[0.99] dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100 dark:hover:border-blue-400/60 dark:hover:bg-slate-800 dark:hover:text-white"
            >
              {text}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
