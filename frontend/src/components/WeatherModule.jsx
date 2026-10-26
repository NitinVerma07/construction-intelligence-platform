import { useState } from "react";
import { api } from "../api";
import { Badge, Bullets, Card, Field, SourceNotice, Status, useAction } from "./ui";

export default function WeatherModule() {
  const [city, setCity] = useState("Indore");
  const [activity, setActivity] = useState("Slab concreting");
  const [state, run] = useAction(api.weather);

  const submit = (e) => {
    e.preventDefault();
    run({ city, activity });
  };

  const r = state.data?.result;
  return (
    <>
      <Card title="Weather-Aware Advisory" subtitle="Live conditions and a 3-day outlook turned into site guidance.">
        <form onSubmit={submit} className="grid">
          <Field label="City"><input required value={city} onChange={(e) => setCity(e.target.value)} /></Field>
          <Field label="Planned activity"><input value={activity} onChange={(e) => setActivity(e.target.value)} /></Field>
          <button className="primary" disabled={state.loading}>Get advisory</button>
        </form>
        <Status state={state} />
      </Card>

      {r && (
        <>
          <Card title={`Weather - ${r.weather.city}`}>
            <p className="big">{r.weather.temperature_c} &deg;C</p>
            <p className="muted">
              Humidity {r.weather.humidity_pct}% | Wind {r.weather.wind_kmh} km/h | Rain now {r.weather.precipitation_mm} mm
            </p>
            <table>
              <thead><tr><th>Date</th><th>Max</th><th>Min</th><th>Rain</th><th>Wind</th></tr></thead>
              <tbody>
                {r.weather.forecast.map((d) => (
                  <tr key={d.date}>
                    <td>{d.date}</td><td>{d.temp_max_c}&deg;</td><td>{d.temp_min_c}&deg;</td>
                    <td>{d.rain_mm} mm</td><td>{d.wind_max_kmh} km/h</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
          <Card title="Advisory">
            <SourceNotice source={state.data.source} />
            <p><Badge level={r.advisory.work_suitability} /> {r.advisory.summary}</p>
            <div className="two-col">
              <div><h3>Recommendations</h3><Bullets items={r.advisory.recommendations} /></div>
              <div><h3>Precautions</h3><Bullets items={r.advisory.precautions} /></div>
            </div>
          </Card>
        </>
      )}
    </>
  );
}
