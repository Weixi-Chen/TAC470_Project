export function repoDisplayName(resolvedPath) {
  if (!resolvedPath) return "";
  const parts = resolvedPath.split("/").filter(Boolean);
  return parts[parts.length - 1] || resolvedPath;
}

export function fileNameFromPath(filePath) {
  if (!filePath) return "";
  const parts = filePath.split("/").filter(Boolean);
  return parts[parts.length - 1] || filePath;
}

export function uniqueRelatedFiles(evidence) {
  if (!Array.isArray(evidence)) return [];
  const set = new Set();
  for (const e of evidence) {
    if (e && e.file_path) set.add(e.file_path);
  }
  return [...set].sort();
}

export function evidenceDomId(chunkId) {
  return `evidence-${chunkId}`.replace(/[^a-zA-Z0-9-_]/g, "-");
}

/** First evidence DOM id per file path (for Related Files scroll targets). */
export function buildFileToEvidenceDomId(evidence) {
  const map = new Map();
  for (const e of evidence) {
    if (!e?.file_path || map.has(e.file_path)) continue;
    map.set(e.file_path, evidenceDomId(e.chunk_id));
  }
  return map;
}
