import { useCallback, useMemo, useState } from "react";
import { postJson } from "./lib/api.js";
import {
  buildFileToEvidenceDomId,
  repoDisplayName,
  uniqueRelatedFiles,
} from "./lib/paths.js";
import { AppHeader } from "./components/layout/AppHeader.jsx";
import { InlineAlert } from "./components/primitives/InlineAlert.jsx";
import { SidebarSection } from "./components/sidebar/SidebarSection.jsx";
import { RepoInputCard } from "./components/sidebar/RepoInputCard.jsx";
import { RepoSummaryCard } from "./components/sidebar/RepoSummaryCard.jsx";
import { QuestionComposer } from "./components/sidebar/QuestionComposer.jsx";
import { ExamplePromptList } from "./components/sidebar/ExamplePromptList.jsx";
import { StatusPanel } from "./components/sidebar/StatusPanel.jsx";
import { AnswerCard } from "./components/main/AnswerCard.jsx";
import { EvidencePanel } from "./components/main/EvidencePanel.jsx";
import { RelatedFilesCard } from "./components/main/RelatedFilesCard.jsx";
import { RetrievalSummaryCard } from "./components/main/RetrievalSummaryCard.jsx";
import { MainEmptyState } from "./components/main/MainEmptyState.jsx";

export default function App() {
  const [repoPath, setRepoPath] = useState("");
  const [resolvedRepoPath, setResolvedRepoPath] = useState("");
  const [fileCount, setFileCount] = useState(null);
  const [indexedChunks, setIndexedChunks] = useState(null);
  const [graphNodes, setGraphNodes] = useState(null);
  const [graphEdges, setGraphEdges] = useState(null);
  const [lastIngestedAt, setLastIngestedAt] = useState("");

  const [ingestLoading, setIngestLoading] = useState(false);
  const [ingestError, setIngestError] = useState("");

  const [question, setQuestion] = useState("");
  const [askLoading, setAskLoading] = useState(false);
  const [askError, setAskError] = useState("");
  const [answer, setAnswer] = useState("");
  const [evidence, setEvidence] = useState([]);
  const [reasoningTrace, setReasoningTrace] = useState([]);
  const [answerNonce, setAnswerNonce] = useState(0);
  const [completedAsk, setCompletedAsk] = useState(false);

  const relatedFiles = useMemo(() => uniqueRelatedFiles(evidence), [evidence]);
  const fileToEvidenceDomId = useMemo(
    () => buildFileToEvidenceDomId(evidence),
    [evidence]
  );
  const crossFileReasoning = useMemo(() => {
    const paths = new Set(evidence.map((e) => e.file_path).filter(Boolean));
    return paths.size > 1;
  }, [evidence]);

  const graphSummary =
    graphNodes != null && graphEdges != null
      ? `Structure graph · ${graphNodes} nodes / ${graphEdges} edges`
      : "";

  const statusRows = useMemo(() => {
    const repoDone = Boolean(resolvedRepoPath) && !ingestLoading;
    const repoActive = ingestLoading;
    const askActive = askLoading;
    const answered = Boolean(answer) || evidence.length > 0;
    return [
      {
        label: "Repository indexed",
        tone: repoDone ? "done" : repoActive ? "active" : "idle",
      },
      {
        label: "Retrieving relevant code…",
        tone: askActive ? "active" : answered && !askActive ? "done" : "idle",
      },
      {
        label: "Generating answer…",
        tone: askActive ? "active" : answered && !askActive ? "done" : "idle",
      },
      {
        label: "Ready",
        tone:
          !ingestLoading && !askLoading && resolvedRepoPath ? "done" : "idle",
      },
    ];
  }, [
    answer,
    askLoading,
    evidence.length,
    ingestLoading,
    resolvedRepoPath,
  ]);

  const emptyStatePhase = resolvedRepoPath ? "repo-ready" : "no-repo";

  const ingest = useCallback(async () => {
    setIngestError("");
    setIngestLoading(true);
    setFileCount(null);
    setIndexedChunks(null);
    setGraphNodes(null);
    setGraphEdges(null);
    setLastIngestedAt("");
    setResolvedRepoPath("");
    setAnswer("");
    setEvidence([]);
    setReasoningTrace([]);
    setCompletedAsk(false);
    try {
      const data = await postJson("/api/v1/ingestion/repositories", {
        local_repo_path: repoPath.trim(),
      });
      setResolvedRepoPath(data.repository_path || "");
      setFileCount(typeof data.file_count === "number" ? data.file_count : null);
      setIndexedChunks(
        typeof data.indexed_chunks === "number" ? data.indexed_chunks : null
      );
      setGraphNodes(typeof data.graph_nodes === "number" ? data.graph_nodes : null);
      setGraphEdges(typeof data.graph_edges === "number" ? data.graph_edges : null);
      setLastIngestedAt(
        new Date().toLocaleString(undefined, {
          dateStyle: "medium",
          timeStyle: "short",
        })
      );
    } catch (e) {
      setIngestError(e instanceof Error ? e.message : String(e));
    } finally {
      setIngestLoading(false);
    }
  }, [repoPath]);

  const ask = useCallback(async () => {
    const repoId = resolvedRepoPath || repoPath.trim();
    setAskError("");
    setAskLoading(true);
    setAnswer("");
    setEvidence([]);
    setReasoningTrace([]);
    try {
      const data = await postJson("/api/v1/qa/answer", {
        repository_id: repoId,
        question: question.trim(),
        top_k: 8,
      });
      setAnswer(data.answer || "");
      setEvidence(Array.isArray(data.evidence) ? data.evidence : []);
      setReasoningTrace(Array.isArray(data.reasoning_trace) ? data.reasoning_trace : []);
      setAnswerNonce((n) => n + 1);
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setAskError(msg);
      setAnswer(`Could not complete this request. ${msg}`);
      setEvidence([]);
      setReasoningTrace([]);
    } finally {
      setAskLoading(false);
      setCompletedAsk(true);
    }
  }, [question, repoPath, resolvedRepoPath]);

  const loadedName = resolvedRepoPath ? repoDisplayName(resolvedRepoPath) : "";
  const showMainContent = Boolean(
    askLoading ||
      evidence.length > 0 ||
      (typeof answer === "string" && answer.trim().length > 0) ||
      completedAsk
  );

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-slate-50 via-slate-100 to-slate-200/90 dark:from-slate-950 dark:via-slate-950 dark:to-slate-900">
      <AppHeader resolvedRepoPath={resolvedRepoPath} repoReady={Boolean(resolvedRepoPath)} />

      <div className="flex min-h-0 flex-1">
        <aside className="flex w-[320px] shrink-0 flex-col border-r border-slate-300/90 bg-slate-100 shadow-[inset_-1px_0_0_rgba(15,23,42,0.06)] dark:border-slate-800 dark:bg-slate-950 dark:shadow-[inset_-1px_0_0_rgba(255,255,255,0.04)]">
          <div className="flex-1 space-y-10 overflow-y-auto p-5">
            <SidebarSection>
              <RepoInputCard
                repoPath={repoPath}
                onRepoPathChange={setRepoPath}
                onIngest={ingest}
                loading={ingestLoading}
                disabledIngest={!repoPath.trim()}
                loadedBadgeName={loadedName}
              />
              {ingestError ? <InlineAlert>{ingestError}</InlineAlert> : null}
              <RepoSummaryCard
                resolvedRepoPath={resolvedRepoPath}
                fileCount={fileCount}
                indexedChunks={indexedChunks}
                graphSummary={graphSummary}
                lastUpdatedLabel={lastIngestedAt ? `Updated ${lastIngestedAt}` : ""}
              />
            </SidebarSection>

            <SidebarSection>
              <QuestionComposer
                question={question}
                onQuestionChange={setQuestion}
                onAsk={ask}
                askLoading={askLoading}
                disabledAsk={
                  !question.trim() || !(resolvedRepoPath || repoPath.trim())
                }
              />
              {askError ? <InlineAlert>{askError}</InlineAlert> : null}
            </SidebarSection>

            <SidebarSection>
              <ExamplePromptList onSelect={setQuestion} />
            </SidebarSection>

            <SidebarSection className="border-t border-slate-300 pt-8 dark:border-slate-800">
              <StatusPanel rows={statusRows} />
            </SidebarSection>
          </div>
        </aside>

        <main className="min-w-0 flex-1 overflow-y-auto">
          <div className="mx-auto max-w-3xl space-y-8 px-6 py-8 pb-20">
            {showMainContent ? (
              <>
                <AnswerCard
                  answer={answer}
                  chunkCount={evidence.length}
                  crossFileReasoning={crossFileReasoning}
                  isLoading={askLoading}
                />
                <EvidencePanel evidence={evidence} answerNonce={answerNonce} />
                <RelatedFilesCard
                  filePaths={relatedFiles}
                  fileToEvidenceDomId={fileToEvidenceDomId}
                />
                <RetrievalSummaryCard
                  evidence={evidence}
                  reasoningTrace={reasoningTrace}
                />
              </>
            ) : (
              <MainEmptyState phase={emptyStatePhase} />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
