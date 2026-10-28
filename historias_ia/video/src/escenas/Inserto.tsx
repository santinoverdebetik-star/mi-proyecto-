import React from "react";
import { AbsoluteFill, interpolate, random, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FUENTE_TEXTO, FUENTE_TITULO } from "../estilo";

const FONDO = "radial-gradient(ellipse 75% 65% at 50% 40%, #2a3244 0%, #151a24 55%, #05060a 100%)";

/** Frase clave de la narracion en tipografia cinetica: las palabras entran una a una y la mas importante brilla en naranja. */
export const Frase: React.FC<{ texto: string; v?: number }> = ({ texto, v = 0 }) => {
  const f = useCurrentFrame(); const { fps, durationInFrames } = useVideoConfig();
  const palabras = texto.split(/\s+/).filter(Boolean);
  const clave = palabras.reduce((m, p, i) => (p.replace(/[^\p{L}\d$%]/gu, "").length > palabras[m].replace(/[^\p{L}\d$%]/gu, "").length ? i : m), 0);
  const t = interpolate(f, [0, durationInFrames], [0, 1]);
  const tam = palabras.length > 6 ? 108 : 132;
  return (
    <AbsoluteFill style={{ background: FONDO, justifyContent: "center", alignItems: "center" }}>
      <AbsoluteFill style={{ backgroundImage: "linear-gradient(rgba(53,217,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(53,217,255,0.05) 1px, transparent 1px)", backgroundSize: "90px 90px", transform: `translateY(${-t * 90}px)` }} />
      <div style={{ position: "absolute", left: 150, top: 300, width: 10, height: interpolate(f, [0, 14], [0, 480], { extrapolateRight: "clamp" }), background: v % 2 ? C.cian : C.naranja, boxShadow: `0 0 30px ${v % 2 ? C.cian : C.naranja}` }} />
      <div style={{ width: 1500, display: "flex", flexWrap: "wrap", gap: "10px 34px", justifyContent: "flex-start", transform: `scale(${1 + t * 0.04})` }}>
        {palabras.map((p, i) => {
          const e = spring({ frame: f - 4 - i * 4, fps, config: { damping: 14, stiffness: 170 } });
          const k = i === clave;
          return <span key={i} style={{ fontFamily: FUENTE_TITULO, fontSize: tam, lineHeight: 1.08, textTransform: "uppercase", letterSpacing: 2, color: k ? C.naranja : C.crema,
            opacity: e, transform: `translateY(${(1 - e) * 50}px) scale(${0.9 + 0.1 * e})`, textShadow: k ? `0 0 50px ${C.naranja}99` : "0 4px 24px #000a" }}>{p}</span>;
        })}
      </div>
    </AbsoluteFill>
  );
};

const LINEAS_TERMINAL = [
  ["$ escaneando red local...", C.cian], ["  > 192.168.1.1   router        [ok]", C.crema], ["  > 192.168.1.14  caja_tv       [respuesta rara]", C.naranja],
  ["  > 192.168.1.23  camara        [ok]", C.crema], ["$ analizando trafico...", C.cian], ["  ! conexion saliente desconocida", C.naranja],
  ["  ! el aparato obedece a otro", C.rojo], ["$ simulacion de laboratorio. no es un caso real.", C.gris],
];
/** Terminal que escribe sola: ilustracion generica (no muestra datos reales). */
export const Terminal: React.FC<{ v?: number }> = ({ v = 0 }) => {
  const f = useCurrentFrame();
  const lineas = [...LINEAS_TERMINAL.slice(v % 3, v % 3 + 5)];
  let n = f * 2.6 - 8; const filas: React.ReactNode[] = [];
  lineas.forEach(([txt, col], i) => { const k = Math.max(0, Math.min(txt.length, Math.floor(n))); n -= txt.length + 6;
    if (k > 0) filas.push(<div key={i} style={{ color: col as string, whiteSpace: "pre", textShadow: `0 0 12px ${col}66` }}>{txt.slice(0, k)}{k < txt.length || Math.floor(f / 8) % 2 ? <span style={{ background: col as string, color: "transparent" }}>_</span> : null}</div>); });
  return (
    <AbsoluteFill style={{ background: FONDO, justifyContent: "center", alignItems: "center" }}>
      <div style={{ width: 1400, height: 700, borderRadius: 22, background: "rgba(5,8,12,0.92)", border: "2px solid #35d9ff55", boxShadow: "0 0 80px #35d9ff22, 0 40px 120px #000c", overflow: "hidden", transform: `scale(${1 + f * 0.0006})` }}>
        <div style={{ height: 56, background: "#10151d", display: "flex", alignItems: "center", gap: 14, paddingLeft: 24 }}>
          {["#e0201b", "#ffb000", "#35d9ff"].map((c) => <div key={c} style={{ width: 16, height: 16, borderRadius: 8, background: c }} />)}
          <div style={{ marginLeft: 24, color: C.gris, fontFamily: FUENTE_TEXTO, fontSize: 22 }}>laboratorio — ilustracion</div>
        </div>
        <div style={{ padding: 40, fontFamily: "monospace", fontSize: 40, lineHeight: 1.6 }}>{filas}</div>
      </div>
    </AbsoluteFill>
  );
};

