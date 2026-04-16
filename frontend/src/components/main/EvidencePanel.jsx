import { EvidenceCard } from "./EvidenceCard.jsx";
import { evidenceDomId } from "../../lib/paths.js";

export function EvidencePanel({ evidence, answerNonce }) {
  if (!evidence.length) return null;
  return (
    <div className="space-y-4">
      <h2 className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        Evidence
      </h2>
      <div className="space-y-3">
        {evidence.map((item, index) => (
          <EvidenceCard
            key={`${answerNonce}-${item.chunk_id || index}`}
            item={item}
            domId={evidenceDomId(item.chunk_id || String(index))}
            defaultExpanded={index === 0}
          />
        ))}
      </div>
    </div>
  );
}
