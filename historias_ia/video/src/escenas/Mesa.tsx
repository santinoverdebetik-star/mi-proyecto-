import React, { useMemo } from "react";
import { random, useCurrentFrame } from "remotion";
import * as THREE from "three";
import { Caja, M, Plano, useLienzo } from "./Salas";
import type { Cam, V3 } from "./Salas";

/* ESCENAS DE MESA (macro, como el video de referencia 3): una mesa de madera en penumbra calida con un objeto protagonista que ilustra lo que dice el narrador
   (reloj digital, router, laptop, ROBOT = la IA, hilera de cajitas con LEDs, telefono, cerradura con llave, papeles). Todo procedural. */
const rr = (s: string, k: string) => random(`${s}|${k}`);
const pick = <T,>(s: string, k: string, a: T[]): T => a[Math.floor(rr(s, k) * a.length) % a.length];
export const PROPS_MESA = ["reloj", "router", "laptop", "robot", "cajas", "telefono", "llave", "papeles"];

const Brillo: React.FC<{ p: V3; c: string; s?: number; o?: number }> = ({ p, c, s = 0.6, o = 0.9 }) => {
  const tex = useMemo(() => { const cv = document.createElement("canvas"); cv.width = cv.height = 64; const x = cv.getContext("2d")!; const g = x.createRadialGradient(32, 32, 0, 32, 32, 32); g.addColorStop(0, "rgba(255,255,255,1)"); g.addColorStop(0.25, "rgba(255,255,255,0.45)"); g.addColorStop(1, "rgba(255,255,255,0)"); x.fillStyle = g; x.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(cv); }, []);
  return <sprite position={p} scale={[s, s, 1]}><spriteMaterial map={tex} color={c} blending={THREE.AdditiveBlending} transparent depthWrite={false} opacity={o} toneMapped={false} /></sprite>;
};
const Led: React.FC<{ p: V3; c: string; s?: number }> = ({ p, c, s = 0.012 }) => (
  <group position={p}><mesh><sphereGeometry args={[s, 10, 10]} /><meshLambertMaterial color="#000" emissive={c} emissiveIntensity={5} /></mesh><Brillo p={[0, 0, 0.01]} c={c} s={s * 18} /></group>);

