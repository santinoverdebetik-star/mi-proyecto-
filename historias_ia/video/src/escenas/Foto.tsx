import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

/** Foto REAL a pantalla completa (clip corto entre los 3D): empuje/alejamiento lento con deriva, buena luz y un toque de color de acento. */
export const Foto: React.FC<{ archivo: string; luz?: string; v?: number; pos?: string }> = ({ archivo, luz = "media", v = 0, pos = "50% 50%" }) => {
  const f = useCurrentFrame(); const { durationInFrames } = useVideoConfig();
  const t = interpolate(f, [0, durationInFrames], [0, 1], { extrapolateRight: "clamp" });
  const dentro = v % 2 === 0;
  const s = dentro ? 1.06 + 0.12 * t : 1.18 - 0.12 * t;
  const dx = [-26, 26, 0, 18][v % 4] * (dentro ? t : 1 - t), dy = [0, -14, 20, 10][v % 4] * (dentro ? t : 1 - t);
  const br = { noche: 0.95, media: 1.05, clara: 1.12 }[luz as "noche"] ?? 1.05;
  const acento = ["#ff5a1f", "#35d9ff"][v % 2];
  return (
    <AbsoluteFill style={{ background: "#05060a", overflow: "hidden" }}>
      <Img src={staticFile(archivo)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: pos, transform: `scale(${s}) translate(${dx}px, ${dy}px)`, filter: `contrast(1.1) saturate(1.05) brightness(${br})` }} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at ${v % 2 ? 78 : 22}% 70%, ${acento}2e, transparent 55%)`, mixBlendMode: "screen" }} />
    </AbsoluteFill>
  );
};
