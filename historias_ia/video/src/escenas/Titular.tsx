import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FUENTE_TITULO } from "../estilo";

/** Titular sobre FOTO REAL con gradacion tipo After Effects (contraste, viñeta, destello de color, grano). El texto ocupa solo un lado (~40 % del cuadro), nunca toda la escena. */
export const Titular: React.FC<{ lineas: string[]; resalta?: number; lado?: "izq" | "centro"; fondo?: string }> = ({ lineas, resalta, fondo }) => {
  const f = useCurrentFrame(); const { fps, durationInFrames: D } = useVideoConfig();
  const t = interpolate(f, [0, D], [0, 1], { extrapolateRight: "clamp" });
  const n = lineas.length; const tam = n > 2 ? 104 : 128;
  return (
    <AbsoluteFill style={{ background: "#07090d", overflow: "hidden" }}>
      {fondo
        ? <Img src={staticFile(fondo)} style={{ position: "absolute", width: "100%", height: "100%", objectFit: "cover", transform: `scale(${1.08 + 0.1 * t}) translateX(${-t * 30}px)`, filter: "contrast(1.22) saturate(1.1) brightness(0.8)" }} />
        : <AbsoluteFill style={{ background: "radial-gradient(ellipse 75% 65% at 60% 40%, #2a3244 0%, #151a24 55%, #05060a 100%)" }} />}
      <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(4,5,8,0.92) 0%, rgba(4,5,8,0.78) 30%, rgba(4,5,8,0.12) 62%, rgba(4,5,8,0) 100%)" }} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at ${88 - t * 12}% 80%, ${C.naranja}55, transparent 50%)`, mixBlendMode: "screen" }} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 15% 15%, ${C.cian}22, transparent 40%)`, mixBlendMode: "screen" }} />
      <svg width="0" height="0"><filter id="desgaste"><feTurbulence type="fractalNoise" baseFrequency="0.22" numOctaves="4" seed="4" result="n" /><feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -4 3.2" result="m" /><feComposite in="SourceGraphic" in2="m" operator="in" /></filter></svg>
      <div style={{ position: "absolute", left: 130, top: 0, bottom: 0, width: 780, display: "flex", flexDirection: "column", justifyContent: "center" }}>
        <div style={{ width: interpolate(f, [0, 12], [0, 260], { extrapolateRight: "clamp" }), height: 8, background: C.naranja, boxShadow: `0 0 24px ${C.naranja}`, marginBottom: 26 }} />
        {lineas.map((l, i) => {
          const e = spring({ frame: f - 3 - i * 6, fps, config: { damping: 14, stiffness: 140 } });
          const k = i === (resalta ?? n - 1);
          return <div key={i} style={{ fontFamily: FUENTE_TITULO, fontSize: tam, lineHeight: 1.0, letterSpacing: 2, textTransform: "uppercase", color: k ? C.naranja : C.crema,
            opacity: e, transform: `translateX(${(1 - e) * -80}px)`, filter: "url(#desgaste)", textShadow: k ? `0 0 50px ${C.naranja}99` : "0 4px 30px #000" }}>{l}</div>;
        })}
      </div>
    </AbsoluteFill>
  );
};
