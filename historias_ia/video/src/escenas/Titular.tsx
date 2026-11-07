import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { FUENTE_DIN, FUENTE_TITULO } from "../estilo";
import { estilo } from "../estilos";

/** Titular sobre FOTO REAL con gradacion tipo After Effects (contraste, viñeta, destello de color, grano). El texto ocupa solo un lado (~40 % del cuadro), nunca toda la escena. */
export const Titular: React.FC<{ lineas: string[]; resalta?: number; lado?: "izq" | "centro"; fondo?: string; est?: number; lay?: number }> = ({ lineas, resalta, fondo, est = 0, lay = 0 }) => {
  const f = useCurrentFrame(); const { fps, durationInFrames: D } = useVideoConfig();
  const E = estilo(est);
  const t = interpolate(f, [0, D], [0, 1], { extrapolateRight: "clamp" });
  const n = lineas.length; const tam = n > 2 ? 104 : 128;
  const lado = lay === 1 ? "der" : "izq"; const din = lay >= 2;                 // lay 2-4: tipografia DIN condensada blanca (referencia 3); 0-1: cartel Anton
  const grad = lado === "izq" ? "linear-gradient(90deg, rgba(4,5,8,0.92) 0%, rgba(4,5,8,0.78) 30%, rgba(4,5,8,0.12) 62%, rgba(4,5,8,0) 100%)" : "linear-gradient(270deg, rgba(4,5,8,0.92) 0%, rgba(4,5,8,0.78) 30%, rgba(4,5,8,0.12) 62%, rgba(4,5,8,0) 100%)";
  const gradB = "linear-gradient(0deg, rgba(4,5,8,0.95) 0%, rgba(4,5,8,0.7) 28%, rgba(4,5,8,0) 60%)";
  const caja: React.CSSProperties = lay === 4 ? { left: 0, right: 0, top: 380, alignItems: "center", textAlign: "center" } : lay === 2 ? { left: 130, bottom: 110, width: 1000 } : lay === 3 ? { left: 130, top: 300, width: 760, padding: "34px 44px", background: "rgba(5,6,10,0.72)", border: `4px solid ${E.a}`, boxShadow: `0 0 50px ${E.a}55` }
    : lado === "der" ? { right: 130, top: 0, bottom: 0, width: 780, justifyContent: "center", alignItems: "flex-end", textAlign: "right" } : { left: 130, top: 0, bottom: 0, width: 780, justifyContent: "center" };
  return (
    <AbsoluteFill style={{ background: "#07090d", overflow: "hidden" }}>
      {fondo
        ? <Img src={staticFile(fondo)} style={{ position: "absolute", width: "100%", height: "100%", objectFit: "cover", transform: `scale(${1.08 + 0.1 * t}) translateX(${(lay % 2 ? 1 : -1) * t * 30}px)`, filter: E.filtro }} />
        : <AbsoluteFill style={{ background: `radial-gradient(ellipse 75% 65% at 60% 40%, ${E.fondo1} 0%, #151a24 55%, ${E.fondo2} 100%)` }} />}
      <AbsoluteFill style={{ background: lay === 4 ? "radial-gradient(ellipse 60% 40% at 50% 50%, rgba(2,3,5,0.78) 0%, rgba(2,3,5,0.25) 70%, rgba(2,3,5,0) 100%)" : lay === 2 ? gradB : lay === 3 ? "linear-gradient(90deg, rgba(4,5,8,0.5), rgba(4,5,8,0.05))" : grad }} />
      <AbsoluteFill style={{ background: E.tinte, opacity: 0.16, mixBlendMode: "color" }} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at ${88 - t * 12}% 80%, ${E.a}55, transparent 50%)`, mixBlendMode: "screen" }} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 15% 15%, ${E.b}22, transparent 40%)`, mixBlendMode: "screen" }} />
      {lay === 2 && <AbsoluteFill style={{ background: `linear-gradient(90deg, transparent 0%, ${E.a}22 50%, transparent 100%)`, height: 6, top: 880, boxShadow: `0 0 30px ${E.a}` }} />}
      <svg width="0" height="0"><filter id="desgaste"><feTurbulence type="fractalNoise" baseFrequency="0.22" numOctaves="4" seed="4" result="n" /><feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -4 3.2" result="m" /><feComposite in="SourceGraphic" in2="m" operator="in" /></filter></svg>
      <div style={{ position: "absolute", display: "flex", flexDirection: "column", ...caja }}>
        <div style={{ width: interpolate(f, [0, 12], [0, 260], { extrapolateRight: "clamp" }), height: 8, background: E.a, boxShadow: `0 0 24px ${E.a}`, marginBottom: 26, alignSelf: lado === "der" ? "flex-end" : "flex-start" }} />
        {lineas.map((l, i) => {
          const e = spring({ frame: f - 3 - i * 6, fps, config: { damping: 14, stiffness: 140 } });
          const k = i === (resalta ?? n - 1);
          return <div key={i} style={{ fontFamily: din ? FUENTE_DIN : FUENTE_TITULO, fontWeight: din ? 600 : 400, fontSize: lay === 4 ? 92 : din ? tam * 0.82 : tam, lineHeight: 1.04, letterSpacing: din ? 8 : 2, textTransform: "uppercase", color: k ? E.a : din ? "#f4f4f2" : "#f1e8d6",
            opacity: e, transform: `translateX(${(1 - e) * (lado === "der" ? 80 : -80)}px)`, filter: "url(#desgaste)", textShadow: k ? `0 0 50px ${E.a}99` : "0 4px 30px #000" }}>{l}</div>;
        })}
      </div>
    </AbsoluteFill>
  );
};
