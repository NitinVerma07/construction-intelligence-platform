import { useState } from "react";
import { api } from "../api";
import { Bullets, Card, Field, SourceNotice, Status, inr, num, toNumber, useAction } from "./ui";

export default function PlanningModule() {
  const [f, setF] = useState({
    project_type: "residential", location: "Indore", built_up_area_sqft: 1500,
    floors: 2, budget_inr: "", duration_months: "",
  });
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const [state, run] = useAction(api.planning);

  const submit = (e) => {
    e.preventDefault();
    run({
      ...f,
      built_up_area_sqft: Number(f.built_up_area_sqft),
      floors: Number(f.floors),
      budget_inr: toNumber(f.budget_inr),
      duration_months: toNumber(f.duration_months),
    });
  };

  const p = state.data?.result;
  return (
    <>
      <Card title="Construction Planning" subtitle="Phase-wise schedule, material estimate and cost breakdown.">
        <form onSubmit={submit} className="grid">
          <Field label="Project type">
            <select value={f.project_type} onChange={set("project_type")}>
              <option value="residential">Residential</option>
              <option value="commercial">Commercial</option>
              <option value="industrial">Industrial</option>
              <option value="infrastructure">Infrastructure</option>
            </select>
          </Field>
          <Field label="Location"><input required value={f.location} onChange={set("location")} /></Field>
          <Field label="Built-up area (sq ft)"><input type="number" min="101" required value={f.built_up_area_sqft} onChange={set("built_up_area_sqft")} /></Field>
          <Field label="Floors"><input type="number" min="1" value={f.floors} onChange={set("floors")} /></Field>
          <Field label="Budget (INR)" hint="Optional"><input type="number" min="1" value={f.budget_inr} onChange={set("budget_inr")} /></Field>
          <Field label="Target duration (months)" hint="Optional"><input type="number" min="1" value={f.duration_months} onChange={set("duration_months")} /></Field>
          <button className="primary" disabled={state.loading}>Generate plan</button>
        </form>
        <Status state={state} />
      </Card>

      {p && (
        <>
          <Card title="Plan overview">
            <SourceNotice source={state.data.source} />
            <p className="big">{inr(p.total_estimated_cost_inr)}</p>
            <p className="muted">{p.total_duration_weeks} weeks (about {(p.total_duration_weeks / 4.345).toFixed(1)} months)</p>
            <p>{p.summary}</p>
          </Card>
          <Card title="Phases">
            {p.phases.map((ph, i) => (
              <div className="phase" key={i}>
                <h3>{i + 1}. {ph.name} <span className="muted">- {ph.duration_weeks} wks</span></h3>
                <Bullets items={ph.tasks} />
              </div>
            ))}
          </Card>
          <Card title="Materials & cost">
            <div className="two-col">
              <table>
                <thead><tr><th>Material</th><th>Quantity</th></tr></thead>
                <tbody>
                  {p.materials.map((m, i) => (
                    <tr key={i}><td>{m.material}</td><td>{num(m.quantity)} {m.unit}</td></tr>
                  ))}
                </tbody>
              </table>
              <table>
                <thead><tr><th>Category</th><th>%</th><th>Amount</th></tr></thead>
                <tbody>
                  {p.cost_breakdown.map((c, i) => (
                    <tr key={i}><td>{c.category}</td><td>{c.percent}</td><td>{inr(c.amount_inr)}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
            <h3>Key risks</h3>
            <Bullets items={p.risks} />
          </Card>
        </>
      )}
    </>
  );
}