const Reloj: React.FC<{ s: string }> = ({ s }) => {
  const hh = 0; const f = useCurrentFrame();
  const tex = useLienzo(256, 128, (ctx, W, H, fr) => { ctx.fillStyle = "#1a0505"; ctx.fillRect(0, 0, W, H); const seg = 47 - Math.floor(fr / 30); const t = `00:${String(Math.max(0, seg)).padStart(2, "0")}`; ctx.font = "bold 96px monospace"; ctx.textAlign = "center"; ctx.fillStyle = "#ff3a2a"; ctx.shadowColor = "#ff3a2a"; ctx.shadowBlur = 20; ctx.fillText(t, W / 2, H * 0.74); });
  const c = pick(s, "rc", ["#ff3a2a", "#35d9ff", "#ffb347"]);
  return (<group position={[0, 0.79, 0]}>
    <Caja p={[0, 0.14, 0]} s={[0.62, 0.3, 0.22]} c="#111214" /><Plano p={[0, 0.15, 0.113]} w={0.5} h={0.2} tex={tex} />
    <Brillo p={[0, 0.15, 0.2]} c={c} s={1.6} o={0.55} /><pointLight position={[0, 0.2, 0.5]} color={c} intensity={4} distance={3} decay={2} />
    <group position={[0.55, 0.07, 0.1]}><mesh><cylinderGeometry args={[0.07, 0.06, 0.14, 16]} /><M c="#d8d4cc" /></mesh></group>
  </group>);
};
const Router: React.FC<{ s: string }> = ({ s }) => {
  const c = pick(s, "lc", ["#35d9ff", "#4aff9a", "#ffb347"]);
  return (<group position={[0, 0.79, 0]}>
    <Caja p={[0, 0.04, 0]} s={[0.62, 0.07, 0.36]} c="#16181c" />
    {[-0.22, 0, 0.22].map((x, i) => <mesh key={i} position={[x, 0.24, -0.12]} rotation={[0, 0, (i - 1) * 0.12]}><boxGeometry args={[0.018, 0.36, 0.018]} /><M c="#0c0d0f" /></mesh>)}
    {[0, 1, 2, 3, 4].map((i) => <Led key={i} p={[-0.2 + i * 0.1, 0.06, 0.181]} c={i % 3 === 0 ? c : "#4aff9a"} s={0.013} />)}
    <pointLight position={[0, 0.2, 0.5]} color={c} intensity={3.5} distance={3} decay={2} />
    {[0, 1, 2].map((i) => <Caja key={i} p={[-0.2 + i * 0.2, 0.012, 0.34]} s={[0.012, 0.012, 0.7]} c={["#2a6aff", "#e8c820", "#2a6aff"][i]} />)}
  </group>);
};
const Laptop: React.FC<{ s: string }> = ({ s }) => {
  const tex = useLienzo(512, 320, (ctx, W, H, f) => { ctx.fillStyle = "#04080c"; ctx.fillRect(0, 0, W, H); ctx.font = "22px monospace"; const off = Math.floor(f / 6);
    for (let i = 0; i < 11; i++) { const n = i + off; const k = random(`${s}lp${n}`); ctx.fillStyle = k > 0.8 ? "#ffb347" : k > 0.3 ? "#6fe8ff" : "#ffffff"; ctx.globalAlpha = 0.55 + 0.45 * random(`${s}la${n}`); ctx.fillText((i % 3 === 0 ? "$ " : "  ") + Array.from({ length: 6 }, (_, j) => Math.floor(random(`${s}lq${n}${j}`) * 65536).toString(16)).join(" "), 18, 36 + i * 26); } });
  return (<group position={[0, 0.79, 0]}>
    <Caja p={[0, 0.012, 0.05]} s={[0.72, 0.024, 0.5]} c="#24262b" m={0.5} />
    <group position={[0, 0.02, -0.2]} rotation={[-0.22, 0, 0]}><Caja p={[0, 0.25, 0]} s={[0.72, 0.46, 0.02]} c="#1c1e22" /><Plano p={[0, 0.25, 0.012]} w={0.66} h={0.4} tex={tex} /></group>
    <pointLight position={[0, 0.4, 0.5]} color="#6fe8ff" intensity={4} distance={3.5} decay={2} />
  </group>);
};
/* ROBOT: la IA. Cuerpo, cabeza con visor y ojos luminosos, antena, brazos; la cabeza gira lento. */
const Robot: React.FC<{ s: string }> = ({ s }) => {
  const f = useCurrentFrame(); const giro = Math.sin(f / 40) * 0.35; const c = pick(s, "ec", ["#35d9ff", "#4aff9a", "#ff7a2f"]); const cuerpo = pick(s, "bc", ["#c9ccd2", "#8a9098", "#d8d2c4"]);
  const parp = Math.floor(f / 55) % 9 === 0 ? 0.1 : 1;
  return (<group position={[0, 0.79, 0]} scale={1.5}>
    <Caja p={[0, 0.34, 0]} s={[0.42, 0.44, 0.26]} c={cuerpo} m={0.3} /><Caja p={[0, 0.34, 0.131]} s={[0.22, 0.16, 0.01]} c="#15181c" /><Led p={[0, 0.36, 0.14]} c={c} s={0.014} />
    {[-1, 1].map((l) => <group key={l}><mesh position={[l * 0.28, 0.36, 0]} rotation={[0, 0, l * 0.18]}><cylinderGeometry args={[0.04, 0.04, 0.38, 12]} /><M c="#6a7078" /></mesh><mesh position={[l * 0.31, 0.15, 0]}><sphereGeometry args={[0.055, 12, 12]} /><M c="#4a5058" /></mesh>
      <mesh position={[l * 0.12, 0.06, 0]}><cylinderGeometry args={[0.055, 0.055, 0.14, 12]} /><M c="#4a5058" /></mesh></group>)}
    <group position={[0, 0.7, 0]} rotation={[0, giro, 0]}>
      <Caja p={[0, 0.0, 0]} s={[0.36, 0.28, 0.28]} c={cuerpo} m={0.3} /><Caja p={[0, 0.01, 0.145]} s={[0.3, 0.14, 0.012]} c="#06080b" />
      <mesh position={[-0.07, 0.015, 0.153]}><sphereGeometry args={[0.028, 12, 12]} /><meshLambertMaterial color="#000" emissive={c} emissiveIntensity={6 * parp} /></mesh>
      <mesh position={[0.07, 0.015, 0.153]}><sphereGeometry args={[0.028, 12, 12]} /><meshLambertMaterial color="#000" emissive={c} emissiveIntensity={6 * parp} /></mesh>
      <Brillo p={[-0.07, 0.015, 0.2]} c={c} s={0.2} o={0.9 * parp} /><Brillo p={[0.07, 0.015, 0.2]} c={c} s={0.2} o={0.9 * parp} />
      <mesh position={[0, 0.22, 0]}><cylinderGeometry args={[0.01, 0.01, 0.18, 8]} /><M c="#2a2c30" /></mesh><mesh position={[0, 0.32, 0]}><sphereGeometry args={[0.025, 10, 10]} /><meshLambertMaterial color="#000" emissive={c} emissiveIntensity={4} /></mesh>
    </group>
    <pointLight position={[0, 0.8, 0.6]} color={c} intensity={5} distance={3.5} decay={2} />
  </group>);
};
/* HILERA DE CAJITAS (como la mesa de pruebas del video): cajas negras con LED, cables azules/amarillos hacia el borde. */
const Cajas: React.FC<{ s: string }> = ({ s }) => {
  const n = 8 + Math.floor(rr(s, "n") * 8); const c = pick(s, "lc", ["#35d9ff", "#4aff9a"]); const f = useCurrentFrame();
  return (<group position={[0, 0.79, 0]}>
    {Array.from({ length: n }, (_, i) => { const x = (i - (n - 1) / 2) * 0.3; const on = random(`${s}on${i}${Math.floor(f / 20)}`) > 0.3;
      return (<group key={i}><Caja p={[x, 0.03, -0.05]} s={[0.22, 0.055, 0.17]} c="#101114" m={0.4} /><Led p={[x - 0.07, 0.062, 0.04]} c={on ? c : "#0a3a3a"} s={0.009} />
        <Caja p={[x, 0.008, 0.2]} s={[0.012, 0.012, 0.52]} c={i % 2 ? "#2a6aff" : "#e8c820"} /><Caja p={[x + 0.02, 0.008, 0.2]} s={[0.012, 0.012, 0.52]} c="#6aa0e8" /></group>); })}
    <pointLight position={[0, 0.3, 0.6]} color={c} intensity={4} distance={4} decay={2} />
  </group>);
};
const Telefono: React.FC<{ s: string }> = ({ s }) => {
  const tex = useLienzo(160, 320, (ctx, W, H, f) => { ctx.fillStyle = "#07101a"; ctx.fillRect(0, 0, W, H); for (let i = 0; i < 5; i++) { ctx.fillStyle = `rgba(53,217,255,${0.35 + 0.4 * Math.abs(Math.sin((f + i * 20) / 25))})`; ctx.fillRect(14, 30 + i * 54, W - 28, 40); ctx.fillStyle = "#fff"; ctx.fillRect(24, 40 + i * 54, 40 + random(s + i) * 80, 6); } });
  return (<group position={[0, 0.79, 0]} rotation={[-Math.PI / 2 + 0.28, 0, 0.2]}>
    <Caja p={[0, 0, 0]} s={[0.17, 0.34, 0.012]} c="#0b0c0f" /><Plano p={[0, 0, 0.0071]} w={0.155} h={0.32} tex={tex} /><pointLight position={[0, 0, 0.3]} color="#6fe8ff" intensity={3.5} distance={2.5} decay={2} />
  </group>);
};
const Llave: React.FC<{ s: string }> = ({ s }) => (
  <group position={[0, 1.0, -0.3]}>
    <Caja p={[0, 0, -0.02]} s={[0.6, 0.6, 0.04]} c="#1e1a16" />
    <mesh rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.14, 0.14, 0.04, 28]} /><meshLambertMaterial color="#c8a050" emissive="#4a3410" emissiveIntensity={0.6} /></mesh>
    <mesh position={[0, 0, 0.03]}><circleGeometry args={[0.035, 16]} /><meshBasicMaterial color="#000" /></mesh>
    <group position={[0.05, -0.04, 0.12]} rotation={[0, 0.6, 0.5]}>
      <mesh rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.012, 0.012, 0.22, 10]} /><meshLambertMaterial color="#d6b25a" emissive="#4a3410" emissiveIntensity={0.5} /></mesh>
      <mesh position={[0, 0, 0.14]}><torusGeometry args={[0.05, 0.014, 10, 24]} /><meshLambertMaterial color="#d6b25a" emissive="#4a3410" emissiveIntensity={0.5} /></mesh>
    </group>
    <pointLight position={[0.3, 0.2, 0.5]} color="#ffb066" intensity={7} distance={3} decay={2} />
  </group>);