/** Cifra importante del guion, con cuenta ascendente y un arco que se llena. */
export const Dato: React.FC<{ valor: string; etiqueta?: string }> = ({ valor, etiqueta }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const m = valor.match(/^(\D*)(\d[\d.,]*)(.*)$/);
  const num = m ? parseFloat(m[2].replace(",", ".")) : NaN;
  const e = spring({ frame: f, fps, config: { damping: 20, stiffness: 60 } });
  const esAnio = m && /^(19|20)\d\d$/.test(m[2]);
  const mostrado = m ? (esAnio ? m[2] : (Number.isInteger(num) ? String(Math.round(num * e)) : (num * e).toFixed(1))) : valor;
  const arco = 2 * Math.PI * 340;
  return (
    <AbsoluteFill style={{ background: FONDO, justifyContent: "center", alignItems: "center" }}>
      <svg width={900} height={900} style={{ position: "absolute", transform: "rotate(-90deg)" }}>
        <circle cx={450} cy={450} r={340} stroke="#ffffff14" strokeWidth={10} fill="none" />
        <circle cx={450} cy={450} r={340} stroke={C.naranja} strokeWidth={10} fill="none" strokeLinecap="round" strokeDasharray={arco} strokeDashoffset={arco * (1 - 0.8 * e)} style={{ filter: `drop-shadow(0 0 16px ${C.naranja})` }} />
      </svg>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontFamily: FUENTE_TITULO, fontSize: 330, lineHeight: 1, color: C.crema, textShadow: `0 0 70px ${C.naranja}88` }}>{m ? m[1] : ""}{mostrado}<span style={{ color: C.naranja }}>{m ? m[3].trim() : ""}</span></div>
        {etiqueta && <div style={{ fontFamily: FUENTE_TEXTO, fontWeight: 800, fontSize: 40, letterSpacing: 6, color: C.cian, textTransform: "uppercase", marginTop: 70, maxWidth: 1100, opacity: interpolate(f, [10, 24], [0, 1], { extrapolateRight: "clamp" }) }}>{etiqueta}</div>}
      </div>
    </AbsoluteFill>
  );
};

/** Red de aparatos 2D: una chispa naranja se contagia de nodo en nodo por los enlaces (ilustracion del contagio). */
export const Flujo: React.FC<{ v?: number }> = ({ v = 0 }) => {
  const f = useCurrentFrame(); const { durationInFrames } = useVideoConfig();
  const N = 17;
  const nodos = Array.from({ length: N }, (_, i) => ({ x: 160 + random(`fx${v}_${i}`) * 1600, y: 140 + random(`fy${v}_${i}`) * 800 }));
  const enlaces: [number, number][] = [];
  nodos.forEach((a, i) => nodos.map((b, j) => ({ j, d: Math.hypot(a.x - b.x, a.y - b.y) })).filter((o) => o.j !== i).sort((p, q) => p.d - q.d).slice(0, 2).forEach((o) => { if (!enlaces.some(([x, y]) => (x === i && y === o.j) || (x === o.j && y === i))) enlaces.push([i, o.j]); }));
  const origen = v % N;                                                      // orden de contagio = distancia al nodo de origen
  const dist = nodos.map((n) => Math.hypot(n.x - nodos[origen].x, n.y - nodos[origen].y));
  const tInf = (i: number) => 8 + dist[i] / 14;
  const t = interpolate(f, [0, durationInFrames], [0, 1]);
  return (
    <AbsoluteFill style={{ background: FONDO }}>
      <svg width="100%" height="100%" viewBox="0 0 1920 1080" style={{ transform: `scale(${1.03 + t * 0.06})` }}>
        {enlaces.map(([a, b], k) => {
          const inf = f > Math.max(tInf(a), tInf(b));
          const p = ((f * 0.025 + k * 0.37) % 1);
          return <g key={k}>
            <line x1={nodos[a].x} y1={nodos[a].y} x2={nodos[b].x} y2={nodos[b].y} stroke={inf ? C.naranja : C.cian} strokeOpacity={inf ? 0.7 : 0.3} strokeWidth={3} />
            <circle cx={nodos[a].x + (nodos[b].x - nodos[a].x) * p} cy={nodos[a].y + (nodos[b].y - nodos[a].y) * p} r={7} fill={inf ? C.naranja : C.cian} style={{ filter: `drop-shadow(0 0 10px ${inf ? C.naranja : C.cian})` }} />
          </g>;
        })}
        {nodos.map((n, i) => { const inf = f > tInf(i); const r = 18 + (inf ? Math.sin(f / 5 + i) * 3 : 0);
          return <g key={i}><circle cx={n.x} cy={n.y} r={r + 16} fill={inf ? C.naranja : C.cian} opacity={0.12} /><circle cx={n.x} cy={n.y} r={r} fill={inf ? C.naranja : "#0d1a26"} stroke={inf ? "#ffd0a8" : C.cian} strokeWidth={4} style={{ filter: `drop-shadow(0 0 14px ${inf ? C.naranja : C.cian})` }} /></g>; })}
      </svg>
    </AbsoluteFill>
  );
};
