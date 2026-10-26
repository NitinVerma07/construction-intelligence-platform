import { useState } from "react";
import { api } from "../api";
import { Badge, Bullets, Card, Field, ImagePicker, SourceNotice, Status, useAction } from "./ui";

function ImageModule({ title, subtitle, action, render }) {
  const [file, setFile] = useState(null);
  const [notes, setNotes] = useState("");
  const [state, run] = useAction(action);

  return (
    <>
      <Card title={title} subtitle={subtitle}>
        <ImagePicker file={file} onChange={setFile} />
        <Field label="Notes (optional)" hint="Location, crack width, how long it has been there, etc.">
          <textarea rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />
        </Field>
        <button className="primary" disabled={!file || state.loading} onClick={() => run(file, notes)}>
          Analyse image
        </button>
        <Status state={state} />
      </Card>
      {state.data && (
        <Card title="Result">
          <SourceNotice source={state.data.source} />
          {render(state.data.result)}
        </Card>
      )}
    </>
  );
}

export function SafetyModule() {
  return (
    <ImageModule
      title="Site Safety Monitoring"
      subtitle="Upload a site photo to check PPE, hazards and housekeeping."
      action={api.safety}
      render={(r) => (
        <>
          <p>
            <Badge level={r.risk_level} /> <strong>Risk score {r.risk_score}/100</strong>
          </p>
          <p>{r.summary}</p>
          <h3>Findings</h3>
          {r.findings.length === 0 && <p className="muted">No hazards reported.</p>}
          {r.findings.map((f, i) => (
            <div className="row" key={i}>
              <Badge level={f.severity} />
              <div>
                <strong>{f.issue}</strong>
                <p className="muted">{f.recommendation}</p>
              </div>
            </div>
          ))}
          <div className="two-col">
            <div>
              <h3>PPE detected</h3>
              <Bullets items={r.ppe_detected} />
            </div>
            <div>
              <h3>PPE missing</h3>
              <Bullets items={r.ppe_missing} />
            </div>
          </div>
        </>
      )}
    />
  );
}

export function CrackModule() {
  return (
    <ImageModule
      title="Crack Detection & Analysis"
      subtitle="Upload a photo of a wall, slab, column or beam."
      action={api.cracks}
      render={(r) => (
        <>
          <p>
            <Badge level={r.severity} /> <Badge level={r.urgency}>{r.urgency.replace("_", " ")}</Badge>{" "}
            <strong>{r.crack_type}</strong>
          </p>
          <p>
            Structural risk: <strong>{r.structural_risk ? "Yes - consult an engineer" : "Not indicated"}</strong> | Confidence{" "}
            {Math.round(r.confidence * 100)}%
          </p>
          <p>{r.summary}</p>
          <div className="two-col">
            <div>
              <h3>Probable causes</h3>
              <Bullets items={r.probable_causes} />
            </div>
            <div>
              <h3>Recommended actions</h3>
              <Bullets items={r.recommended_actions} />
            </div>
          </div>
        </>
      )}
    />
  );
}
