import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C } from "../estilo";

/** Imagen 3D/render aportada (public/img/...) con empuje lento, deriva y gradacion oscura con brillo de color. */
export const Imagen: React.FC<{ archivo: string; zoom?: [number, number]; deriva?: [number, number]; brillo?: string }> = ({ archivo, zoom = [1.04, 1.18], deriva = [0, -30], brillo = C.naranja }) => {
  const f = useCurrentFrame(); const { durationInFrames } = useVideoConfig();
  const t = interpolate(f, [0, durationInFrames], [0, 1]);
  const s = zoom[0] + (zoom[1] - zoom[0]) * t;
  return (
    <AbsoluteFill style={{ background: C.negro, overflow: "hidden" }}>
      <Img src={staticFile(archivo)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${s}) translate(${deriva[0] * t}px, ${deriva[1] * t}px)`, filter: "contrast(1.12) saturate(0.9) brightness(0.9)" }} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 70% 60%, ${brillo}22, transparent 55%)`, mixBlendMode: "screen" }} />
    </AbsoluteFill>
  );
};
