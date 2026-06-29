/** Project Lens dashboard — demo-idea */
export default function Dashboard() {
  const veredicto = "condicional";
  const score = 58.2;
  const areas = [
    { label: "trend", score: 50.0 },
    { label: "market", score: 60.0 },
    { label: "competition", score: 35.0 },
    { label: "financial", score: 73.33 },
    { label: "scalability", score: 80.0 },
    { label: "cost_mvp", score: 40.0 },
    { label: "risk", score: 55.0 },
  ];
  const siguiente = "Ejecutar plan_accion fase 1";
  return (
    <div style={ fontFamily: "system-ui", padding: 24, maxWidth: 720 }>
      <h1>Project Lens — demo-idea</h1>
      <p>Veredicto: <strong>{veredicto}</strong> · Score {score}</p>
      <ul>
        {areas.map((a) => (
          <li key={a.label}>{a.label}: {a.score}</li>
        ))}
      </ul>
      <p>Siguiente: {siguiente}</p>
    </div>
  );
}
