import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import * as THREE from "three";
import { RB } from "./Realismo";
import { C } from "../estilo";
import { CajaStreaming } from "./Objetos3D";

const rnd = (s: string) => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return ((h >>> 0) % 10000) / 10000; };
const mix = (a: string, b: string, t: number) => new THREE.Color(a).lerp(new THREE.Color(b), Math.min(1, Math.max(0, t)));
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const Mat: React.FC<{ c: string; e?: string; ei?: number; r?: number; m?: number }> = ({ c, e, ei = 0, r = 0.5, m = 0.3 }) => <meshStandardMaterial color={c} emissive={e ?? "#000"} emissiveIntensity={ei} roughness={r} metalness={m} />;

export const Router: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <group position={[0, -0.3, 0]}>
      <mesh><RB args={[2.4, 0.28, 1.3]} /><Mat c="#2a2e37" r={0.4} m={0.5} /></mesh>
      {[-0.9, 0, 0.9].map((x, i) => <mesh key={i} position={[x, 0.85, -0.5]} rotation={[0, 0, (i - 1) * 0.18]}><RB args={[0.07, 1.5, 0.07]} /><Mat c="#15171c" /></mesh>)}
      {[0, 1, 2, 3, 4].map((i) => <mesh key={i} position={[-0.9 + i * 0.3, 0.02, 0.66]}><RB args={[0.1, 0.07, 0.02]} /><Mat c="#000" e={i === 2 ? C.naranja : C.cian} ei={(Math.floor((f + i * 6) / 8) % 2) ? 3 : 0.6} /></mesh>)}
      {[0, 1, 2, 3].map((k) => { const t = ((f / 60 + k / 4) % 1); return <mesh key={k} position={[0, 0.9, -0.5]} scale={0.4 + t * 3.6}><torusGeometry args={[1, 0.012, 8, 48]} /><meshBasicMaterial color={C.naranja} transparent opacity={(1 - t) * 0.8} /></mesh>; })}
      <pointLight position={[0, 2, 3]} color="#aac8ff" intensity={6} distance={10} />
    </group>
  );
};

export const CamaraSeguridad: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <group position={[0, 0.5, 0]}>
      <mesh position={[0, 0, -0.9]}><RB args={[3.2, 2.4, 0.1]} /><Mat c="#262a33" r={0.9} m={0.1} /></mesh>
      <mesh position={[0, 0.2, -0.6]}><cylinderGeometry args={[0.1, 0.1, 0.6, 12]} /><Mat c="#555b66" m={0.8} /></mesh>
      <group position={[0, 0.2, 0]} rotation={[0, Math.sin(f / 40) * 0.55, 0]}>
        <mesh position={[0, 0, 0.15]}><RB args={[0.7, 0.55, 1.4]} /><Mat c="#c9ced6" r={0.35} m={0.6} /></mesh>
        <mesh position={[0, 0, 0.95]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.24, 0.24, 0.3, 24]} /><Mat c="#0b0c0f" m={0.9} r={0.2} /></mesh>
        <mesh position={[0, 0, 1.11]}><circleGeometry args={[0.18, 24]} /><Mat c="#000" e="#3a7cc0" ei={1.2} /></mesh>
        <mesh position={[0.25, 0.32, 0.3]}><sphereGeometry args={[0.05, 10, 10]} /><Mat c="#000" e={C.rojo} ei={(Math.floor(f / 15) % 2) ? 4 : 0.3} /></mesh>
        <pointLight position={[0, 0, 1.4]} color={C.rojo} intensity={3} distance={4} />
      </group>
      <pointLight position={[2, 2, 3]} color="#cfe0ff" intensity={8} distance={10} />
    </group>
  );
};

