const BASE = import.meta.env.VITE_API_URL || "/api";

function describeError(body, fallback) {
  if (!body || body.detail === undefined) return fallback;
  if (typeof body.detail === "string") return body.detail;
  if (Array.isArray(body.detail)) {
    return body.detail.map((d) => `${(d.loc || []).slice(1).join(".")}: ${d.msg}`).join("; ");
  }
  return fallback;
}

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${BASE}${path}`, options);
  } catch {
    throw new Error("Cannot reach the backend. Is it running on port 8000?");
  }
  if (!res.ok) {
    let body = null;
    try {
      body = await res.json();
    } catch {
      /* non-JSON error body */
    }
    throw new Error(describeError(body, res.statusText || `Request failed (${res.status})`));
  }
  return res.status === 204 ? null : res.json();
}

const post = (path, body) =>
  request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

const upload = (path, file, notes) => {
  const form = new FormData();
  form.append("file", file);
  form.append("notes", notes || "");
  return request(path, { method: "POST", body: form });
};

export const api = {
  health: () => request("/health"),
  safety: (file, notes) => upload("/safety/analyze", file, notes),
  cracks: (file, notes) => upload("/cracks/analyze", file, notes),
  valuation: (body) => post("/valuation/estimate", body),
  planning: (body) => post("/planning/generate", body),
  assistant: (body) => post("/assistant/ask", body),
  knowledge: (body) => post("/knowledge/ask", body),
  weather: (body) => post("/weather/advisory", body),
  history: (module) => request(`/history${module ? `?module=${module}` : ""}`),
  deleteHistory: (id) => request(`/history/${id}`, { method: "DELETE" }),
};
