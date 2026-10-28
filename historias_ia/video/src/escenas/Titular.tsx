import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FUENTE_TITULO } from "../estilo";

/** Titular condensado, crema desgastado (+ palabra clave en naranja). Como “NEW GUEST” de la miniatura. */
export const Titular: React.FC<{ lineas: string[]; resalta?: number; lado?: "izq" | "centro"; fondo?: string }> = ({ lineas, resalta, lado = "centro", fondo }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: C.negro, justifyContent: "center", alignItems: lado === "centro" ? "center" : "flex-start", paddingLeft: lado === "izq" ? 140 : 0 }}>
      {fondo && <><Img src={staticFile(fondo)} style={{ position: "absolute", width: "100%", height: "100%", objectFit: "cover", transform: "scale(1.06)" }} /><AbsoluteFill style={{ background: "rgba(0,0,0,0.6)" }} /><AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(0,0,0,0.7), rgba(0,0,0,0.15))" }} /></>}
      <svg width="0" height="0"><filter id="desgaste"><feTurbulence type="fractalNoise" baseFrequency="0.22" numOctaves="4" seed="4" result="n" /><feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -4 3.2" result="m" /><feComposite in="SourceGraphic" in2="m" operator="in" /></filter></svg>
      <div style={{ textAlign: lado === "centro" ? "center" : "left", transform: `scale(${interpolate(f, [0, 90], [1, 1.06])})` }}>
        {lineas.map((l, i) => {
          const e = spring({ frame: f - i * 6, fps, config: { damping: 14, stiffness: 140 } });
          return (
            <div key={i} style={{ fontFamily: FUENTE_TITULO, fontSize: i === resalta ? 300 : 250, lineHeight: 0.98, letterSpacing: 2, textTransform: "uppercase",
              color: i === resalta ? C.naranja : C.crema, opacity: e, transform: `translateY(${(1 - e) * 60}px)`, filter: "url(#desgaste)",
              textShadow: i === resalta ? `0 0 60px ${C.naranja}88` : "none" }}>{l}</div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