export const Movil: React.FC = () => {
  const f = useCurrentFrame();
  const inf = interpolate(f, [30, 90], [0, 1], clamp);
  const col = mix("#1c6fb8", C.naranja, inf > 0.5 ? 1 : 0);   // azul normal -> naranja infectado (sin tono rosa intermedio)
  return (
    <group position={[0, 0.7, 0]} rotation={[0.1, f * 0.012 - 0.5, 0.05]}>
      <mesh><RB args={[1.0, 2.0, 0.1]} /><Mat c="#14161b" m={0.8} r={0.25} /></mesh>
      <mesh position={[0, 0, 0.055]}><planeGeometry args={[0.9, 1.9]} /><Mat c="#02060a" e={"#" + col.getHexString()} ei={0.9 + inf} /></mesh>
      {[0, 1, 2, 3, 4].map((i) => <mesh key={i} position={[-0.1, 0.65 - i * 0.28, 0.06]}><RB args={[0.55 + rnd("m" + i) * 0.2, 0.09, 0.01]} /><Mat c="#fff" e="#fff" ei={1.2} /></mesh>)}
      <pointLight position={[0, 0, 1.6]} color={"#" + col.getHexString()} intensity={5} distance={7} />
      <pointLight position={[2, 2, 3]} color="#cfe0ff" intensity={5} distance={10} />
    </group>
  );
};

export const PcAntiguo: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <group position={[0, 0.2, 0]}>
      <mesh position={[0, 0.7, 0]}><RB args={[2.2, 1.9, 1.7]} /><Mat c="#cfc6a8" r={0.8} m={0.05} /></mesh>
      <mesh position={[0, 0.8, 0.88]}><planeGeometry args={[1.7, 1.3]} /><Mat c="#010a03" e="#16e052" ei={0.6} /></mesh>
      {Array.from({ length: 9 }, (_, i) => <mesh key={i} position={[-0.7 + (rnd("p" + i) * 0.6) / 2 + 0.25, 1.25 - i * 0.14 - ((f * 0.01) % 0.14), 0.89]}><RB args={[0.3 + rnd("q" + i) * 1.0, 0.045, 0.01]} /><Mat c="#000" e="#7dff9f" ei={1.8} /></mesh>)}
      <mesh position={[0, -0.35, 1.5]}><RB args={[2.0, 0.12, 0.7]} /><Mat c="#cfc6a8" r={0.8} m={0.05} /></mesh>
      <mesh position={[2.0, 0.1, 0]}><RB args={[0.9, 1.9, 1.6]} /><Mat c="#cfc6a8" r={0.8} m={0.05} /></mesh>
      <pointLight position={[0, 1, 2.2]} color="#29ff7a" intensity={4} distance={7} />
      <pointLight position={[-2, 3, 4]} color="#ffe9c0" intensity={7} distance={12} />
    </group>
  );
};

export const Reloj: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <group position={[0, 0.8, 0]}>
      <mesh rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[1.5, 1.5, 0.14, 48]} /><Mat c="#b9b4a8" r={0.8} m={0} /></mesh>
      <mesh position={[0, 0, 0.05]}><torusGeometry args={[1.52, 0.09, 12, 64]} /><Mat c="#2a2e37" m={0.8} r={0.3} /></mesh>
      {Array.from({ length: 12 }, (_, i) => { const a = (i / 12) * Math.PI * 2; return <mesh key={i} position={[Math.sin(a) * 1.28, Math.cos(a) * 1.28, 0.08]} rotation={[0, 0, -a]}><RB args={[0.07, 0.24, 0.02]} /><Mat c="#111" /></mesh>; })}
      <group position={[0, 0, 0.1]} rotation={[0, 0, -f * 0.006]}><mesh position={[0, 0.4, 0]}><RB args={[0.09, 0.9, 0.02]} /><Mat c="#111" /></mesh></group>
      <group position={[0, 0, 0.11]} rotation={[0, 0, -f * 0.07]}><mesh position={[0, 0.55, 0]}><RB args={[0.06, 1.2, 0.02]} /><Mat c="#111" /></mesh></group>
      <group position={[0, 0, 0.12]} rotation={[0, 0, -f * 0.42]}><mesh position={[0, 0.6, 0]}><RB args={[0.025, 1.35, 0.02]} /><Mat c="#000" e={C.naranja} ei={2} /></mesh></group>
      <pointLight position={[1.5, 2, 3]} color="#fff0d8" intensity={9} distance={9} />
    </group>
  );
};