const Papeles: React.FC<{ s: string }> = ({ s }) => (
  <group position={[0, 0.79, 0]}>
    {Array.from({ length: 7 }, (_, i) => <Caja key={i} p={[(rr(s, "x" + i) - 0.5) * 0.08, 0.004 + i * 0.004, (rr(s, "z" + i) - 0.5) * 0.06]} s={[0.42, 0.003, 0.3]} c="#efe9da" rot={[0, (rr(s, "r" + i) - 0.5) * 0.5, 0]} />)}
    <group position={[0.42, 0.065, 0.05]}><mesh><cylinderGeometry args={[0.055, 0.05, 0.12, 18]} /><M c="#e8e4dc" /></mesh></group>
    <group position={[-0.42, 0.012, 0.08]}><mesh rotation={[Math.PI / 2, 0, 0]} position={[-0.04, 0, 0]}><torusGeometry args={[0.035, 0.004, 8, 20]} /><M c="#1a1a1a" /></mesh><mesh rotation={[Math.PI / 2, 0, 0]} position={[0.04, 0, 0]}><torusGeometry args={[0.035, 0.004, 8, 20]} /><M c="#1a1a1a" /></mesh></group>
    <pointLight position={[0.3, 0.7, 0.4]} color="#ffb066" intensity={8} distance={3.5} decay={2} />
  </group>);

