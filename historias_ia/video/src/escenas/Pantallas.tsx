import React from "react";
import { AbsoluteFill, interpolate, random, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FUENTE_PIXEL } from "../estilo";
import { estilo } from "../estilos";

/* ---------- iconos de pixel art (14 columnas; '#' = pixel) ---------- */
const ICONOS: Record<string, string[]> = {
  tv: ["..#........#..", "...#......#...", "##############", "#............#", "#.##########.#", "#.#........#.#", "#.#........#.#", "#.#........#.#", "#.##########.#", "#............#", "##############", "....########.."],
  caja: ["..............", "..............", "..............", "##############", "#............#", "#............#", "#.##########.#", "#..........#.#", "#............#", "##############", "..#........#..", ".............."],
  intruso: ["....######....", "..##########..", ".############.", ".##..####..##.", ".##..####..##.", ".############.", ".############.", "..##########..", "..#.##..##.#..", "..#.##..##.#..", "...#.#..#.#...", ".............."],
  laptop: ["..............", "..##########..", "..#........#..", "..#........#..", "..#........#..", "..#........#..", "..##########..", ".############.", "##............##".slice(0, 14), "##############", "..............", ".............."],
  router: ["...#......#...", "...#......#...", "...#......#...", "...#......#...", "##############", "#............#", "#.#.#.#......#", "#............#", "##############", "..............", "..............", ".............."],
  candado: ["....######....", "...##....##...", "...#......#...", "...#......#...", "##############", "#............#", "#.....##.....#", "#.....##.....#", "#.....##.....#", "#............#", "##############", ".............."],
  nube: ["..............", "......###.....", "....#######...", "...#########..", ".############.", "##############", "##############", ".############.", "..............", "..............", "..............", ".............."],
  alerta: ["......##......", ".....####.....", ".....####.....", "....######....", "....##..##....", "...###..###...", "...###..###...", "..####..####..", "..##########..", ".############.", "##############", ".............."],
  codigo: ["..............", "...#......#...", "..#........#..", ".#...#..#...#.", ".#....##....#.", ".#...#..#...#.", ".#...#..#...#.", "..#........#..", "...#......#...", "..............", "..............", ".............."],
  flechas: ["..............", ".#########.##.", ".#########..##", "..............", "..............", "##.#########..", "#..#########..", "..............", "..............", "..............", "..............", ".............."],
};
const PIX = (ic: string, px: number, color: string, borde = "#14080a") => {
  const m = ICONOS[ic] ?? ICONOS.caja; const w = 14, h = m.length;
  const celdas: React.ReactNode[] = [];
  m.forEach((fila, y) => fila.split("").forEach((c, x) => {
    if (c !== "#") return;
    celdas.push(<rect key={`b${x}_${y}`} x={x * px - 3} y={y * px - 3} width={px + 6} height={px + 6} fill={borde} />);
  }));
  m.forEach((fila, y) => fila.split("").forEach((c, x) => { if (c === "#") celdas.push(<rect key={`${x}_${y}`} x={x * px} y={y * px} width={px} height={px} fill={color} />); }));
  return <svg width={w * px} height={h * px} viewBox={`-6 -6 ${w * px + 12} ${h * px + 12}`} style={{ overflow: "visible" }}>{celdas}</svg>;
};

const TEMAS: Record<string, { c1: string; c2: string; izq: string; der: string }> = {
  rojo: { c1: "#c4162a", c2: "#4a0610", izq: "#2f56d6", der: "#f08a12" },
  azul: { c1: "#1d4fb8", c2: "#06133a", izq: "#35d9ff", der: "#ff5a1f" },
  oscuro: { c1: "#2b3344", c2: "#05060a", izq: "#35d9ff", der: "#ff5a1f" },
  verde: { c1: "#1a8a5a", c2: "#04281a", izq: "#2f56d6", der: "#f0c812" },
  morado: { c1: "#7a1ab8", c2: "#1e0436", izq: "#35d9ff", der: "#ff8a1f" },
  amarillo: { c1: "#c89a14", c2: "#3a2a04", izq: "#1f3fd6", der: "#d8221b" },
};

