import { useEffect, useMemo, useState } from "react";

/** Wraps an async API call and tracks loading / error / data. */
export function useAction(fn) {
  const [state, setState] = useState({ loading: false, error: null, data: null });
  const run = async (...args) => {
    setState({ loading: true, error: null, data: null });
    try {
      const data = await fn(...args);
      setState({ loading: false, error: null, data });
    } catch (e) {
      setState({ loading: false, error: e.message, data: null });
    }
  };
  return [state, run];
}

export const inr = (n) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);

export const num = (n) => new Intl.NumberFormat("en-IN").format(n);

export function Card({ title, subtitle, children }) {
  return (
    <section className="card">
      {title && <h2>{title}</h2>}
      {subtitle && <p className="muted">{subtitle}</p>}
      {children}
    </section>
  );
}

export function Field({ label, hint, children }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
      {hint && <small>{hint}</small>}
    </label>
  );
}

export function Badge({ level, children }) {
  return <span className={`badge lvl-${level}`}>{children ?? level}</span>;
}

export function Bullets({ items, empty = "None" }) {
  if (!items || items.length === 0) return <p className="muted">{empty}</p>;
  return (
    <ul className="bullets">
      {items.map((t, i) => (
        <li key={i}>{t}</li>
      ))}
    </ul>
  );
}

export function Status({ state }) {
  if (state.loading) return <p className="status loading">Analysing... this can take 10-20 seconds.</p>;
  if (state.error) return <p className="status error">{state.error}</p>;
  return null;
}

/** Shown when the backend answered without calling the live LLM. */
export function SourceNotice({ source }) {
  if (!source || source === "llm") return null;
  return (
    <p className="notice">
      {source === "mock"
        ? "Demo output: no API key configured, so this uses built-in rules. Add ANTHROPIC_API_KEY to .env for live AI analysis."
        : "The AI service did not respond, so rule-based output is shown instead."}
    </p>
  );
}

export function ImagePicker({ file, onChange }) {
  const preview = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);
  useEffect(() => () => preview && URL.revokeObjectURL(preview), [preview]);
  return (
    <div className="picker">
      <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={(e) => onChange(e.target.files[0] || null)} />
      {preview && <img src={preview} alt="Selected upload preview" />}
    </div>
  );
}

export const toNumber = (v) => (v === "" || v === null || v === undefined ? null : Number(v));
