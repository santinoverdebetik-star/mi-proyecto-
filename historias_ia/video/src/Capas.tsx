import React from "react";
import { AbsoluteFill, staticFile, useCurrentFrame, random } from "remotion";
import { C, FUENTE_TEXTO, FUENTE_TITULO } from "./estilo";

export const Fuentes: React.FC = () => (
  <style>{`
    @font-face { font-family: ${FUENTE_TITULO}; src: url(${staticFile("fuentes/anton-latin-400-normal.woff2")}) format("woff2"); }
    @font-face { font-family: ${FUENTE_TEXTO}; font-weight: 500; src: url(${staticFile("fuentes/inter-latin-500-normal.woff2")}) format("woff2"); }
    @font-face { font-family: ${FUENTE_TEXTO}; font-weight: 800; src: url(${staticFile("fuentes/inter-latin-800-normal.woff2")}) format("woff2"); }
  `}</style>
);

/** viñeta + grano de pelicula + polvo flotante: va encima de TODAS las escenas para unificar el look */
export const Acabado: React.FC<{ vineta?: number; grano?: number }> = ({ vineta = 0.5, grano = 0.06 }) => {
  const f = useCurrentFrame();
  const semilla = Math.floor(f / 2);                                   // el grano cambia cada 2 fotogramas (look de 15 fps)
  const polvo = Array.from({ length: 26 }, (_, i) => {
    const x = (random(`px${i}`) * 100 + Math.sin((f + i * 17) / 90) * 2) % 100;
    const y = (random(`py${i}`) * 140 - f * (0.015 + random(`v${i}`) * 0.03) + 140) % 100;
    return { x, y, r: 1 + random(`r${i}`) * 2.2, o: 0.08 + random(`o${i}`) * 0.2 };
  });
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg width="100%" height="100%" style={{ position: "absolute", mixBlendMode: "screen" }}>
        {polvo.map((p, i) => <circle key={i} cx={`${p.x}%`} cy={`${p.y}%`} r={p.r} fill="#fff" opacity={p.o} />)}
      </svg>
      <svg width="100%" height="100%" style={{ position: "absolute", mixBlendMode: "overlay", opacity: grano * 9 }}>
        <filter id={`g${semilla}`}><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={semilla} /><feColorMatrix type="saturate" values="0" /></filter>
        <rect width="100%" height="100%" filter={`url(#g${semilla})`} />
      </svg>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,${vineta}) 100%)` }} />
    </AbsoluteFill>
  );
};

/** destello rojo/blanco muy corto para golpes de impacto (“hit”) */
export const Flash: React.FC<{ en: number; color?: string }> = ({ en, color = "#fff" }) => {
  const f = useCurrentFrame();
  const o = Math.max(0, 1 - Math.abs(f - en) / 4) * 0.55;
  return <AbsoluteFill style={{ background: color, opacity: o, mixBlendMode: "screen" }} />;
};
