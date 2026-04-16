export function apiBase() {
  const env = import.meta.env.VITE_API_BASE_URL;
  if (env && String(env).trim()) {
    return String(env).replace(/\/$/, "");
  }
  return "";
}

export async function postJson(path, body) {
  const base = apiBase();
  const url = `${base}${path}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    throw new Error(text || `HTTP ${res.status}`);
  }
  if (!res.ok) {
    const detail =
      data && typeof data.detail === "string"
        ? data.detail
        : data && Array.isArray(data.detail)
          ? data.detail.map((d) => d.msg || JSON.stringify(d)).join("\n")
          : text || res.statusText;
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return data;
}