export const Calendario: React.FC = () => {
  const f = useCurrentFrame();
  const flip = interpolate(f, [20, 55], [0, Math.PI * 0.98], clamp);
  const marca = interpolate(f, [70, 90], [0, 1], clamp);
  const hoja = (z: number) => (
    <group>
      <mesh position={[0, 0, z]}><RB args={[2.6, 3.0, 0.03]} /><Mat c="#ece8de" r={0.8} m={0} /></mesh>
      <mesh position={[0, 1.2, z + 0.02]}><RB args={[2.6, 0.55, 0.01]} /><Mat c="#b3261e" e="#b3261e" ei={0.4} /></mesh>
      {Array.from({ length: 35 }, (_, i) => <mesh key={i} position={[-1.05 + (i % 7) * 0.35, 0.65 - Math.floor(i / 7) * 0.4, z + 0.02]}><RB args={[0.2, 0.16, 0.01]} /><Mat c="#2b2b2b" /></mesh>)}
    </group>
  );
  return (
    <group position={[0, 0.8, 0]}>
      {hoja(0)}
      <group position={[0, 1.5, 0.05]} rotation={[-flip, 0, 0]}><group position={[0, -1.5, 0]}>{hoja(0.02)}</group></group>
      <mesh position={[0.35, 0.25, 0.09]} scale={marca}><torusGeometry args={[0.24, 0.025, 8, 32]} /><Mat c="#000" e={C.naranja} ei={2.5} /></mesh>
      <pointLight position={[1.5, 2, 3]} color="#fff0d8" intensity={9} distance={9} />
    </group>
  );
};

export const Placa: React.FC = () => {
  const f = useCurrentFrame();
  const trazos = Array.from({ length: 40 }, (_, i) => ({ x: (rnd("x" + i) - 0.5) * 5, z: (rnd("z" + i) - 0.5) * 3.2, l: 0.5 + rnd("l" + i) * 1.4, h: rnd("h" + i) > 0.5 }));
  return (
    <group rotation={[-0.9, 0.2, 0]} position={[0, 0.5, 0]}>
      <mesh><RB args={[5.4, 0.08, 3.6]} /><Mat c="#0c3d2a" r={0.5} m={0.2} /></mesh>
      {trazos.map((t, i) => <mesh key={i} position={[t.x, 0.06, t.z]}><RB args={t.h ? [t.l, 0.01, 0.04] : [0.04, 0.01, t.l]} /><Mat c="#000" e="#c8a24a" ei={0.9} /></mesh>)}
      {[[-1.2, -0.6], [1.0, 0.5], [-0.3, 0.9]].map(([x, z], i) => <mesh key={i} position={[x, 0.15, z]}><RB args={[0.9 - i * 0.15, 0.16, 0.9 - i * 0.15]} /><Mat c="#14171d" r={0.3} m={0.6} /></mesh>)}
      {Array.from({ length: 6 }, (_, i) => { const t = ((f / 80 + i / 6) % 1); return <mesh key={i} position={[-2.4 + t * 4.8, 0.12, -1.2 + (i % 3) * 1.0]}><sphereGeometry args={[0.07, 10, 10]} /><Mat c="#000" e={C.naranja} ei={3} /></mesh>; })}
      <pointLight position={[0, 2, 1]} color="#ffd9a8" intensity={6} distance={9} />
    </group>
  );
};

export const Llave: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <group position={[0, 0.5, 0]} rotation={[0, Math.sin(f / 50) * 0.4, 0]}>
      <mesh><RB args={[2.0, 2.6, 0.2]} /><Mat c="#2d323b" m={0.7} r={0.35} /></mesh>
      <mesh position={[0, 0.15, 0.11]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.28, 0.28, 0.05, 24]} /><Mat c="#000" e={C.naranja} ei={1.6} /></mesh>
      <group position={[0, 0.15, 0.25]} rotation={[0, 0, f * 0.01]}>
        <mesh position={[0, 0, 0.45]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.06, 0.06, 1.0, 12]} /><Mat c="#d6b25a" m={0.95} r={0.25} /></mesh>
        {[0.25, 0.4, 0.6].map((z, i) => <mesh key={i} position={[0.1, 0, z]}><RB args={[0.2, 0.06, 0.07]} /><Mat c="#d6b25a" m={0.95} r={0.25} /></mesh>)}
        <mesh position={[0, 0, 1.05]}><torusGeometry args={[0.32, 0.08, 12, 32]} /><Mat c="#d6b25a" m={0.95} r={0.25} /></mesh>
      </group>
      <pointLight position={[0, 0.2, 1.8]} color={C.naranja} intensity={5} distance={6} />
      <pointLight position={[2, 2, 3]} color="#cfe0ff" intensity={6} distance={10} />
    </group>
  );
};