export type Tarjeta = { icono: string; titulo: string; valor: string };
/** Pantalla de comparacion en pixel art (dos tarjetas crema con icono, titulo y valor + icono central), fondo de color liso con viñeta. */
export const Comparar: React.FC<{ izq: Tarjeta; der: Tarjeta; centro?: string; tema?: string }> = ({ izq, der, centro = "vs", tema = "rojo" }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const T = TEMAS[tema] ?? TEMAS.rojo;
  const eI = spring({ frame: f - 3, fps, config: { damping: 12, stiffness: 120 } });
  const eD = spring({ frame: f - 9, fps, config: { damping: 12, stiffness: 120 } });
  const eC = spring({ frame: f - 16, fps, config: { damping: 9, stiffness: 160 } });
  const paso = Math.floor(f / 4);                                         // movimiento "a saltos" como el pixel art
  const bob = (k: number) => Math.round(Math.sin(paso * 0.9 + k) * 2) * 4;
  const tarj = (t: Tarjeta, color: string, e: number, lado: number, k: number) => (
    <div style={{ width: 520, height: 540, background: "linear-gradient(160deg,#f7ecd4,#e8d9b8)", border: "5px solid #14080a", boxShadow: "10px 10px 0 #14080a66",
      transform: `translateX(${(1 - e) * lado * 900}px) rotate(${(1 - e) * lado * 6}deg)`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 26 }}>
      <div style={{ transform: `translateY(${bob(k)}px)` }}>{PIX(t.icono, 17, color)}</div>
      <div style={{ fontFamily: FUENTE_PIXEL, fontSize: 21, color: "#2a2018", letterSpacing: 1, textAlign: "center", maxWidth: 460, lineHeight: 1.5 }}>{t.titulo}</div>
      <div style={{ fontFamily: FUENTE_PIXEL, fontSize: t.valor.length > 9 ? 34 : 44, color, textAlign: "center", letterSpacing: 1, textShadow: "3px 3px 0 #14080a22" }}>{t.valor}</div>
    </div>);
  const trem = f % 7 === 0 && f > 30 ? 3 : 0;
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse 80% 75% at 50% 45%, ${T.c1} 0%, ${T.c2} 100%)`, justifyContent: "center", alignItems: "center" }}>
      <AbsoluteFill style={{ backgroundImage: "linear-gradient(#ffffff0d 2px, transparent 2px), linear-gradient(90deg, #ffffff0d 2px, transparent 2px)", backgroundSize: "60px 60px" }} />
      <div style={{ display: "flex", alignItems: "center", gap: 90, transform: `translate(${trem}px,0) scale(${1 + f * 0.0004})` }}>
        {tarj(izq, T.izq, eI, -1, 0)}
        <div style={{ transform: `scale(${eC}) rotate(${(1 - eC) * 90}deg) translateY(${bob(3)}px)`, opacity: Math.min(1, eC) }}>{centro === "vs" ? <div style={{ width: 150, height: 150, background: "#f7ecd4", border: "5px solid #14080a", boxShadow: "7px 7px 0 #14080a66", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: FUENTE_PIXEL, fontSize: 52, color: "#14080a" }}>VS</div> : PIX(centro, 12, "#fff7ec")}</div>
        {tarj(der, T.der, eD, 1, 2)}
      </div>
    </AbsoluteFill>
  );
};

/* ---------- transiciones profesionales (entrada y salida de cada escena) ---------- */
const ENT = 9, SAL = 7;
const COLS_PIX = [C.naranja, "#e0201b", "#f1e8d6", "#ff8a3d"];
export const Transicion: React.FC<{ tipo?: string; est?: number; children: React.ReactNode }> = ({ tipo = "pixel", est = 0, children }) => {
  const EE = estilo(est); const CP = [EE.a, EE.b, "#f1e8d6", EE.a];
  const f = useCurrentFrame(); const { durationInFrames: D } = useVideoConfig();
  const tin = Math.min(1, f / ENT), tout = Math.min(1, (D - 1 - f) / SAL);          // 0 = tapado ... 1 = visible
  let cap: React.ReactNode = null; let estilo_: React.CSSProperties = {};
  if (tipo === "pixel") {
    const cols = 24, filas = 14, sw = 80, sh = 78;
    const celdas = [];
    for (let i = 0; i < cols * filas; i++) {
      const r = random(`p${i}`); const x = i % cols, y = Math.floor(i / cols);
      const orden = (r * 0.7 + (x / cols) * 0.3);                                        // barrido suave de izquierda a derecha + azar
      const visibleIn = tin < 1 && orden > tin * 1.0;
      const visibleOut = tout < 1 && orden < (1 - tout) * 1.0;
      if (visibleIn || visibleOut) celdas.push(<div key={i} style={{ position: "absolute", left: x * sw, top: y * sh, width: sw + 1, height: sh + 1, background: CP[i % 4] }} />);
    }
    cap = <AbsoluteFill>{celdas}</AbsoluteFill>;
  } else if (tipo === "barras") {
    const n = 8, ancho = 240; const bs = [];
    for (let i = 0; i < n; i++) {
      const ein = tin < 1 ? 1 - Math.max(0, Math.min(1, (f - i * 0.6) / (ENT - 4))) : 0;
      const eout = tout < 1 ? 1 - Math.max(0, Math.min(1, (D - 1 - f - (n - i) * 0.5) / (SAL - 3))) : 0;
      if (ein > 0) bs.push(<div key={"i" + i} style={{ position: "absolute", left: i * ancho, top: 0, width: ancho + 1, height: "100%", background: i % 2 ? EE.a : EE.b, transform: `scaleY(${ein})`, transformOrigin: "top" }} />);
      if (eout > 0) bs.push(<div key={"o" + i} style={{ position: "absolute", left: i * ancho, top: 0, width: ancho + 1, height: "100%", background: i % 2 ? EE.a : EE.b, transform: `scaleY(${eout})`, transformOrigin: "bottom" }} />);
    }
    cap = <AbsoluteFill>{bs}</AbsoluteFill>;
  } else if (tipo === "cortina") {                                                      // barrido diagonal de color
    const ein = tin < 1 ? 1 - tin : 0, eout = tout < 1 ? 1 - tout : 0;
    if (ein > 0) cap = <AbsoluteFill style={{ background: `linear-gradient(115deg, ${EE.a} 0%, ${EE.a} ${ein * 130 - 30}%, transparent ${ein * 130 - 29}%)` }} />;
    if (eout > 0) cap = <AbsoluteFill style={{ background: `linear-gradient(115deg, transparent ${100 - eout * 130 + 30}%, ${EE.b} ${100 - eout * 130 + 31}%)` }} />;
  } else if (tipo === "persianas") {                                                    // persianas horizontales
    const n = 10, h = 108, bs = [];
    for (let i = 0; i < n; i++) { const ein = tin < 1 ? 1 - Math.max(0, Math.min(1, (f - i * 0.5) / (ENT - 3))) : 0; const eout = tout < 1 ? 1 - Math.max(0, Math.min(1, (D - 1 - f - (n - i) * 0.4) / (SAL - 2))) : 0; const e = Math.max(ein, eout);
      if (e > 0) bs.push(<div key={i} style={{ position: "absolute", top: i * h, left: 0, width: "100%", height: h + 1, background: i % 2 ? EE.a : "#14080a", transform: `scaleX(${e})`, transformOrigin: ein > 0 ? "left" : "right" }} />); }
    cap = <AbsoluteFill>{bs}</AbsoluteFill>;
  } else if (tipo === "rgb") {                                                          // separacion RGB + destello
    const e = tin < 1 ? 1 - tin : 0, s = tout < 1 ? 1 - tout : 0; const sp = (e + s) * 40;
    estilo_ = { filter: `drop-shadow(${sp}px 0 0 rgba(255,0,60,0.8)) drop-shadow(${-sp}px 0 0 rgba(0,200,255,0.8))`, transform: `translateX(${(e - s) * 30}px)` };
    cap = <AbsoluteFill style={{ background: "#fff", opacity: (e + s) * 0.45, mixBlendMode: "screen" }} />;
  } else {                                                                              // zoom con desenfoque + destello
    const e = tin < 1 ? 1 - tin : 0, s = tout < 1 ? 1 - tout : 0;
    estilo_ = { transform: `scale(${1 + e * 0.28 + s * 0.16})`, filter: `blur(${e * 14 + s * 10}px)` };
    cap = <AbsoluteFill style={{ background: "#fff", opacity: e * 0.55 + s * 0.4, mixBlendMode: "screen" }} />;
  }
  return <AbsoluteFill><AbsoluteFill style={estilo_}>{children}</AbsoluteFill>{cap}</AbsoluteFill>;
};

/** Pantalla roja de 'ordenador': ventana crema (como la que se ve en el monitor de la sala) o cadena de aparatos en pixel art con paquetes que viajan. */
const FONDOS_ROJA: Record<string, [string, string, string]> = { rojo: ["#c4162a", "#4a0610", "#3a0510"], cian: ["#1d6fb8", "#06223a", "#05182a"], verde: ["#1a8a5a", "#06301e", "#04221a"], magenta: ["#9a1ab8", "#2e0640", "#220430"], amarillo: ["#c89a14", "#4a3606", "#382804"], naranja: ["#d9531a", "#4a1a06", "#381204"], bn: ["#6a6a6e", "#1a1a1c", "#101012"] };
export const Roja: React.FC<{ variante?: string; etiqueta?: string; v?: number; est?: number }> = ({ variante = "ventana", etiqueta, v = 0, est = 1 }) => {
  const FR = FONDOS_ROJA[estilo(est).n];
  const f = useCurrentFrame(); const { fps, durationInFrames: D } = useVideoConfig();
  const t = f / D; const paso = Math.floor(f / 3);
  const fondo = (
    <>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 80% 75% at 50% 45%, ${FR[0]} 0%, ${FR[1]} 100%)` }} />
      <AbsoluteFill style={{ backgroundImage: "linear-gradient(#ffffff0d 2px, transparent 2px), linear-gradient(90deg, #ffffff0d 2px, transparent 2px)", backgroundSize: "60px 60px" }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 150, height: 6, background: "#14080a55" }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 150, background: FR[2] }} />
      {Array.from({ length: 14 }, (_, i) => <div key={i} style={{ position: "absolute", left: i * 140, bottom: 156, width: 90 + (i * 37) % 60, height: 20 + (i * 53) % 50, background: "#8d0f1e" }} />)}
    </>);
  if (variante === "ventana") {
    const e = spring({ frame: f, fps, config: { damping: 16, stiffness: 110 } });
    const lineas = [0.62, 0.48, 0.7, 0.35, 0.56];
    return (
      <AbsoluteFill>{fondo}
        <div style={{ position: "absolute", left: 269, top: 216, width: 1382, height: 626, background: "#f3e7cf", border: "5px solid #14080a", boxShadow: "12px 12px 0 #14080a66", transform: `scale(${(0.9 + 0.1 * e) * (1 + t * 0.06)})`, opacity: e }}>
          <div style={{ height: 46, background: "#2a5bd7", display: "flex", alignItems: "center", paddingLeft: 18, gap: 10 }}>{[0, 1, 2].map((i) => <div key={i} style={{ width: 16, height: 16, background: "#f3e7cf" }} />)}</div>
          <div style={{ padding: "46px 60px" }}>
            {lineas.map((w, i) => <div key={i} style={{ height: 20, width: `${Math.min(100, Math.max(0, (f - 8 - i * 5) * 5)) * w}%`, background: "#2a2018", opacity: 0.8, marginBottom: 34 }} />)}
            {Math.floor(f / 9) % 2 === 0 && <div style={{ width: 20, height: 34, background: "#14080a", marginTop: -8 }} />}
          </div>
        </div>
        {etiqueta && <div style={{ position: "absolute", top: 70, width: "100%", textAlign: "center", fontFamily: FUENTE_PIXEL, fontSize: 34, color: "#f7ecd4", textShadow: "4px 4px 0 #14080a" }}>{etiqueta}</div>}
      </AbsoluteFill>);
  }
  const nodos = [{ ic: "caja", x: 260, c: "#2f56d6" }, { ic: "router", x: 760, c: "#f7ecd4" }, { ic: "nube", x: 1260, c: "#f08a12" }, { ic: "laptop", x: 1700, c: "#f7ecd4" }];
  return (
    <AbsoluteFill>{fondo}
      <svg width="100%" height="100%" viewBox="0 0 1920 1080" style={{ position: "absolute" }}>
        {nodos.slice(1).map((n, i) => { const a = nodos[i]; const prog = ((f * 0.02 + i * 0.3) % 1);
          return <g key={i}><line x1={a.x + 80} y1={700} x2={n.x - 80} y2={700} stroke="#14080a" strokeWidth={14} /><line x1={a.x + 80} y1={700} x2={n.x - 80} y2={700} stroke="#f08a12" strokeWidth={6} strokeDasharray="14 14" />
            {[0, 1, 2].map((k) => { const q = (prog + k * 0.18) % 1; return <rect key={k} x={a.x + 80 + (n.x - a.x - 160) * q - 9} y={700 - 9 - (paso % 2) * 3} width={18} height={18} fill="#fff7ec" stroke="#14080a" strokeWidth={3} />; })}</g>; })}
      </svg>
      {nodos.map((n, i) => { const e = spring({ frame: f - 4 - i * 5, fps, config: { damping: 12, stiffness: 140 } });
        return <div key={i} style={{ position: "absolute", left: n.x - 100, top: 480 + (1 - e) * 120 + Math.round(Math.sin(paso * 0.8 + i) * 2) * 4, opacity: e }}>{PIX(n.ic, 14, n.c)}</div>; })}
      {etiqueta && <div style={{ position: "absolute", top: 110, width: "100%", textAlign: "center", fontFamily: FUENTE_PIXEL, fontSize: 40, color: "#f7ecd4", textShadow: "4px 4px 0 #14080a" }}>{etiqueta}</div>}
    </AbsoluteFill>);
};