const MADERA = ["#5a3a22", "#4a3020", "#6a4a2e", "#3a281a", "#5a5046"];
export const MesaG: React.FC<{ s: string; prop: string }> = ({ s, prop }) => {
  const madera = pick(s, "ma", MADERA); const pared = s.startsWith("A") ? "#0c1220" : pick(s, "pa", ["#14181e", "#1a1612", "#101820", "#181418"]); const lampara = s.startsWith("A") ? "#ff3a2a" : pick(s, "la", ["#ffb066", "#ffc880", "#ff9a52"]);
  const fondo = useLienzo(512, 256, (ctx, W, H) => { const g = ctx.createRadialGradient(W * (0.2 + 0.6 * rr(s, "gx")), H * 0.4, 5, W / 2, H / 2, W * 0.7); g.addColorStop(0, "rgba(255,170,90,0.55)"); g.addColorStop(1, "rgba(0,0,0,0)"); ctx.fillStyle = "#0a0b0e"; ctx.fillRect(0, 0, W, H); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); });
  const P = { reloj: Reloj, router: Router, laptop: Laptop, robot: Robot, cajas: Cajas, telefono: Telefono, llave: Llave, papeles: Papeles }[prop as "reloj"] ?? Papeles;
  return (
    <group>
      <Caja p={[0, 0.75, 0]} s={[prop === "cajas" ? 7 : 4.2, 0.08, 2.6]} c={madera} r={0.55} />
      <mesh position={[0, 0, 0]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[30, 30]} /><meshLambertMaterial color="#0b0c0f" /></mesh>
      <mesh position={[0, 2.2, -1.5]}><planeGeometry args={[14, 5]} /><meshLambertMaterial color={pared} /></mesh>
      <Plano p={[0, 1.6, -1.49]} w={9} h={3.4} tex={fondo} />
      <mesh position={[rr(s, "lx") > 0.5 ? 1.4 : -1.4, 1.45, -0.98]}><sphereGeometry args={[0.09, 12, 12]} /><meshLambertMaterial color="#fff" emissive={lampara} emissiveIntensity={2.2} /></mesh>
      <pointLight position={[rr(s, "lx") > 0.5 ? 1.4 : -1.4, 1.5, -0.6]} color={lampara} intensity={6} distance={6} decay={2} />
      <P s={s} />
      <ambientLight intensity={0.1} color="#8090b0" />
    </group>);
};
export const infoMesa = (s: string, prop: string) => ({ zona: { x: [-0.9, 0.9] as [number, number], y: [0.9, 1.35] as [number, number], z: [0.9, 2.3] as [number, number] }, ancho: prop === "cajas" ? 3 : 0.6 });
export const camMesa = (s: string, prop: string): Cam => {
  const rob = prop === "robot"; const kz = rob ? 2.0 : 1.0; const tgt: V3 = prop === "llave" ? [0, 1.0, -0.3] : rob ? [0, 1.4, 0] : [0, 0.88, 0]; const k = Math.floor(rr(s, "c") * 5); const a = rr(s, "a"), b = rr(s, "b");
  const W = prop === "cajas" ? 2.4 : rob ? 1.0 : 0.6; const t2: V3 = [tgt[0] + (rr(s, "j") - 0.5) * 0.3, tgt[1] + (rr(s, "j2") - 0.5) * 0.1, tgt[2]];
  const yb = rob ? 1.3 : 0.92;
  if (k === 0) return { desde: [W * (a - 0.5), yb + 0.03, 1.5 * kz], hasta: [W * (b - 0.5) * 0.4, yb, 0.75 * kz], mira: tgt, miraHasta: t2 };           // avance macro
  if (k === 1) return { desde: [-W * 0.5, yb, 1.0 * kz], hasta: [W * 0.5, yb + 0.03, 1.0 * kz], mira: tgt, miraHasta: t2 };                                // travelling lateral
  if (k === 2) return { desde: [W * 0.7, yb + 0.15, 1.3 * kz], hasta: [-W * 0.7, yb + 0.05, 1.1 * kz], mira: t2, miraHasta: tgt };                          // arco
  if (k === 3) return { desde: [0, yb + 0.35, 0.9 * kz], hasta: [0, yb - 0.04, 1.2 * kz], mira: tgt, miraHasta: t2 };                                       // bajada
  return { desde: [W * 0.3, yb - 0.02, 0.7 * kz], hasta: [-W * 0.3, yb + 0.1, 1.5 * kz], mira: tgt, miraHasta: t2 };                                       // retroceso
};
