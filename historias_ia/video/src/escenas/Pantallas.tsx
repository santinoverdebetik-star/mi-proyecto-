import React from "react";
import { AbsoluteFill, interpolate, random, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FUENTE_PIXEL } from "../estilo";

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
export const Transicion: React.FC<{ tipo?: string; children: React.ReactNode }> = ({ tipo = "pixel", children }) => {
  const f = useCurrentFrame(); const { durationInFrames: D } = useVideoConfig();
  const tin = Math.min(1, f / ENT), tout = Math.min(1, (D - 1 - f) / SAL);          // 0 = tapado ... 1 = visible
  let cap: React.ReactNode = null; let estilo: React.CSSProperties = {};
  if (tipo === "pixel") {
    const cols = 24, filas = 14, sw = 80, sh = 78;
    const celdas = [];
    for (let i = 0; i < cols * filas; i++) {
      const r = random(`p${i}`); const x = i % cols, y = Math.floor(i / cols);
      const orden = (r * 0.7 + (x / cols) * 0.3);                                        // barrido suave de izquierda a derecha + azar
      const visibleIn = tin < 1 && orden > tin * 1.0;
      const visibleOut = tout < 1 && orden < (1 - tout) * 1.0;
      if (visibleIn || visibleOut) celdas.push(<div key={i} style={{ position: "absolute", left: x * sw, top: y * sh, width: sw + 1, height: sh + 1, background: COLS_PIX[i % 4] }} />);
    }
    cap = <AbsoluteFill>{celdas}</AbsoluteFill>;
  } else if (tipo === "barras") {
    const n = 8, ancho = 240; const bs = [];
    for (let i = 0; i < n; i++) {
      const ein = tin < 1 ? 1 - Math.max(0, Math.min(1, (f - i * 0.6) / (ENT - 4))) : 0;
      const eout = tout < 1 ? 1 - Math.max(0, Math.min(1, (D - 1 - f - (n - i) * 0.5) / (SAL - 3))) : 0;
      if (ein > 0) bs.push(<div key={"i" + i} style={{ position: "absolute", left: i * ancho, top: 0, width: ancho + 1, height: "100%", background: i % 2 ? C.naranja : "#e0201b", transform: `scaleY(${ein})`, transformOrigin: "top" }} />);
      if (eout > 0) bs.push(<div key={"o" + i} style={{ position: "absolute", left: i * ancho, top: 0, width: ancho + 1, height: "100%", background: i % 2 ? C.naranja : "#e0201b", transform: `scaleY(${eout})`, transformOrigin: "bottom" }} />);
    }
    cap = <AbsoluteFill>{bs}</AbsoluteFill>;
  } else {                                                                              // zoom con desenfoque + destello
    const e = tin < 1 ? 1 - tin : 0, s = tout < 1 ? 1 - tout : 0;
    estilo = { transform: `scale(${1 + e * 0.28 + s * 0.16})`, filter: `blur(${e * 14 + s * 10}px)` };
    cap = <AbsoluteFill style={{ background: "#fff", opacity: e * 0.55 + s * 0.4, mixBlendMode: "screen" }} />;
  }
  return <AbsoluteFill><AbsoluteFill style={estilo}>{children}</AbsoluteFill>{cap}</AbsoluteFill>;
};
