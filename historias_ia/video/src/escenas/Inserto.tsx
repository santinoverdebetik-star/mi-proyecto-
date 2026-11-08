import React from "react";
import { AbsoluteFill, Img, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FUENTE_TERMINAL, FUENTE_TEXTO, FUENTE_TITULO } from "../estilo";
import { estilo } from "../estilos";

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

/** Cifra importante del guion sobre una FOTO REAL con gradacion; la cifra ocupa solo una esquina (nunca toda la escena). */
export const Dato: React.FC<{ valor: string; etiqueta?: string; fondo?: string; est?: number; lay?: number }> = ({ valor, etiqueta, fondo, est = 0, lay = 0 }) => {
  const E = estilo(est);
  const f = useCurrentFrame(); const { fps, durationInFrames: D } = useVideoConfig();
  const m = valor.match(/^(\D*)(\d[\d.,]*)(.*)$/);
  const num = m ? parseFloat(m[2].replace(",", ".")) : NaN;
  const e = spring({ frame: f, fps, config: { damping: 20, stiffness: 60 } });
  const esAnio = m && /^(19|20)\d\d$/.test(m[2]);
  const mostrado = m ? (esAnio ? m[2] : (Number.isInteger(num) ? String(Math.round(num * e)) : (num * e).toFixed(1))) : valor;
  const t = interpolate(f, [0, D], [0, 1], { extrapolateRight: "clamp" });
  const arco = 2 * Math.PI * 130;
  return (
    <AbsoluteFill style={{ background: "#07090d", overflow: "hidden" }}>
      {fondo ? <Img src={staticFile(fondo)} style={{ position: "absolute", width: "100%", height: "100%", objectFit: "cover", transform: `scale(${1.06 + 0.08 * t})`, filter: E.filtro }} /> : <AbsoluteFill style={{ background: FONDO }} />}
      <AbsoluteFill style={{ background: lay === 1 ? "linear-gradient(270deg, rgba(4,5,8,0.9) 0%, rgba(4,5,8,0.6) 34%, rgba(4,5,8,0) 62%)" : lay === 2 ? "linear-gradient(0deg, rgba(4,5,8,0.92) 0%, rgba(4,5,8,0.55) 30%, rgba(4,5,8,0) 58%)" : "linear-gradient(90deg, rgba(4,5,8,0.9) 0%, rgba(4,5,8,0.6) 34%, rgba(4,5,8,0) 62%)" }} />
      <AbsoluteFill style={{ background: E.tinte, opacity: 0.16, mixBlendMode: "color" }} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 85% 85%, ${E.a}44, transparent 50%)`, mixBlendMode: "screen" }} />
      <div style={{ position: "absolute", ...(lay === 1 ? { right: 130, top: 330 } : lay === 2 ? { left: 130, bottom: 90 } : { left: 130, top: 330 }), display: "flex", alignItems: "center", gap: 36 }}>
        <svg width={300} height={300} style={{ transform: "rotate(-90deg)" }}>
          <circle cx={150} cy={150} r={130} stroke="#ffffff22" strokeWidth={10} fill="none" />
          <circle cx={150} cy={150} r={130} stroke={E.a} strokeWidth={10} fill="none" strokeLinecap="round" strokeDasharray={arco} strokeDashoffset={arco * (1 - 0.8 * e)} style={{ filter: `drop-shadow(0 0 14px ${E.a})` }} />
        </svg>
        <div style={{ marginLeft: -330, width: 300, textAlign: "center", fontFamily: FUENTE_TITULO, fontSize: String(mostrado).length > 4 ? 100 : 130, color: C.crema, textShadow: `0 0 40px ${E.a}88` }}>{m ? m[1] : ""}{mostrado}<span style={{ color: E.a }}>{m ? m[3].trim() : ""}</span></div>
        {etiqueta && <div style={{ marginLeft: 70, maxWidth: 480, fontFamily: FUENTE_TEXTO, fontWeight: 800, fontSize: 30, letterSpacing: 4, color: E.b, textTransform: "uppercase", opacity: interpolate(f, [10, 24], [0, 1], { extrapolateRight: "clamp" }) }}>{etiqueta}</div>}
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

/** Radar: barrido verde-cian que detecta puntos; algunos se vuelven naranja al ser tocados por el haz. */
export const Radar: React.FC<{ v?: number }> = ({ v = 0 }) => {
  const f = useCurrentFrame();
  const ang = (f * 5) % 360; const R = 420;
  const pts = Array.from({ length: 14 }, (_, i) => { const a = random(`ra${v}_${i}`) * 360, r = 70 + random(`rr${v}_${i}`) * (R - 90); return { a, r, x: Math.cos(a * Math.PI / 180) * r, y: Math.sin(a * Math.PI / 180) * r, raro: i % 4 === 0 }; });
  return (
    <AbsoluteFill style={{ background: FONDO, justifyContent: "center", alignItems: "center" }}>
      <svg width={1000} height={1000} viewBox="-500 -500 1000 1000" style={{ transform: `scale(${1.3 + f * 0.0007})` }}>
        {[1, 2, 3, 4].map((k) => <circle key={k} r={R * k / 4} fill="none" stroke={C.cian} strokeOpacity={0.25} strokeWidth={2} />)}
        <line x1={-R} y1={0} x2={R} y2={0} stroke={C.cian} strokeOpacity={0.18} /><line x1={0} y1={-R} x2={0} y2={R} stroke={C.cian} strokeOpacity={0.18} />
        <defs><linearGradient id="haz" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stopColor={C.cian} stopOpacity={0} /><stop offset="1" stopColor={C.cian} stopOpacity={0.55} /></linearGradient></defs>
        <g transform={`rotate(${ang})`}><path d={`M0 0 L ${R} 0 A ${R} ${R} 0 0 0 ${R * Math.cos(-0.7)} ${R * Math.sin(-0.7)} Z`} fill="url(#haz)" /><line x2={R} stroke={C.cian} strokeWidth={4} style={{ filter: `drop-shadow(0 0 12px ${C.cian})` }} /></g>
        {pts.map((p, i) => { const dif = ((ang - p.a) % 360 + 360) % 360; const brillo = Math.max(0, 1 - dif / 200); const col = p.raro ? C.naranja : C.cian;
          return <circle key={i} cx={p.x} cy={p.y} r={p.raro ? 15 : 10} fill={col} opacity={0.15 + brillo * 0.85} style={{ filter: `drop-shadow(0 0 ${8 + brillo * 14}px ${col})` }} />; })}
      </svg>
    </AbsoluteFill>
  );
};

/** Cuadricula de aparatos: una casilla naranja se contagia y se expande por las vecinas, como fichas de domino. */
export const Cuadricula: React.FC<{ v?: number }> = ({ v = 0 }) => {
  const f = useCurrentFrame(); const { durationInFrames } = useVideoConfig();
  const cols = 16, filas = 9, sz = 100, gap = 18; const w = cols * (sz + gap), h = filas * (sz + gap);
  const o = { x: 2 + (v * 5) % (cols - 4), y: 1 + (v * 3) % (filas - 2) };
  return (
    <AbsoluteFill style={{ background: FONDO, justifyContent: "center", alignItems: "center" }}>
      <div style={{ position: "relative", width: w, height: h, transform: `scale(${1.02 + f / durationInFrames * 0.07})` }}>
        {Array.from({ length: cols * filas }, (_, k) => {
          const cx = k % cols, cy = Math.floor(k / cols); const d = Math.hypot(cx - o.x, cy - o.y); const t = f - 6 - d * 3.8;
          const inf = t > 0 ? Math.min(1, t / 8) : 0;
          return <div key={k} style={{ position: "absolute", left: cx * (sz + gap), top: cy * (sz + gap), width: sz, height: sz, borderRadius: 14,
            background: inf > 0 ? `rgba(255,90,31,${0.25 + inf * 0.65})` : "rgba(53,217,255,0.10)", border: `3px solid ${inf > 0 ? C.naranja : "#35d9ff55"}`,
            boxShadow: inf > 0 ? `0 0 ${30 * inf}px ${C.naranja}` : "none", transform: `scale(${1 + (inf > 0 && inf < 1 ? 0.15 : 0)})` }} />;
        })}
      </div>
    </AbsoluteFill>
  );
};

/** Barras de trafico: una avalancha de peticiones que sube y baja (para ataques/avalanchas/picos). */
export const Barras: React.FC<{ v?: number }> = ({ v = 0 }) => {
  const f = useCurrentFrame(); const { durationInFrames } = useVideoConfig();
  const n = 44; const sube = interpolate(f, [0, durationInFrames * 0.85], [0.15, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: FONDO, justifyContent: "center", alignItems: "center" }}>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 12, height: 640, width: 1700 }}>
        {Array.from({ length: n }, (_, i) => {
          const ruido = 0.5 + 0.5 * Math.sin(f / 5 + i * 0.9 + v) * Math.cos(f / 11 + i * 0.37);
          const h = Math.max(0.05, Math.min(1, (0.18 + 0.82 * ruido) * sube * (0.55 + 0.45 * random(`b${v}_${i}`) + (i / n) * 0.3)));
          const rojo = h > 0.78;
          return <div key={i} style={{ flex: 1, height: `${h * 100}%`, borderRadius: 6, background: rojo ? C.naranja : C.cian, opacity: rojo ? 1 : 0.8, boxShadow: `0 0 20px ${rojo ? C.naranja : C.cian}88` }} />;
        })}
      </div>
      <div style={{ position: "absolute", left: 110, right: 110, bottom: 190, height: 3, background: "#ffffff22" }} />
    </AbsoluteFill>
  );
};

/** Globo de puntos que gira, con arcos luminosos entre ciudades (red mundial / expansion). */
export const Globo2D: React.FC<{ v?: number }> = ({ v = 0 }) => {
  const f = useCurrentFrame(); const R = 380; const rot = f * 0.012 + v;
  const pts: { x: number; y: number; z: number }[] = [];
  for (let la = -75; la <= 75; la += 15) for (let lo = 0; lo < 360; lo += 12 / Math.max(0.35, Math.cos(la * Math.PI / 180))) {
    const a = (lo * Math.PI / 180) + rot, b = la * Math.PI / 180; pts.push({ x: Math.cos(b) * Math.sin(a) * R, y: -Math.sin(b) * R, z: Math.cos(b) * Math.cos(a) });
  }
  const ciudades = Array.from({ length: 9 }, (_, i) => { const lo = random(`lo${v}_${i}`) * Math.PI * 2 + rot, la = (random(`la${v}_${i}`) - 0.5) * 2.0; return { x: Math.cos(la) * Math.sin(lo) * R, y: -Math.sin(la) * R, z: Math.cos(la) * Math.cos(lo), i }; });
  const vis = ciudades.filter((c) => c.z > 0.05);
  return (
    <AbsoluteFill style={{ background: FONDO, justifyContent: "center", alignItems: "center" }}>
      <svg width={1100} height={1000} viewBox="-550 -500 1100 1000" style={{ transform: `scale(${1.25 + f * 0.0006})` }}>
        <circle r={R + 6} fill="none" stroke={C.cian} strokeOpacity={0.35} strokeWidth={3} style={{ filter: `drop-shadow(0 0 20px ${C.cian})` }} />
        {pts.filter((p) => p.z > 0).map((p, i) => <circle key={i} cx={p.x} cy={p.y} r={2 + p.z * 3} fill={C.cian} opacity={0.2 + p.z * 0.6} />)}
        {vis.slice(1).map((c, k) => { const a = vis[k]; const mx = (a.x + c.x) / 2, my = (a.y + c.y) / 2 - 120; const p = (f * 0.03 + k * 0.2) % 1;
          return <g key={k}><path d={`M${a.x} ${a.y} Q${mx} ${my} ${c.x} ${c.y}`} fill="none" stroke={C.naranja} strokeOpacity={0.6} strokeWidth={3} />
            <circle cx={(1 - p) * (1 - p) * a.x + 2 * (1 - p) * p * mx + p * p * c.x} cy={(1 - p) * (1 - p) * a.y + 2 * (1 - p) * p * my + p * p * c.y} r={8} fill="#fff" style={{ filter: `drop-shadow(0 0 10px ${C.naranja})` }} /></g>; })}
        {vis.map((c) => <circle key={c.i} cx={c.x} cy={c.y} r={11} fill={C.naranja} style={{ filter: `drop-shadow(0 0 14px ${C.naranja})` }} />)}
      </svg>
    </AbsoluteFill>
  );
};

/** Lluvia de codigo: columnas de simbolos que caen, con alguna columna naranja (algo se cuela). */
export const Lluvia: React.FC<{ v?: number }> = ({ v = 0 }) => {
  const f = useCurrentFrame(); const cols = 48; const SIM = "01{}<>/\\=+*#$%&@";
  return (
    <AbsoluteFill style={{ background: FONDO, overflow: "hidden" }}>
      {Array.from({ length: cols }, (_, c) => {
        const vel = 5 + random(`lv${v}_${c}`) * 9, off = random(`lo${v}_${c}`) * 1200, raro = c % 11 === 3;
        const y0 = ((f * vel + off) % 1500) - 300;
        return <div key={c} style={{ position: "absolute", left: 20 + c * 39, top: y0 - 560, fontFamily: "monospace", fontSize: 34, lineHeight: "40px", whiteSpace: "pre", color: raro ? C.naranja : C.cian, textShadow: `0 0 14px ${raro ? C.naranja : C.cian}`,
          opacity: raro ? 0.95 : 0.55, WebkitMaskImage: "linear-gradient(to bottom, transparent, #000 90%)", maskImage: "linear-gradient(to bottom, transparent, #000 90%)" }}>
          {Array.from({ length: 15 }, (_, k) => SIM[Math.floor(random(`s${v}_${c}_${k}_${Math.floor(f / 6)}`) * SIM.length)]).join("\n")}</div>;
      })}
    </AbsoluteFill>
  );
};

/** Ondas de señal superpuestas (abstracto, colores del tema). */
export const Ondas: React.FC<{ est?: number; v?: number }> = ({ est = 0, v = 0 }) => {
  const f = useCurrentFrame(); const E = estilo(est);
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse 75% 65% at 50% 45%, ${E.fondo1} 0%, ${E.fondo2} 100%)` }}>
      <svg width="100%" height="100%" viewBox="0 0 1920 1080">
        {Array.from({ length: 7 }, (_, k) => { const amp = 60 + k * 26, fr = 0.004 + k * 0.0011, ph = f * (0.05 + k * 0.012) + v + k;
          const d = Array.from({ length: 97 }, (_, i) => { const x = i * 20; const y = 540 + Math.sin(x * fr + ph) * amp * Math.sin(i / 96 * Math.PI) + Math.sin(x * fr * 2.3 + ph * 1.4) * amp * 0.25; return `${i ? "L" : "M"}${x} ${y}`; }).join(" ");
          return <path key={k} d={d} fill="none" stroke={k % 2 ? E.a : E.b} strokeWidth={4 - k * 0.3} opacity={0.9 - k * 0.1} style={{ filter: `drop-shadow(0 0 12px ${k % 2 ? E.a : E.b})` }} />; })}
      </svg>
    </AbsoluteFill>);
};

