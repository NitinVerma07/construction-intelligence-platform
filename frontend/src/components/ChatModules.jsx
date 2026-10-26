import { useState } from "react";
import { api } from "../api";
import { Badge, Bullets, Card, Field, SourceNotice, Status, useAction } from "./ui";

export function AssistantModule() {
  const [query, setQuery] = useState("What should I check before pouring the slab tomorrow?");
  const [context, setContext] = useState("");
  const [state, run] = useAction(api.assistant);

  const submit = (e) => {
    e.preventDefault();
    run({ query, site_context: context });
  };

  const r = state.data?.result;
  return (
    <>
      <Card title="Daily Site Assistant" subtitle="Ask for checklists, instructions or decisions for today's work.">
        <form onSubmit={submit}>
          <Field label="Your question"><textarea rows={3} required minLength={3} value={query} onChange={(e) => setQuery(e.target.value)} /></Field>
          <Field label="Site context (optional)" hint="Stage of work, weather, crew size, constraints">
            <textarea rows={2} value={context} onChange={(e) => setContext(e.target.value)} />
          </Field>
          <button className="primary" disabled={state.loading}>Ask assistant</button>
        </form>
        <Status state={state} />
      </Card>
      {r && (
        <Card title="Answer">
          <SourceNotice source={state.data.source} />
          <p><Badge level={r.priority === "high" ? "high" : r.priority === "normal" ? "medium" : "low"}>{r.priority} priority</Badge></p>
          <p>{r.answer}</p>
          <h3>Checklist</h3>
          <ul className="checklist">{r.checklist.map((c, i) => <li key={i}><label><input type="checkbox" /> {c}</label></li>)}</ul>
          {r.follow_ups.length > 0 && (<><h3>Worth clarifying</h3><Bullets items={r.follow_ups} /></>)}
        </Card>
      )}
    </>
  );
}

export function KnowledgeModule() {
  const [question, setQuestion] = useState("How long should concrete be cured?");
  const [state, run] = useAction(api.knowledge);

  const submit = (e) => {
    e.preventDefault();
    run({ question });
  };

  const r = state.data?.result;
  return (
    <>
      <Card title="Construction Knowledge Assistant" subtitle="Materials, methods, testing and code references.">
        <form onSubmit={submit}>
          <Field label="Your question"><textarea rows={3} required minLength={3} value={question} onChange={(e) => setQuestion(e.target.value)} /></Field>
          <button className="primary" disabled={state.loading}>Ask</button>
        </form>
        <Status state={state} />
      </Card>
      {r && (
        <Card title="Answer">
          <SourceNotice source={state.data.source} />
          <p>{r.answer}</p>
          {r.key_points.length > 0 && (<><h3>Key points</h3><Bullets items={r.key_points} /></>)}
          {r.standards.length > 0 && (<><h3>Standards</h3><Bullets items={r.standards} /></>)}
          <p className="muted">General guidance only; confirm design decisions with a licensed engineer.</p>
        </Card>
      )}
    </>
  );
}