export const Dominos: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <group position={[0, -0.8, 0]}>
      {Array.from({ length: 26 }, (_, i) => {
        const caida = interpolate(f, [10 + i * 5, 24 + i * 5], [0, 1.25], clamp);
        return (
          <group key={i} position={[-5.4 + i * 0.42, 0, 0]}>
            <group position={[0.1, 0, 0]} rotation={[0, 0, -caida]}><mesh position={[-0.1, 0.55, 0]}><RB args={[0.13, 1.1, 0.55]} /><Mat c={i === 0 || caida > 0.3 ? "#c9561d" : "#d9d4c6"} e={caida > 0.3 ? C.naranja : "#000"} ei={caida > 0.3 ? 0.7 : 0} r={0.4} m={0.1} /></mesh></group>
          </group>
        );
      })}
      <pointLight position={[0, 3, 4]} color="#fff0d8" intensity={9} distance={14} />
    </group>
  );
};

export const Escudo: React.FC = () => {
  const f = useCurrentFrame();
  const forma = new THREE.Shape(); forma.moveTo(0, 1.5); forma.lineTo(1.1, 1.1); forma.lineTo(1.1, 0); forma.quadraticCurveTo(1.0, -1.0, 0, -1.6); forma.quadraticCurveTo(-1.0, -1.0, -1.1, 0); forma.lineTo(-1.1, 1.1); forma.lineTo(0, 1.5);
  const g = interpolate(f, [25, 80], [0, 1], clamp);
  return (
    <group position={[0, 0.8, 0]} rotation={[0, Math.sin(f / 45) * 0.35, 0]}>
      <mesh><extrudeGeometry args={[forma, { depth: 0.18, bevelEnabled: true, bevelSize: 0.05, bevelThickness: 0.05, bevelSegments: 2 }]} /><Mat c="#4a7fb0" m={0.8} r={0.3} e="#12304f" ei={0.6} /></mesh>
      {[[0.1, 0.9, 0.4, 0.5], [0.0, 0.2, -0.5, -0.5], [-0.2, -0.4, 0.3, 0.4], [0.3, -0.9, -0.3, 0.45]].map(([x, y, rz, l], i) => <mesh key={i} position={[x, y * g + (1 - g) * 2, 0.25]} rotation={[0, 0, rz]} scale={[1, g, 1]}><RB args={[0.05, l * 2, 0.02]} /><Mat c="#000" e={C.naranja} ei={3} /></mesh>)}
      <pointLight position={[0, 0, 1.6]} color={C.naranja} intensity={g * 9} distance={6} />
      <pointLight position={[2, 2, 3]} color="#cfe0ff" intensity={7} distance={10} />
    </group>
  );
};

export const Dinero: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <group position={[0, -0.9, 0]} rotation={[0, f * 0.004, 0]}>
      {[[-1.7, 0.4], [0, 0.7], [1.7, 0.3], [-0.9, -1.4], [0.9, -1.2]].map(([x, z], i) => (
        <group key={i} position={[x, 0, z]}>
          {Array.from({ length: 12 + i * 3 }, (_, k) => <mesh key={k} position={[(rnd("j" + i + k) - 0.5) * 0.06, 0.04 + k * 0.045, (rnd("k" + i + k) - 0.5) * 0.06]} rotation={[0, (rnd("r" + i + k) - 0.5) * 0.08, 0]}><RB args={[1.0, 0.04, 0.5]} /><Mat c="#7fa383" e="#1f3a25" ei={0.6} r={0.8} m={0} /></mesh>)}
          <mesh position={[0, 0.3 + i * 0.07, 0]}><RB args={[0.35, 0.72 + i * 0.14, 0.52]} /><Mat c="#caa46a" r={0.9} m={0} /></mesh>
        </group>
      ))}
      <pointLight position={[0, 3, 3]} color="#fff0d8" intensity={9} distance={12} />
    </group>
  );
};

