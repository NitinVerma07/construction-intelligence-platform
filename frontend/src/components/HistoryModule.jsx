import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import { Badge, Card } from "./ui";

export default function HistoryModule() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState(null);
  const [open, setOpen] = useState(null);

  const load = useCallback(() => {
    api.history().then(setItems).catch((e) => setError(e.message));
  }, []);
  useEffect(load, [load]);

  const remove = async (id) => {
    try {
      await api.deleteHistory(id);
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <Card title="Analysis History" subtitle="Every analysis is saved to the local SQLite database.">
      {error && <p className="status error">{error}</p>}
      {!error && items.length === 0 && <p className="muted">Nothing here yet. Run an analysis first.</p>}
      {items.map((it) => (
        <div className="history-item" key={it.id}>
          <div className="row">
            <Badge level="neutral">{it.module}</Badge>
            <div className="grow">
              <p>{it.summary}</p>
              <p className="muted">{new Date(it.created_at + "Z").toLocaleString()} | {it.source}</p>
            </div>
            <button onClick={() => setOpen(open === it.id ? null : it.id)}>{open === it.id ? "Hide" : "JSON"}</button>
            <button className="danger" onClick={() => remove(it.id)}>Delete</button>
          </div>
          {open === it.id && <pre>{JSON.stringify(it.result, null, 2)}</pre>}
        </div>
      ))}
    </Card>
  );
}
