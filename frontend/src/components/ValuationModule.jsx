import { useState } from "react";
import { api } from "../api";
import { Badge, Card, Field, SourceNotice, Status, inr, useAction } from "./ui";

export default function ValuationModule() {
  const [f, setF] = useState({
    city: "Indore", locality: "", property_type: "apartment", area_sqft: 1200,
    bedrooms: 2, age_years: 0, quality: "standard", amenities: "",
  });
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const [state, run] = useAction(api.valuation);

  const submit = (e) => {
    e.preventDefault();
    run({
      ...f,
      area_sqft: Number(f.area_sqft),
      bedrooms: Number(f.bedrooms),
      age_years: Number(f.age_years),
      amenities: f.amenities.split(",").map((a) => a.trim()).filter(Boolean),
    });
  };

  const r = state.data?.result;
  return (
    <>
      <Card title="Real Estate Valuation" subtitle="Indicative market value - not a certified valuation.">
        <form onSubmit={submit} className="grid">
          <Field label="City"><input required value={f.city} onChange={set("city")} /></Field>
          <Field label="Locality"><input value={f.locality} onChange={set("locality")} /></Field>
          <Field label="Property type">
            <select value={f.property_type} onChange={set("property_type")}>
              <option value="apartment">Apartment</option>
              <option value="independent_house">Independent house</option>
              <option value="villa">Villa</option>
              <option value="plot">Plot</option>
              <option value="commercial">Commercial</option>
            </select>
          </Field>
          <Field label="Area (sq ft)"><input type="number" min="101" required value={f.area_sqft} onChange={set("area_sqft")} /></Field>
          <Field label="Bedrooms"><input type="number" min="0" value={f.bedrooms} onChange={set("bedrooms")} /></Field>
          <Field label="Age (years)"><input type="number" min="0" value={f.age_years} onChange={set("age_years")} /></Field>
          <Field label="Construction quality">
            <select value={f.quality} onChange={set("quality")}>
              <option value="basic">Basic</option>
              <option value="standard">Standard</option>
              <option value="premium">Premium</option>
              <option value="luxury">Luxury</option>
            </select>
          </Field>
          <Field label="Amenities" hint="Comma separated, e.g. parking, lift, gym">
            <input value={f.amenities} onChange={set("amenities")} />
          </Field>
          <button className="primary" disabled={state.loading}>Estimate value</button>
        </form>
        <Status state={state} />
      </Card>

      {r && (
        <Card title="Estimate">
          <SourceNotice source={state.data.source} />
          <p className="big">{inr(r.estimated_value_inr)}</p>
          <p className="muted">
            Range {inr(r.range_low_inr)} - {inr(r.range_high_inr)} | {inr(r.price_per_sqft_inr)}/sq ft |{" "}
            Confidence <Badge level={r.confidence === "high" ? "low" : r.confidence === "medium" ? "medium" : "high"}>{r.confidence}</Badge>
          </p>
          <p>{r.summary}</p>
          <h3>Value drivers</h3>
          {r.factors.map((x, i) => (
            <div className="row" key={i}>
              <Badge level={x.impact} />
              <div><strong>{x.name}</strong><p className="muted">{x.note}</p></div>
            </div>
          ))}
        </Card>
      )}
    </>
  );
}