export const Hdmi: React.FC = () => {
  const f = useCurrentFrame();
  const x = interpolate(f, [15, 75], [-2.6, 0.05], clamp);
  return (
    <group position={[0, 0.3, 0]}>
      <mesh position={[1.2, 0, 0]}><RB args={[2.8, 1.5, 0.5]} /><Mat c="#1a1d24" m={0.6} r={0.4} /></mesh>
      <mesh position={[0.0, 0, 0.27]}><RB args={[0.9, 0.22, 0.04]} /><Mat c="#000" e={C.cian} ei={1.0 + 1.5 * interpolate(f, [70, 80], [0, 1], clamp)} /></mesh>
      <group position={[x, 0, 0.1]}>
        <mesh position={[-0.35, 0, 0]}><RB args={[0.7, 0.26, 0.2]} /><Mat c="#14161b" m={0.4} r={0.5} /></mesh>
        <mesh position={[0.2, 0, 0]}><RB args={[0.45, 0.17, 0.1]} /><Mat c="#c9ced6" m={0.95} r={0.2} /></mesh>
        <mesh position={[-1.8, 0, 0]}><RB args={[2.2, 0.1, 0.1]} /><Mat c="#14161b" /></mesh>
      </group>
      <pointLight position={[0, 1.2, 2]} color={C.cian} intensity={5} distance={7} />
      <pointLight position={[2, 2, 4]} color="#cfe0ff" intensity={6} distance={12} />
    </group>
  );
};

export const Password: React.FC = () => {
  const f = useCurrentFrame();
  const abre = interpolate(f, [40, 70], [0, 1], clamp);
  return (
    <group position={[0, 0.7, 0]}>
      <mesh><RB args={[3.6, 2.4, 0.08]} /><Mat c="#10151d" m={0.5} r={0.4} e="#0d1a2c" ei={0.8} /></mesh>
      <mesh position={[0, -0.1, 0.06]}><RB args={[2.6, 0.4, 0.02]} /><Mat c="#1d2733" e="#233447" ei={0.6} /></mesh>
      <mesh position={[-1.1 + ((Math.floor(f / 10) % 2) ? 0.04 : 0), -0.1, 0.08]}><RB args={[0.03, 0.26, 0.01]} /><Mat c="#fff" e="#fff" ei={2} /></mesh>
      <mesh position={[0, 0.65, 0.06]}><RB args={[0.9, 0.7, 0.05]} /><Mat c="#9aa3b0" m={0.8} r={0.3} /></mesh>
      <group position={[0.25, 1.0, 0.06]} rotation={[0, 0, -abre * 0.7]}><mesh position={[-0.25, abre * 0.15 + 0.1, 0]}><torusGeometry args={[0.25, 0.05, 10, 24, Math.PI]} /><Mat c="#c3c7ce" m={0.9} r={0.25} /></mesh></group>
      <mesh position={[0, -0.75, 0.06]} scale={[abre, 1, 1]}><RB args={[2.0, 0.06, 0.02]} /><Mat c="#000" e={C.naranja} ei={2.6} /></mesh>
      <pointLight position={[0, 0.5, 2]} color="#7fa8ff" intensity={5} distance={7} />
    </group>
  );
};

