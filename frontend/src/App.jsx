import { useEffect, useState } from "react";
import { api } from "./api";
import { SafetyModule, CrackModule } from "./components/ImageModules";
import ValuationModule from "./components/ValuationModule";
import PlanningModule from "./components/PlanningModule";
import WeatherModule from "./components/WeatherModule";
import { AssistantModule, KnowledgeModule } from "./components/ChatModules";
import HistoryModule from "./components/HistoryModule";

const TABS = [
  { id: "safety", label: "Site Safety", view: SafetyModule },
  { id: "cracks", label: "Crack Analysis", view: CrackModule },
  { id: "valuation", label: "Valuation", view: ValuationModule },
  { id: "planning", label: "Project Planning", view: PlanningModule },
  { id: "weather", label: "Weather Advisory", view: WeatherModule },
  { id: "assistant", label: "Site Assistant", view: AssistantModule },
  { id: "knowledge", label: "Knowledge", view: KnowledgeModule },
  { id: "history", label: "History", view: HistoryModule },
];

export default function App() {
  const [tab, setTab] = useState("safety");
  const [health, setHealth] = useState(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth({ status: "offline" }));
  }, []);

  const View = TABS.find((t) => t.id === tab).view;

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>Construction<br />Intelligence</h1>
        <nav>
          {TABS.map((t) => (
            <button key={t.id} className={t.id === tab ? "active" : ""} onClick={() => setTab(t.id)}>
              {t.label}
            </button>
          ))}
        </nav>
        <p className="health">
          {health === null && "Connecting..."}
          {health?.status === "offline" && "Backend offline"}
          {health?.status === "ok" && (health.llm_mode === "live" ? `AI live (${health.model})` : "Demo mode (no API key)")}
        </p>
      </aside>
      <main className="content">
        <View />
      </main>
    </div>
  );
}