/** Anillos HUD que giran y laten (abstracto, colores del tema). */
export const Anillos: React.FC<{ est?: number; v?: number }> = ({ est = 0, v = 0 }) => {
  const f = useCurrentFrame(); const E = estilo(est);
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse 75% 65% at 50% 45%, ${E.fondo1} 0%, ${E.fondo2} 100%)`, justifyContent: "center", alignItems: "center" }}>
      <svg width={1100} height={1100} viewBox="-550 -550 1100 1100" style={{ transform: `scale(${0.95 + f * 0.0012})` }}>
        {[1, 2, 3, 4, 5].map((k) => { const r = 90 + k * 78; const dir = k % 2 ? 1 : -1; const pulso = 1 + 0.03 * Math.sin(f / 5 + k + v);
          return <g key={k} transform={`rotate(${dir * f * (0.8 + k * 0.4) + v * 37}) scale(${pulso})`}>
            <circle r={r} fill="none" stroke={k % 2 ? E.a : E.b} strokeWidth={3 + (k === 3 ? 5 : 0)} strokeDasharray={`${40 + k * 22} ${24 + k * 10}`} opacity={0.9} style={{ filter: `drop-shadow(0 0 10px ${k % 2 ? E.a : E.b})` }} />
            <circle cx={r} r={9} fill={E.a} /></g>; })}
        <circle r={46} fill={E.a} opacity={0.85} style={{ filter: `drop-shadow(0 0 30px ${E.a})` }} />
      </svg>
    </AbsoluteFill>);
};

/** Texto escrito letra por letra en monoespaciada (fragmentos del caso), sobre negro con azul frio; **lo marcado** sale en rojo/ambar. Ocupa solo una parte del cuadro. */
export const Escribe: React.FC<{ texto: string; est?: number }> = ({ texto, est = 2 }) => {
  const f = useCurrentFrame(); const { durationInFrames: D } = useVideoConfig(); const E = estilo(est);
  const limpio = texto.replace(/\*\*/g, ""); const ini = texto.indexOf("**"); const fin = texto.lastIndexOf("**") - 2;
  const n = Math.min(limpio.length, Math.floor(Math.max(0, f - 6) * limpio.length / Math.max(20, D * 0.72)));
  const vis = limpio.slice(0, n); const pre = ini >= 0 ? vis.slice(0, ini) : vis; const hi = ini >= 0 ? vis.slice(ini, Math.max(ini, fin)) : "";
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse 70% 60% at 30% 50%, ${E.fondo1} 0%, ${E.fondo2} 75%)` }}>
      <AbsoluteFill style={{ backgroundImage: "repeating-linear-gradient(0deg, rgba(255,255,255,0.035) 0px, rgba(255,255,255,0.035) 2px, transparent 2px, transparent 5px)" }} />
      <div style={{ position: "absolute", left: 150, top: 300, width: 1240, fontFamily: FUENTE_TERMINAL, fontSize: 70, lineHeight: 1.18, color: "#cfe6ff", textShadow: `0 0 18px ${E.b}88` }}>
        <span style={{ color: E.b }}>{"> "}</span>{pre}<span style={{ color: E.a, textShadow: `0 0 22px ${E.a}` }}>{hi}</span>{Math.floor(f / 7) % 2 === 0 && <span style={{ background: E.a }}>{"\u00a0"}</span>}
      </div>
    </AbsoluteFill>);
};