export const Engranajes: React.FC = () => {
  const f = useCurrentFrame();
  const gear = (x: number, y: number, r: number, dientes: number, sentido: number, color: string, emis = 0) => (
    <group position={[x, y, 0]} rotation={[0, 0, sentido * f * 0.02 * (8 / dientes)]}>
      <mesh rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[r, r, 0.35, 40]} /><Mat c={color} m={0.85} r={0.3} e={color} ei={emis} /></mesh>
      {Array.from({ length: dientes }, (_, i) => { const a = (i / dientes) * Math.PI * 2; return <mesh key={i} position={[Math.sin(a) * (r + 0.1), Math.cos(a) * (r + 0.1), 0]} rotation={[0, 0, -a]}><RB args={[0.22, 0.28, 0.35]} /><Mat c={color} m={0.85} r={0.3} e={color} ei={emis} /></mesh>; })}
      <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 0, 0.18]}><cylinderGeometry args={[r * 0.35, r * 0.35, 0.05, 20]} /><Mat c="#14161b" /></mesh>
    </group>
  );
  return <group position={[0, 0.7, 0]}>{gear(-1.5, 0, 1.2, 12, 1, "#7c8594")}{gear(0.95, 0.85, 0.85, 9, -1, "#8b93a1")}{gear(1.3, -1.0, 0.7, 7, 1, "#b84a1a", 0.35)}<pointLight position={[0, 1, 3]} color="#fff0d8" intensity={9} distance={10} /></group>;
};

export const Latido: React.FC = () => {
  const f = useCurrentFrame();
  const n = 120;
  const ecg = (u: number) => { const p = (u % 1); if (p < 0.1) return 0.0; if (p < 0.2) return Math.sin((p - 0.1) * Math.PI / 0.1) * 0.15; if (p < 0.3) return 0; if (p < 0.34) return -0.2 * ((p - 0.3) / 0.04); if (p < 0.4) return -0.2 + 1.7 * ((p - 0.34) / 0.06); if (p < 0.46) return 1.5 - 1.9 * ((p - 0.4) / 0.06); if (p < 0.5) return -0.4 + 0.4 * ((p - 0.46) / 0.04); return 0; };
  const cae = interpolate(f, [0, 150], [0, 1], clamp);
  return (
    <group position={[0, 0.4, 0]}>
      <mesh position={[0, 0.5, -0.1]}><RB args={[7.4, 3.0, 0.06]} /><Mat c="#05100f" e="#062321" ei={0.7} /></mesh>
      {Array.from({ length: n }, (_, i) => { const x = -3.4 + (i / n) * 6.8; const y = ecg(i / 40 - f * 0.012) * 1.0; return <mesh key={i} position={[x, y + 0.2, 0]}><sphereGeometry args={[0.045, 8, 8]} /><Mat c="#000" e={"#" + mix("#37f0c9", C.rojo, cae).getHexString()} ei={2.4} /></mesh>; })}
      <pointLight position={[0, 1, 3]} color={"#" + mix("#37f0c9", C.rojo, cae).getHexString()} intensity={6} distance={9} />
    </group>
  );
};

export const Paquetes: React.FC = () => {
  const f = useCurrentFrame();
  const nodos: [number, number, number][] = [[-4, -0.4, 0], [-2, 0.9, -0.5], [0, -0.2, 0.3], [2, 1.0, -0.4], [4, 0.1, 0.2]];
  return (
    <group position={[0, 0.3, 0]}>
      {nodos.map((p, i) => <mesh key={i} position={p}><RB args={[0.5, 0.5, 0.5]} /><Mat c="#26303d" e={C.cian} ei={0.9} m={0.6} r={0.3} /></mesh>)}
      {nodos.slice(1).map((p, i) => { const a = new THREE.Vector3(...nodos[i]), b = new THREE.Vector3(...p), q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize()); return <mesh key={i} position={a.clone().add(b).multiplyScalar(0.5)} quaternion={q}><cylinderGeometry args={[0.03, 0.03, a.distanceTo(b), 8]} /><Mat c="#000" e={C.cian} ei={1.2} /></mesh>; })}
      {Array.from({ length: 9 }, (_, k) => { const u = ((f / 140 + k / 9) % 1) * 4, s = Math.min(3, Math.floor(u)), t = u - s; const a = new THREE.Vector3(...nodos[s]), b = new THREE.Vector3(...nodos[s + 1]); const bad = k % 3 === 0; return <mesh key={k} position={a.lerp(b, t)} rotation={[f * 0.05, f * 0.04, 0]}><RB args={[0.2, 0.2, 0.2]} /><Mat c="#000" e={bad ? C.naranja : "#e8f6ff"} ei={bad ? 3 : 1.6} /></mesh>; })}
      <pointLight position={[0, 2, 3]} color="#9fd8ff" intensity={6} distance={12} />
    </group>
  );
};

