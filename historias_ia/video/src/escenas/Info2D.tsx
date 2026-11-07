import React, { useLayoutEffect, useMemo, useRef } from "react";
import { AbsoluteFill, interpolate, random, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { FUENTE_DIN, FUENTE_TERMINAL } from "../estilo";
import { estilo } from "../estilos";
import mapa from "../../public/mapa.json";

/* INFOGRAFIAS 2D sobre negro, como las del video de referencia 3: numeros enormes blancos sobre lluvia de datos, mapa de puntos con contador, casa en linea cian,
   puerta abierta con bicho, cuadricula de cajitas con contador. */
const FONDO = "radial-gradient(ellipse 80% 70% at 50% 45%, #0d141c 0%, #04070a 70%, #010203 100%)";

const Lluvia: React.FC<{ a: string; v?: number }> = ({ a, v = 0 }) => {
  const f = useCurrentFrame();
  return (<AbsoluteFill style={{ opacity: 0.16, overflow: "hidden" }}>
    {Array.from({ length: 56 }, (_, c) => { const y0 = ((f * (2 + random(`d${v}${c}`) * 5) + random(`o${v}${c}`) * 1400) % 1500) - 300;
      return <div key={c} style={{ position: "absolute", left: 14 + c * 34, top: y0 - 600, fontFamily: FUENTE_TERMINAL, fontSize: 26, lineHeight: "30px", whiteSpace: "pre", color: a }}>{Array.from({ length: 20 }, (_, k) => "0123456789ABCDEF"[Math.floor(random(`s${v}${c}${k}${Math.floor(f / 8)}`) * 16)]).join("\n")}</div>; })}
  </AbsoluteFill>);
};

/** Cifra enorme blanca sobre lluvia de datos, con cuenta ascendente y una frase corta debajo (como "18,788,000,000"). */
export const Numero: React.FC<{ valor: string; etiqueta?: string; est?: number }> = ({ valor, etiqueta, est = 2 }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig(); const E = estilo(est);
  const m = valor.match(/^(\D*)(\d[\d.,]*)(.*)$/); const raw = m ? m[2].replace(/[.,](?=\d{3}(\D|$))/g, "") : ""; const num = parseFloat(raw);
  const e = spring({ frame: f, fps, config: { damping: 22, stiffness: 50 } }); const esAnio = m && /^(19|20)\d\d$/.test(m[2]);
  const txt = m ? (esAnio || isNaN(num) ? m[2] : Math.round(num * e).toLocaleString("en-US")) : valor;
  const tam = txt.length > 9 ? 190 : txt.length > 6 ? 240 : 300;
  return (<AbsoluteFill style={{ background: FONDO, justifyContent: "center", alignItems: "center" }}>
    <Lluvia a={E.a} v={txt.length} />
    <div style={{ textAlign: "center", opacity: interpolate(f, [0, 8], [0, 1], { extrapolateRight: "clamp" }) }}>
      <div style={{ fontFamily: FUENTE_DIN, fontWeight: 600, fontSize: tam, letterSpacing: 4, color: "#f4f4f2", textShadow: `0 0 40px ${E.a}55`, lineHeight: 1 }}>{m ? m[1] : ""}{txt}<span style={{ color: E.a }}>{m ? m[3].trim() : ""}</span></div>
      {etiqueta && <div style={{ fontFamily: FUENTE_DIN, fontWeight: 500, fontSize: 34, letterSpacing: 12, color: "#9aa7b2", marginTop: 26, textTransform: "uppercase", opacity: interpolate(f, [14, 28], [0, 1], { extrapolateRight: "clamp" }) }}>{etiqueta}</div>}
    </div></AbsoluteFill>);
};

/** Mapa de puntos del mundo (puntos cian que titilan y se encienden por oleadas) con contador opcional. */
export const MapaPuntos: React.FC<{ valor?: string; etiqueta?: string; est?: number }> = ({ valor, etiqueta, est = 2 }) => {
  const ref = useRef<HTMLCanvasElement>(null); const f = useCurrentFrame(); const E = estilo(est);
  const puntos = useMemo(() => {
    const W = 1600, H = 800, cv = document.createElement("canvas"); cv.width = W; cv.height = H; const x = cv.getContext("2d")!; x.fillStyle = "#fff";
    for (const poly of mapa as number[][][]) { x.beginPath(); poly.forEach(([lo, la], i) => { const px = (lo + 180) / 360 * W, py = (84 - la) / 150 * H; i ? x.lineTo(px, py) : x.moveTo(px, py); }); x.closePath(); x.fill(); }
    const d = x.getImageData(0, 0, W, H).data; const out: [number, number, number][] = [];
    for (let py = 6; py < H; py += 11) for (let px = 6; px < W; px += 11) if (d[(py * W + px) * 4] > 128) out.push([px, py, random(`p${px}_${py}`)]);
    return out;
  }, []);
  useLayoutEffect(() => {
    const c = ref.current!; const x = c.getContext("2d")!; x.clearRect(0, 0, c.width, c.height);
    const oleada = f * 22;
    for (const [px, py, r] of puntos) { const t = oleada - px * 0.6 - py * 0.3 + r * 200; const on = Math.max(0, Math.min(1, t / 160)); const tw = 0.6 + 0.4 * Math.sin(f / 6 + r * 30);
      x.fillStyle = r > 0.93 && on > 0.5 ? "#ff6a2a" : E.a; x.globalAlpha = 0.12 + on * tw * (r > 0.93 ? 1 : 0.85); x.beginPath(); x.arc(px, py, r > 0.93 ? 4.2 : 2.6, 0, 7); x.fill(); }
    x.globalAlpha = 1;
  });
  const m = valor?.match(/^(\D*)(\d[\d.,]*)(.*)$/); const num = m ? parseFloat(m[2].replace(/[.,](?=\d{3}(\D|$))/g, "")) : NaN; const k = Math.min(1, f / 70);
  return (<AbsoluteFill style={{ background: FONDO, justifyContent: "center", alignItems: "center" }}>
    <canvas ref={ref} width={1600} height={800} style={{ width: 1600, height: 800, marginTop: valor ? -70 : 0, transform: `scale(${1 + f * 0.0004})` }} />
    {valor && <div style={{ position: "absolute", bottom: 150, width: "100%", textAlign: "center" }}>
      <div style={{ fontFamily: FUENTE_DIN, fontWeight: 600, fontSize: 118, color: "#f4f4f2", letterSpacing: 3 }}>{m && !isNaN(num) ? Math.round(num * k).toLocaleString("en-US") : valor}<span style={{ color: E.a }}>{m ? m[3].trim() : ""}</span></div>
      {etiqueta && <div style={{ fontFamily: FUENTE_DIN, fontWeight: 500, fontSize: 28, letterSpacing: 10, color: "#7f8c98", marginTop: 4, textTransform: "uppercase" }}>{etiqueta}</div>}
    </div>}
  </AbsoluteFill>);
};

const L = (a: string) => ({ stroke: a, strokeWidth: 5, fill: "none", strokeLinejoin: "round" as const, strokeLinecap: "round" as const });
/** Casa en linea cian con sus aparatos conectados por lineas que se dibujan; opcionalmente un bicho que entra. */
export const Casa: React.FC<{ est?: number; infectada?: boolean }> = ({ est = 2, infectada = true }) => {
  const f = useCurrentFrame(); const E = estilo(est); const dib = (d: number, len = 600) => ({ strokeDasharray: len, strokeDashoffset: len * (1 - Math.min(1, Math.max(0, (f - d) / 22))) });
  const bug = Math.min(1, Math.max(0, (f - 50) / 40));
  return (<AbsoluteFill style={{ background: FONDO, justifyContent: "center", alignItems: "center" }}>
    <svg width={1500} height={900} viewBox="0 0 1500 900" style={{ transform: `scale(${1 + f * 0.0005})` }}>
      <g {...L(E.a)}>
        <path d="M420 430 L750 150 L1080 430 M470 400 V760 H1030 V400" {...dib(0, 1600)} /><rect x={700} y={560} width={110} height={200} {...dib(8)} /><rect x={560} y={500} width={90} height={90} {...dib(10)} /><rect x={870} y={500} width={90} height={90} {...dib(12)} />
        <rect x={210} y={560} width={150} height={100} {...dib(18)} /><path d="M180 660 H390" {...dib(20)} />
        <rect x={1180} y={230} width={90} height={160} rx={12} {...dib(22)} /><rect x={1130} y={600} width={200} height={130} {...dib(26)} />
        <path d="M360 610 H560 M1080 640 H1130 M1090 430 L1180 330 M750 360 V150" {...dib(30)} strokeDasharray="14 12" />
      </g>
      {[[620, 545], [915, 545], [285, 610], [1230, 310], [1230, 665]].map(([x, y], i) => <circle key={i} cx={x} cy={y} r={9} fill={infectada && bug * 5 > i + 1 ? "#ff6a2a" : E.a} opacity={0.9} />)}
      {infectada && <g transform={`translate(${200 + bug * 520} ${700 - bug * 20})`} opacity={bug > 0 ? 1 : 0}><ellipse rx={20} ry={26} fill="#ff6a2a" /><circle cy={-30} r={10} fill="#ff6a2a" />{[-1, 1].map((l) => [-14, 0, 14].map((y) => <path key={`${l}${y}`} d={`M${l * 16} ${y} l${l * 14} ${y * 0.4 - 6}`} stroke="#ff6a2a" strokeWidth={4} />))}</g>}
    </svg></AbsoluteFill>);
};

/** Puerta abierta con un bicho en el umbral (como "cualquiera podia entrar"). */
export const Puerta: React.FC<{ est?: number }> = ({ est = 2 }) => {
  const f = useCurrentFrame(); const E = estilo(est); const ab = Math.min(1, f / 28); const dib = (d: number, len = 900) => ({ strokeDasharray: len, strokeDashoffset: len * (1 - Math.min(1, Math.max(0, (f - d) / 20))) });
  return (<AbsoluteFill style={{ background: FONDO, justifyContent: "center", alignItems: "center" }}>
    <svg width={1100} height={800} viewBox="0 0 1100 800" style={{ transform: `scale(${1 + f * 0.0006})` }}>
      <g {...L(E.a)}><path d="M300 700 V160 H650 V700" {...dib(0)} /><path d="M100 700 H1000" {...dib(6, 1000)} />
        <path d={`M650 160 L${650 + 190 * ab} ${180 - 14 * ab} V${660 + 14 * ab} L650 700 Z`} {...dib(10)} /><circle cx={650 + 150 * ab} cy={430} r={9} fill={E.a} /></g>
      <g transform={`translate(${440 + Math.sin(f / 7) * 8} 660)`} opacity={f > 20 ? 1 : 0}><ellipse rx={26} ry={34} fill="#ff6a2a" /><circle cy={-40} r={14} fill="#ff6a2a" />{[-1, 1].map((l) => [-20, 0, 20].map((y) => <path key={`${l}${y}`} d={`M${l * 20} ${y} l${l * 18} ${y * 0.4 - 8}`} stroke="#ff6a2a" strokeWidth={5} />))}</g>
    </svg></AbsoluteFill>);
};

/** Cuadricula de cajitas negras con LED que se encienden una a una y un contador arriba. */
export const Grilla: React.FC<{ n?: number; etiqueta?: string; est?: number }> = ({ n = 15, etiqueta, est = 2 }) => {
  const f = useCurrentFrame(); const E = estilo(est); const cols = n > 30 ? 12 : 5; const filas = Math.ceil(n / cols); const vistos = Math.min(n, Math.floor(f / 3));
  return (<AbsoluteFill style={{ background: FONDO, justifyContent: "center", alignItems: "center" }}>
    <div style={{ position: "absolute", top: 120, width: "100%", textAlign: "center" }}>
      <div style={{ fontFamily: FUENTE_DIN, fontWeight: 600, fontSize: 130, color: "#f4f4f2", letterSpacing: 3 }}>{vistos.toLocaleString("en-US")}</div>
      {etiqueta && <div style={{ fontFamily: FUENTE_DIN, fontWeight: 500, fontSize: 28, letterSpacing: 10, color: "#7f8c98", textTransform: "uppercase" }}>{etiqueta}</div>}</div>
    <div style={{ display: "grid", gridTemplateColumns: `repeat(${cols}, 150px)`, gap: 26, marginTop: 190 }}>
      {Array.from({ length: n }, (_, i) => { const on = i < vistos; const lat = on && Math.floor(f / 18 + i) % 4 !== 0;
        return <div key={i} style={{ width: 150, height: 54, borderRadius: 8, background: "linear-gradient(#25292f,#0d0f12)", border: "2px solid #30353c", opacity: on ? 1 : 0.18, position: "relative", boxShadow: on ? `0 0 24px ${E.a}22` : "none" }}>
          <div style={{ position: "absolute", left: 16, top: 22, width: 10, height: 10, borderRadius: 5, background: lat ? E.a : "#0a2a2a", boxShadow: lat ? `0 0 14px ${E.a}` : "none" }} /></div>; })}
    </div></AbsoluteFill>);
};
