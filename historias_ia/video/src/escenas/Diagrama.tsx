import React from "react";
import { AbsoluteFill, interpolate, random, useCurrentFrame } from "remotion";
import { C, FUENTE_TEXTO } from "../estilo";

type Nodo = { id: string; x: number; y: number; etiqueta?: string; icono?: "casa" | "tv" | "pc" | "movil" | "camara" | "router" | "nube" };
const Icono: React.FC<{ t: Nodo["icono"]; c: string }> = ({ t, c }) => {
  const p = { fill: "none", stroke: c, strokeWidth: 3, strokeLinejoin: "round" as const, strokeLinecap: "round" as const };
  switch (t) {
    case "casa": return <g {...p}><path d="M-60 10 L0 -50 L60 10 M-46 0 V60 H46 V0" /><rect x="-12" y="25" width="24" height="35" /><rect x="-32" y="-8" width="18" height="18" /></g>;
    case "tv": return <g {...p}><rect x="-70" y="-42" width="140" height="84" rx="6" /><path d="M-24 58 H24 M0 42 V58" /></g>;
    case "pc": return <g {...p}><rect x="-62" y="-40" width="124" height="76" rx="6" /><path d="M-82 50 H82" /></g>;
    case "movil": return <g {...p}><rect x="-28" y="-56" width="56" height="112" rx="10" /><path d="M-8 -44 H8" /></g>;
    case "camara": return <g {...p}><rect x="-56" y="-26" width="86" height="52" rx="6" /><path d="M30 -10 L62 -26 V26 L30 10 Z" /></g>;
    case "router": return <g {...p}><rect x="-66" y="0" width="132" height="42" rx="6" /><path d="M-40 0 L-52 -40 M40 0 L52 -40 M0 0 V-50" /></g>;
    default: return <g {...p}><path d="M-60 30 A28 28 0 0 1 -44 -22 A40 40 0 0 1 30 -30 A32 32 0 0 1 56 30 Z" /></g>;
  }
};

/** Diagrama de linea neon (cian) sobre negro; con “infeccion” que se propaga y cambia a rojo/naranja. */
export const Diagrama: React.FC<{ nodos: Nodo[]; enlaces: [string, string][]; infecta?: string[]; titulo?: string; escala?: number; ritmo?: number }> = ({ nodos, enlaces, infecta = [], titulo, escala = 1.5, ritmo = 5 }) => {
  const f = useCurrentFrame(); const W = 1920, H = 1080;
  const pos = (id: string) => nodos.find((n) => n.id === id)!;
  const aparece = (i: number) => interpolate(f, [i * ritmo, i * ritmo + 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const infectadoEn = (id: string) => { const k = infecta.indexOf(id); return k < 0 ? Infinity : 50 + k * (infecta.length > 6 ? 9 : 26); };
  return (
    <AbsoluteFill style={{ background: C.negro }}>
      <AbsoluteFill style={{ background: "radial-gradient(circle at 50% 55%, #0b1822 0%, #040405 70%)" }} />
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ position: "absolute" }}>
        <defs><filter id="neon" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter></defs>
        <g filter="url(#neon)">
          {enlaces.map(([a, b], i) => {
            const A0 = pos(a), B0 = pos(b); const t = Math.min(1, aparece(i + 2));
            const L = Math.hypot(B0.x - A0.x, B0.y - A0.y), r0 = 105 * escala; const ux = (B0.x - A0.x) / L, uy = (B0.y - A0.y) / L;
            const A = { x: A0.x + ux * r0, y: A0.y + uy * r0 }, B = { x: B0.x - ux * r0, y: B0.y - uy * r0 };
            const inf = f > Math.min(infectadoEn(a), infectadoEn(b)) && (infecta.includes(a) || infecta.includes(b));
            const col = inf ? C.naranja : C.cian;
            const mx = (A.x + B.x) / 2, my = (A.y + B.y) / 2;
            const zig = Array.from({ length: 6 }, (_, k) => { const u = (k + 1) / 7; return [A.x + (B.x - A.x) * u + (random(`z${i}${k}${Math.floor(f / 3)}`) - 0.5) * 26, A.y + (B.y - A.y) * u + (random(`w${i}${k}${Math.floor(f / 3)}`) - 0.5) * 26]; });
            const d = `M${A.x} ${A.y} ` + zig.map(([x, y]) => `L${x} ${y}`).join(" ") + ` L${B.x} ${B.y}`;
            return <path key={i} d={inf ? d : `M${A.x} ${A.y} L${B.x} ${B.y}`} stroke={col} strokeWidth={inf ? 3 : 2} fill="none" strokeDasharray={inf ? undefined : "1200"} strokeDashoffset={inf ? undefined : 1200 * (1 - t)} opacity={0.9} data-m={mx + my} />;
          })}
          {nodos.map((n, i) => {
            const inf = f > infectadoEn(n.id); const col = inf ? C.naranja : C.cian; const t = aparece(i);
            return (
              <g key={n.id} transform={`translate(${n.x} ${n.y}) scale(${escala * (0.85 + 0.15 * t)})`} opacity={t}>
                <Icono t={n.icono} c={col} />
                {n.etiqueta && <text y={92} fontSize={20} textAnchor="middle" fill={col} fontFamily={FUENTE_TEXTO} fontWeight={500} style={{ letterSpacing: 3, textTransform: "uppercase" }}>{n.etiqueta}</text>}
              </g>
            );
          })}
        </g>
      </svg>
      {titulo && <div style={{ position: "absolute", top: 70, width: "100%", textAlign: "center", color: C.gris, fontFamily: FUENTE_TEXTO, fontWeight: 500, fontSize: 30, letterSpacing: 8, textTransform: "uppercase" }}>{titulo}</div>}
    </AbsoluteFill>
  );
};