export const Antena: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <group position={[0, -1, 0]}>
      {[[-0.5, -0.5], [0.5, -0.5], [-0.5, 0.5], [0.5, 0.5]].map(([x, z], i) => <mesh key={i} position={[x * (1 - 0.0), 1.9, z]} rotation={[z * -0.08, 0, x * 0.08]}><RB args={[0.06, 3.8, 0.06]} /><Mat c="#b9bfc9" m={0.8} r={0.4} /></mesh>)}
      {[0.4, 1.2, 2.0, 2.8].map((y, i) => <mesh key={i} position={[0, y, 0]}><RB args={[1.0 - i * 0.18, 0.04, 1.0 - i * 0.18]} /><Mat c="#b9bfc9" m={0.8} r={0.4} /></mesh>)}
      <mesh position={[0, 3.95, 0]}><sphereGeometry args={[0.1, 12, 12]} /><Mat c="#000" e={C.rojo} ei={(Math.floor(f / 14) % 2) ? 4 : 0.3} /></mesh>
      {[0, 1, 2].map((k) => { const t = ((f / 80 + k / 3) % 1); return <mesh key={k} position={[0, 3.6, 0]} scale={0.3 + t * 4.5}><torusGeometry args={[1, 0.015, 8, 48]} /><meshBasicMaterial color={C.naranja} transparent opacity={(1 - t) * 0.85} /></mesh>; })}
      <pointLight position={[2, 4, 4]} color="#cfe0ff" intensity={9} distance={14} />
    </group>
  );
};

export const Lupa: React.FC = () => {
  const f = useCurrentFrame();
  const x = Math.sin(f / 60) * 1.6;
  return (
    <group position={[0, 0.3, 0]}>
      {Array.from({ length: 80 }, (_, i) => { const mala = i === 37; return <mesh key={i} position={[-3.2 + (i % 16) * 0.42, 0.9 - Math.floor(i / 16) * 0.45, 0]}><sphereGeometry args={[mala ? 0.09 : 0.06, 10, 10]} /><Mat c="#000" e={mala ? C.naranja : C.cian} ei={mala ? 3 : 1.2} /></mesh>; })}
      <group position={[x, 0.3, 0.6]}>
        <mesh><torusGeometry args={[0.9, 0.08, 14, 40]} /><Mat c="#b9bfc9" m={0.9} r={0.25} /></mesh>
        <mesh position={[0, 0, 0.0]}><circleGeometry args={[0.88, 32]} /><meshPhysicalMaterial color="#cfe8ff" transparent opacity={0.16} roughness={0.05} /></mesh>
        <mesh position={[0.8, -0.8, 0]} rotation={[0, 0, Math.PI / 4]}><RB args={[0.12, 1.1, 0.12]} /><Mat c="#14161b" /></mesh>
      </group>
      <pointLight position={[0, 1.5, 3]} color="#bcd8ff" intensity={8} distance={10} />
    </group>
  );
};

export const Mando: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <group position={[0, 0.5, 0]} rotation={[-0.9, 0.0, 0.25 + Math.sin(f / 50) * 0.08]}>
      <mesh><RB args={[0.8, 2.6, 0.22]} /><Mat c="#1a1d24" m={0.4} r={0.5} /></mesh>
      {Array.from({ length: 12 }, (_, i) => <mesh key={i} position={[-0.2 + (i % 3) * 0.2, 0.7 - Math.floor(i / 3) * 0.3, 0.13]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.07, 0.07, 0.05, 12]} /><Mat c="#000" e={i === 4 ? C.naranja : "#5aa9ff"} ei={(Math.floor((f + i * 4) / 12) % 3) ? 0.9 : 2.8} /></mesh>)}
      {[0, 1, 2].map((k) => { const t = ((f / 40 + k / 3) % 1); return <mesh key={k} position={[0, 1.5 + t * 2.4, 0]} scale={0.3 + t}><torusGeometry args={[0.5, 0.012, 8, 32]} /><meshBasicMaterial color={C.naranja} transparent opacity={(1 - t)} /></mesh>; })}
      <pointLight position={[0, 0.5, 1.6]} color="#7fb6ff" intensity={5} distance={7} />
      <pointLight position={[2, 2, 3]} color="#cfe0ff" intensity={6} distance={10} />
    </group>
  );
};

