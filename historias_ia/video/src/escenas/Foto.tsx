import React from "react";
import { estilo } from "../estilos";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

/** Foto REAL a pantalla completa (clip corto entre los 3D): empuje/alejamiento lento con deriva, buena luz y un toque de color de acento. */
export const Foto: React.FC<{ archivo: string; luz?: string; v?: number; pos?: string; est?: number; marco?: number }> = ({ archivo, luz = "media", v = 0, pos = "50% 50%", est = 0, marco = 0 }) => {
  const E = estilo(est);
  const f = useCurrentFrame(); const { durationInFrames } = useVideoConfig();
  const t = interpolate(f, [0, durationInFrames], [0, 1], { extrapolateRight: "clamp" });
  const dentro = v % 2 === 0;
  const s = dentro ? 1.06 + 0.12 * t : 1.18 - 0.12 * t;
  const dx = [-26, 26, 0, 18][v % 4] * (dentro ? t : 1 - t), dy = [0, -14, 20, 10][v % 4] * (dentro ? t : 1 - t);
  const br = { noche: 0.95, media: 1.05, clara: 1.12 }[luz as "noche"] ?? 1.05;
  const acento = E.a;
  return (
    <AbsoluteFill style={{ background: "#05060a", overflow: "hidden" }}>
      <Img src={staticFile(archivo)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: pos, transform: `scale(${s}) translate(${dx}px, ${dy}px)`, filter: `${E.filtro} brightness(${br})` }} />
      <AbsoluteFill style={{ background: E.tinte, opacity: 0.14, mixBlendMode: "color" }} />
      {marco === 1 && <><AbsoluteFill style={{ border: "0 solid #000", borderTopWidth: 70, borderBottomWidth: 70 }} /></>}
      {marco === 2 && <AbsoluteFill style={{ margin: 46, border: `3px solid ${E.a}aa`, boxShadow: `inset 0 0 40px ${E.a}33` }}><div style={{ position: "absolute", left: 14, top: 12, width: 14, height: 14, borderRadius: 7, background: "#ff2a2a", opacity: Math.floor(f / 15) % 2 ? 1 : 0.2 }} /></AbsoluteFill>}
      {marco === 3 && <AbsoluteFill style={{ backgroundImage: "repeating-linear-gradient(0deg, rgba(0,0,0,0.22) 0px, rgba(0,0,0,0.22) 2px, transparent 2px, transparent 5px)", mixBlendMode: "multiply" }} />}
      <AbsoluteFill style={{ background: `radial-gradient(circle at ${v % 2 ? 78 : 22}% 70%, ${acento}2e, transparent 55%)`, mixBlendMode: "screen" }} />
    </AbsoluteFill>
  );
};