export const Nube: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <group position={[0, 1.0, 0]}>
      {[[-1.2, 0, 0, 0.9], [-0.3, 0.45, 0.1, 1.1], [0.8, 0.2, 0, 1.0], [1.7, -0.1, 0, 0.7], [-0.2, -0.2, 0.2, 1.0]].map(([x, y, z, r], i) => <mesh key={i} position={[x, y, z]}><sphereGeometry args={[r, 24, 24]} /><Mat c="#cfe1f5" e="#4f7fb5" ei={0.5} r={0.9} m={0} /></mesh>)}
      {Array.from({ length: 5 }, (_, i) => { const a = -1.4 + i * 0.7; return [0, 1, 2].map((k) => { const t = ((f / 60 + k / 3 + i * 0.13) % 1); return <mesh key={`${i}${k}`} position={[a * (1 - t) * 1.6, -2.2 + (1 - t) * -0.4 + t * 1.5, (i - 2) * 0.3 * (1 - t)]}><sphereGeometry args={[0.05, 8, 8]} /><Mat c="#000" e={C.naranja} ei={3} /></mesh>; }); })}
      <pointLight position={[0, 2, 3]} color="#cfe0ff" intensity={9} distance={12} />
    </group>
  );
};

export const Ojo: React.FC = () => {
  const f = useCurrentFrame();
  const mira = Math.sin(f / 45) * 0.25, parp = (Math.floor(f / 70) % 2 === 0 && (f % 70) < 4) ? 0.1 : 1;
  return (
    <group position={[0, 0.8, 0]}>
      <mesh scale={[1, parp, 1]}><sphereGeometry args={[1.3, 40, 40]} /><Mat c="#e9e2d8" r={0.4} m={0} /></mesh>
      <group position={[mira, 0.05, 1.27]} scale={[1, parp, 1]}>
        <mesh position={[0, 0, 0.0]}><circleGeometry args={[0.6, 40]} /><Mat c="#8a3510" e={C.naranja} ei={0.9} /></mesh>
        <mesh position={[0, 0, 0.02]}><circleGeometry args={[0.26, 30]} /><Mat c="#000" /></mesh>
      </group>
      <pointLight position={[0, 1, 3]} color="#ffd9b0" intensity={8} distance={9} />
    </group>
  );
};

export const TvPlay: React.FC = () => {
  const f = useCurrentFrame();
  const sel = Math.floor(f / 24) % 6;
  const tri = new THREE.Shape(); tri.moveTo(-0.3, -0.4); tri.lineTo(0.5, 0); tri.lineTo(-0.3, 0.4); tri.lineTo(-0.3, -0.4);
  const cols = ["#b83a2e", "#2e6fb8", "#3aa86a", "#b8892e", "#7a3ab8", "#2eb0b8"];
  return (
    <group position={[0, 0.5, 0]}>
      <mesh><RB args={[4.8, 2.8, 0.1]} /><Mat c="#0b0c0f" m={0.7} r={0.3} /></mesh>
      <mesh position={[0, 0, 0.06]}><planeGeometry args={[4.6, 2.62]} /><Mat c="#030609" e="#16243a" ei={0.7} /></mesh>
      {cols.map((c, i) => <mesh key={i} position={[-1.5 + (i % 3) * 1.5, 0.45 - Math.floor(i / 3) * 1.0, 0.08]} scale={i === sel ? 1.12 : 1}><RB args={[1.3, 0.8, 0.02]} /><Mat c="#000" e={c} ei={i === sel ? 2.2 : 0.8} /></mesh>)}
      <mesh position={[-1.5 + (sel % 3) * 1.5, 0.45 - Math.floor(sel / 3) * 1.0, 0.11]}><extrudeGeometry args={[tri, { depth: 0.02, bevelEnabled: false }]} /><Mat c="#fff" e="#fff" ei={1.6} /></mesh>
      <pointLight position={[0, 0, 3]} color="#6fa8ff" intensity={5} distance={9} />
    </group>
  );
};
