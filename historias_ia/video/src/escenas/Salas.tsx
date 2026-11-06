import React, { useLayoutEffect, useMemo } from "react";
import { random, useCurrentFrame } from "remotion";
import * as THREE from "three";
import { RB } from "./Realismo";
import mapa from "../../public/mapa.json";

/* Salas 3D completas con travelling lento (como los planos de ambiente del video de referencia): sala de casa de noche, laboratorio de computadoras viejas,
   pasillo de servidores y sala con un mapamundi. Todo procedural. Unidades ~ metros, suelo en y = 0. */

type V3 = [number, number, number];
const M: React.FC<{ c: string; r?: number; m?: number; e?: string; ei?: number }> = ({ c, r = 0.75, m = 0.05, e, ei = 0 }) => <meshStandardMaterial color={c} roughness={r} metalness={m} emissive={e ?? "#000000"} emissiveIntensity={ei} />;
const Caja: React.FC<{ p: V3; s: V3; c: string; r?: number; m?: number; e?: string; ei?: number; rot?: V3 }> = ({ p, s, c, r, m, e, ei, rot }) => (
  <mesh position={p} rotation={rot}><RB args={s} /><M c={c} r={r} m={m} e={e} ei={ei} /></mesh>);

/** textura de canvas que se redibuja en cada fotograma (pantallas, mapa, letreros) */
function useLienzo(W: number, H: number, dibujar: (ctx: CanvasRenderingContext2D, W: number, H: number, f: number) => void) {
  const f = useCurrentFrame();
  const cv = useMemo(() => { const c = document.createElement("canvas"); c.width = W; c.height = H; return c; }, [W, H]);
  const tex = useMemo(() => { const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t; }, [cv]);
  useLayoutEffect(() => { dibujar(cv.getContext("2d")!, W, H, f); tex.needsUpdate = true; });
  return tex;
}
const Plano: React.FC<{ p: V3; w: number; h: number; tex: THREE.Texture; rot?: V3 }> = ({ p, w, h, tex, rot }) => (
  <mesh position={p} rotation={rot}><planeGeometry args={[w, h]} /><meshBasicMaterial map={tex} toneMapped={false} /></mesh>);

/* ---------- dibujos de pantallas ---------- */
const hex = (s: string, n: number) => Array.from({ length: n }, (_, i) => Math.floor(random(s + i) * 65536).toString(16).padStart(4, "0")).join(" ");
const dibVerde = (sem: string) => (ctx: CanvasRenderingContext2D, W: number, H: number, f: number) => {
  ctx.fillStyle = "#031008"; ctx.fillRect(0, 0, W, H); ctx.font = "26px monospace";
  const off = Math.floor(f / 5);
  for (let i = 0; i < 11; i++) { const n = i + off; ctx.fillStyle = i === 10 ? "#7dffb0" : "#2fe07a"; ctx.globalAlpha = 0.55 + 0.45 * random(sem + "a" + n); ctx.fillText((i % 3 === 0 ? "> " : "  ") + hex(sem + n, 1 + Math.floor(random(sem + "l" + n) * 4)), 22, 40 + i * 31); }
  ctx.globalAlpha = 1; if (Math.floor(f / 8) % 2) { ctx.fillStyle = "#7dffb0"; ctx.fillRect(22, 40 + 10 * 31 - 22, 14, 26); }
};
const dibBlanca = (sem: string) => (ctx: CanvasRenderingContext2D, W: number, H: number) => {
  ctx.fillStyle = "#e9eef5"; ctx.fillRect(0, 0, W, H); ctx.fillStyle = "#2a5bd7"; ctx.fillRect(0, 0, W, 34);
  for (let i = 0; i < 9; i++) { ctx.fillStyle = "#566"; ctx.fillRect(24, 64 + i * 36, 120 + random(sem + i) * 330, 12); }
};
export const dibRoja = (ctx: CanvasRenderingContext2D, W: number, H: number, f: number) => {
  const g = ctx.createRadialGradient(W / 2, H / 2, 20, W / 2, H / 2, W * 0.7); g.addColorStop(0, "#c4162a"); g.addColorStop(1, "#4a0610"); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = "#f3e7cf"; ctx.fillRect(W * 0.14, H * 0.2, W * 0.72, H * 0.58); ctx.fillStyle = "#2a5bd7"; ctx.fillRect(W * 0.14, H * 0.2, W * 0.72, 22);
  for (let i = 0; i < 5; i++) { ctx.fillStyle = "#3a3a3a"; ctx.fillRect(W * 0.18, H * 0.34 + i * 34, W * (0.25 + 0.4 * random("r" + i)), 10); }
  if (Math.floor(f / 8) % 2) { ctx.fillStyle = "#111"; ctx.fillRect(W * 0.18 + 90, H * 0.34 + 4 * 34 - 4, 12, 20); }
};
const dibLeds = (ctx: CanvasRenderingContext2D, W: number, H: number, f: number) => {
  ctx.fillStyle = "#06080b"; ctx.fillRect(0, 0, W, H);
  for (let r = 0; r < 14; r++) { ctx.fillStyle = "#12161c"; ctx.fillRect(10, 10 + r * 34, W - 20, 28);
    for (let k = 0; k < 8; k++) { const q = random(`l${r}_${k}_${Math.floor(f / (6 + r % 4))}`); ctx.fillStyle = q > 0.86 ? "#ffb347" : q > 0.35 ? "#35ff8a" : "#16331f"; ctx.fillRect(24 + k * 30, 18 + r * 34, 14, 10); } }
};
const proy = (lon: number, lat: number, W: number, H: number): [number, number] => [(lon + 180) / 360 * W, (90 - lat) / 180 * H];
const PUNTOS = Array.from({ length: 70 }, (_, i) => ({ lon: -125 + random("mo" + i) * 290, lat: -35 + random("ma" + i) * 90, t: random("mt" + i) }));
const dibMapa = (ctx: CanvasRenderingContext2D, W: number, H: number, f: number) => {
  ctx.fillStyle = "#34567d"; ctx.fillRect(0, 0, W, H); ctx.fillStyle = "#dccb9f"; ctx.strokeStyle = "#a99768"; ctx.lineWidth = 1.5;
  for (const poly of mapa as number[][][]) { ctx.beginPath(); poly.forEach(([lo, la], i) => { const [x, y] = proy(lo, la, W, H); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }); ctx.closePath(); ctx.fill(); ctx.stroke(); }
  const n = Math.min(PUNTOS.length, Math.floor(f / 2.2));
  PUNTOS.slice(0, n).forEach((p, i) => { const [x, y] = proy(p.lon, p.lat, W, H); const pulso = 0.5 + 0.5 * Math.sin(f / 6 + i);
    ctx.fillStyle = "#ff5a1f"; ctx.globalAlpha = 0.28 + 0.2 * pulso; ctx.beginPath(); ctx.arc(x, y, 15 + 7 * pulso, 0, 7); ctx.fill(); ctx.globalAlpha = 1; ctx.beginPath(); ctx.arc(x, y, 6, 0, 7); ctx.fill(); });
};
const dibBarras = (ctx: CanvasRenderingContext2D, W: number, H: number, f: number) => {
  ctx.fillStyle = "#0a0f16"; ctx.fillRect(0, 0, W, H);
  for (let i = 0; i < 26; i++) { const h = (0.18 + 0.7 * Math.abs(Math.sin(i * 0.55 + 1))) * H * 0.75 * Math.min(1, f / 60 + 0.3); ctx.fillStyle = i === 17 ? "#ffb347" : "#3f8fe0"; ctx.fillRect(14 + i * 19, H - 20 - h, 14, h); }
};
const dibLetrero = (txt: string, sub: string) => (ctx: CanvasRenderingContext2D, W: number, H: number) => {
  ctx.fillStyle = "#2b2f36"; ctx.fillRect(0, 0, W, H); ctx.fillStyle = "#e8e2d0"; ctx.textAlign = "center"; ctx.font = "bold 52px sans-serif"; ctx.fillText(txt, W / 2, H * 0.52); ctx.font = "34px sans-serif"; ctx.fillText(sub, W / 2, H * 0.82);
};
const dibPizarra = (ctx: CanvasRenderingContext2D, W: number, H: number) => {
  ctx.fillStyle = "#f2f1ea"; ctx.fillRect(0, 0, W, H); ctx.strokeStyle = "#556"; ctx.lineWidth = 4; ctx.font = "italic 50px cursive"; ctx.fillStyle = "#334";
  for (let i = 0; i < 6; i++) { ctx.beginPath(); ctx.moveTo(40, 90 + i * 62); for (let x = 40; x < 40 + 220 + random("pz" + i) * 520; x += 14) ctx.lineTo(x, 90 + i * 62 + Math.sin(x * 0.2 + i) * 6); ctx.stroke(); }
  ctx.strokeStyle = "#d33"; ctx.strokeRect(W * 0.62, 70, W * 0.32, 230); ctx.beginPath(); ctx.moveTo(W * 0.66, 120); ctx.lineTo(W * 0.7, 160); ctx.moveTo(W * 0.7, 120); ctx.lineTo(W * 0.66, 160); ctx.stroke();
};

/* ---------- muebles y piezas ---------- */
const MonitorCRT: React.FC<{ p: V3; rotY?: number; tex: THREE.Texture; s?: number }> = ({ p, rotY = 0, tex, s = 1 }) => (
  <group position={p} rotation={[0, rotY, 0]} scale={s}>
    <Caja p={[0, 0.27, 0]} s={[0.5, 0.42, 0.4]} c="#b9ae9a" r={0.6} />
    <Caja p={[0, 0.27, -0.3]} s={[0.36, 0.3, 0.28]} c="#aaa08c" r={0.6} />
    <Caja p={[0, 0.05, 0.02]} s={[0.26, 0.05, 0.26]} c="#a89e8a" r={0.6} />
    <Plano p={[0, 0.285, 0.206]} w={0.4} h={0.32} tex={tex} />
  </group>);
const Escritorio: React.FC<{ p: V3; ancho?: number }> = ({ p, ancho = 1.5 }) => (
  <group position={p}>
    <Caja p={[0, 0.72, 0]} s={[ancho, 0.045, 0.75]} c="#d6d0c2" r={0.55} />
    {[[-1, -1], [1, -1], [-1, 1], [1, 1]].map(([a, b], i) => <Caja key={i} p={[a * (ancho / 2 - 0.05), 0.36, b * 0.32]} s={[0.05, 0.72, 0.05]} c="#8d8f94" m={0.5} r={0.4} />)}
    <Caja p={[0, 0.755, 0.2]} s={[0.46, 0.025, 0.16]} c="#cfc7b4" r={0.6} />
  </group>);
const Silla: React.FC<{ p: V3; rotY?: number }> = ({ p, rotY = 0 }) => (
  <group position={p} rotation={[0, rotY, 0]}>
    <Caja p={[0, 0.48, 0]} s={[0.48, 0.07, 0.48]} c="#16181d" r={0.8} /><Caja p={[0, 0.78, -0.22]} s={[0.46, 0.5, 0.07]} c="#16181d" r={0.8} />
    <mesh position={[0, 0.24, 0]}><cylinderGeometry args={[0.04, 0.04, 0.46, 10]} /><M c="#2a2c31" m={0.6} r={0.4} /></mesh>
    <mesh position={[0, 0.03, 0]}><cylinderGeometry args={[0.28, 0.28, 0.04, 14]} /><M c="#2a2c31" m={0.6} r={0.4} /></mesh>
  </group>);
const Planta: React.FC<{ p: V3 }> = ({ p }) => (
  <group position={p}><mesh position={[0, 0.2, 0]}><cylinderGeometry args={[0.2, 0.15, 0.4, 14]} /><M c="#7a4b36" r={0.8} /></mesh>
    {[0, 1, 2, 3, 4].map((i) => <mesh key={i} position={[Math.sin(i * 1.3) * 0.12, 0.6 + i * 0.1, Math.cos(i * 1.3) * 0.12]} scale={[1, 1.5, 1]}><sphereGeometry args={[0.17, 10, 10]} /><M c="#2f5d34" r={0.8} /></mesh>)}</group>);
const Cuarto: React.FC<{ w: number; d: number; h: number; piso: string; pared: string; techo?: string; z0?: number }> = ({ w, d, h, piso, pared, techo = "#2a2a2e", z0 = 0 }) => (
  <group position={[0, 0, z0]}>
    <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow><planeGeometry args={[w, d]} /><M c={piso} r={0.45} m={0.05} /></mesh>
    <mesh position={[0, h, 0]} rotation={[Math.PI / 2, 0, 0]}><planeGeometry args={[w, d]} /><M c={techo} r={0.9} /></mesh>
    <mesh position={[0, h / 2, -d / 2]}><planeGeometry args={[w, h]} /><M c={pared} r={0.9} /></mesh>
    <mesh position={[0, h / 2, d / 2]} rotation={[0, Math.PI, 0]}><planeGeometry args={[w, h]} /><M c={pared} r={0.9} /></mesh>
    <mesh position={[-w / 2, h / 2, 0]} rotation={[0, Math.PI / 2, 0]}><planeGeometry args={[d, h]} /><M c={pared} r={0.9} /></mesh>
    <mesh position={[w / 2, h / 2, 0]} rotation={[0, -Math.PI / 2, 0]}><planeGeometry args={[d, h]} /><M c={pared} r={0.9} /></mesh>
  </group>);
const Panel: React.FC<{ p: V3; s?: V3; ei?: number; c?: string }> = ({ p, s = [1.3, 0.05, 0.4], ei = 3, c = "#fff4e0" }) => <mesh position={p}><boxGeometry args={s} /><meshStandardMaterial color="#ffffff" emissive={c} emissiveIntensity={ei} toneMapped={false} /></mesh>;

/* ================= 1. SALA DE CASA DE NOCHE ================= */
export const SalaHogar: React.FC = () => {
  const f = useCurrentFrame();
  const led = Math.floor(f / 14) % 2 === 0;
  const tv = useLienzo(256, 144, (ctx, W, H) => { const g = ctx.createLinearGradient(0, 0, W, H); g.addColorStop(0, "#07101c"); g.addColorStop(1, "#02040a"); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); });
  return (
    <group>
      <Cuarto w={9} d={8} h={2.9} piso="#5e4430" pared="#7d7466" techo="#4a4640" z0={-0.5} />
      {/* ventana nocturna */}
      <mesh position={[-2.6, 1.7, -4.47]}><planeGeometry args={[2.4, 1.4]} /><meshBasicMaterial color="#1c3a6a" toneMapped={false} /></mesh>
      <Caja p={[-2.6, 1.7, -4.46]} s={[2.6, 0.08, 0.06]} c="#e8e2d6" /><Caja p={[-2.6, 0.98, -4.46]} s={[2.6, 0.08, 0.1]} c="#e8e2d6" /><Caja p={[-2.6, 1.7, -4.45]} s={[0.05, 1.4, 0.05]} c="#e8e2d6" />
      <pointLight position={[-2.6, 1.7, -3.2]} color="#7fa8ff" intensity={9} distance={9} decay={2} />
      {/* mueble de TV + TV + caja */}
      <Caja p={[0.9, 0.3, -4.1]} s={[2.1, 0.6, 0.5]} c="#3a2b20" r={0.6} />
      <Caja p={[0.9, 1.17, -4.1]} s={[1.6, 0.92, 0.07]} c="#0b0c0f" r={0.3} m={0.5} />
      <Plano p={[0.9, 1.17, -4.06]} w={1.5} h={0.84} tex={tv} />
      <Caja p={[0.15, 0.63, -4.0]} s={[0.36, 0.06, 0.24]} c="#15171b" r={0.35} m={0.4} />
      <mesh position={[0.3, 0.665, -3.89]}><sphereGeometry args={[0.012, 10, 10]} /><meshStandardMaterial color="#000" emissive={led ? "#ff5a1f" : "#3a1205"} emissiveIntensity={led ? 6 : 0.3} toneMapped={false} /></mesh>
      {led && <pointLight position={[0.3, 0.7, -3.7]} color="#ff5a1f" intensity={1.8} distance={2.4} decay={2} />}
      {/* estante con router */}
      <Caja p={[3.4, 1.05, -4.2]} s={[1.2, 0.05, 0.4]} c="#3a2b20" /><Caja p={[3.4, 1.12, -4.2]} s={[0.4, 0.06, 0.24]} c="#e8e8ea" r={0.4} />
      {[0, 1, 2].map((i) => <mesh key={i} position={[3.3 + i * 0.05, 1.155, -4.07]}><sphereGeometry args={[0.008, 8, 8]} /><meshStandardMaterial color="#000" emissive="#35ff8a" emissiveIntensity={4} toneMapped={false} /></mesh>)}
      {/* sofa, mesa, alfombra, lampara, planta */}
      <Caja p={[0.2, 0.25, 1.4]} s={[2.6, 0.5, 1.0]} c="#4a4f63" r={0.9} /><Caja p={[0.2, 0.7, 1.82]} s={[2.6, 0.55, 0.22]} c="#444a5e" r={0.9} />
      <Caja p={[-1.25, 0.45, 1.4]} s={[0.22, 0.7, 1.0]} c="#444a5e" r={0.9} /><Caja p={[1.65, 0.45, 1.4]} s={[0.22, 0.7, 1.0]} c="#444a5e" r={0.9} />
      <Caja p={[0.4, 0.2, -1.4]} s={[1.3, 0.04, 0.7]} c="#2d2118" r={0.5} /><Caja p={[0.4, 0.01, -0.6]} s={[3.2, 0.02, 2.4]} c="#5a2d32" r={1} />
      <group position={[-3.1, 0, -1.2]}><mesh position={[0, 0.75, 0]}><cylinderGeometry args={[0.02, 0.02, 1.5, 8]} /><M c="#222" m={0.6} /></mesh>
        <mesh position={[0, 1.55, 0]}><cylinderGeometry args={[0.17, 0.26, 0.3, 18, 1, true]} /><meshStandardMaterial color="#f1d9a8" emissive="#ffc880" emissiveIntensity={1.6} side={THREE.DoubleSide} toneMapped={false} /></mesh></group>
      <pointLight position={[-3.1, 1.5, -1.2]} color="#ffbf70" intensity={11} distance={9} decay={2} />
      <Planta p={[3.7, 0, -3.2]} />
      <ambientLight intensity={0.16} color="#6f82b8" />
      <pointLight position={[0.9, 1.2, -3.0]} color="#7fa8ff" intensity={4} distance={6} decay={2} />
    </group>);
};

/* ================= 2. LABORATORIO DE COMPUTADORAS VIEJAS ================= */
export const SalaLab: React.FC<{ roja?: boolean }> = ({ roja = true }) => {
  const t1 = useLienzo(512, 384, dibVerde("a")), t2 = useLienzo(512, 384, dibBlanca("b")), t3 = useLienzo(512, 384, dibVerde("c")), roj = useLienzo(512, 384, dibRoja);
  const pz = useLienzo(1024, 512, dibPizarra);
  const filas = [-1.2, -3.6, -6.0, -8.4, -10.8];
  return (
    <group>
      <Cuarto w={12} d={18} h={3.3} piso="#8a6a48" pared="#9a917e" techo="#5a5750" z0={-5} />
      <Plano p={[0, 1.75, -13.95]} w={4.4} h={2.2} tex={pz} />
      {[-1, 1].map((lado) => filas.map((z, i) => {
        const x = lado * 2.4; const tex = roja && lado === 1 && i === 1 ? roj : [t1, t2, t3][(i + (lado > 0 ? 1 : 0)) % 3];
        return (<group key={`${lado}_${i}`}>
          <Escritorio p={[x, 0, z]} /><MonitorCRT p={[x, 0.745, z - 0.15]} tex={tex} /><Silla p={[x + 0.1, 0, z + 0.8]} rotY={Math.PI + (i % 3 - 1) * 0.3} />
        </group>);
      }))}
      {[-8, -3, -12.5, 1].map((z, i) => <Panel key={i} p={[0, 3.25, z]} s={[7, 0.05, 0.5]} ei={2.6} c="#fff1d6" />)}
      {[1, -3.5, -8, -12].map((z, i) => <pointLight key={i} position={[0, 3.0, z]} color="#ffdcae" intensity={8} distance={8} decay={2} />)}
      <Planta p={[-5.4, 0, -12.8]} /><Planta p={[5.4, 0, 0.6]} />
      <ambientLight intensity={0.22} color="#d8c9ae" />
    </group>);
};

/* ================= 3. PASILLO DE SERVIDORES CON JAULA ================= */
export const SalaServidores: React.FC = () => {
  const leds = useLienzo(256, 512, dibLeds); const cartel = useLienzo(512, 256, dibLetrero("CLÚSTER DE PRUEBAS", "ACCESO RESTRINGIDO"));
  const racks = Array.from({ length: 11 }, (_, i) => 2.4 - i * 1.25);
  const jaula = useMemo(() => { const p: number[] = []; for (let x = -3; x <= 3.01; x += 0.5) p.push(x, 0, -9, x, 3, -9); for (let y = 0; y <= 3.01; y += 0.5) p.push(-3, y, -9, 3, y, -9);
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(p, 3)); return g; }, []);
  return (
    <group>
      <Cuarto w={7} d={20} h={3.2} piso="#3a3a3d" pared="#9a9b9c" techo="#202225" z0={-5.5} />
      {racks.map((z, i) => [-1, 1].map((lado) => (
        <group key={`${i}_${lado}`}>
          <Caja p={[lado * 2.5, 1.1, z]} s={[0.95, 2.2, 0.95]} c="#14161a" r={0.5} m={0.4} />
          <Plano p={[lado * 2.5 - lado * 0.485, 1.1, z]} w={0.85} h={2.0} tex={leds} rot={[0, lado > 0 ? -Math.PI / 2 : Math.PI / 2, 0]} />
        </group>)))}
      <lineSegments geometry={jaula}><lineBasicMaterial color="#6a6d72" /></lineSegments>
      <Plano p={[0, 2.1, -14.45]} w={3.4} h={1.7} tex={cartel} />
      {[2, -2, -6, -10].map((z, i) => <Panel key={i} p={[0, 3.15, z]} s={[0.5, 0.05, 2.2]} ei={3.2} c="#e6f0ff" />)}
      {[1.5, -4, -10.5].map((z, i) => <pointLight key={i} position={[0, 2.8, z]} color="#cfe0ff" intensity={8} distance={9} decay={2} />)}
      <ambientLight intensity={0.5} color="#a9bddf" />
    </group>);
};

/* ================= 4. SALA CON MAPAMUNDI ================= */
export const SalaMapa: React.FC = () => {
  const m = useLienzo(1024, 512, dibMapa), b = useLienzo(512, 384, dibBarras), v = useLienzo(512, 384, dibVerde("m"));
  return (
    <group>
      <Cuarto w={11} d={9} h={3.4} piso="#5c4a38" pared="#8a7d68" techo="#4d4943" z0={-0.5} />
      <Caja p={[0, 1.8, -4.46]} s={[6.5, 3.3, 0.06]} c="#3a2a1d" /><Plano p={[0, 1.8, -4.42]} w={6.3} h={3.1} tex={m} />
      <Escritorio p={[3.7, 0, -2.2]} ancho={1.8} /><MonitorCRT p={[3.7, 0.745, -2.35]} tex={b} s={1.15} />
      <Escritorio p={[-3.9, 0, -2.0]} ancho={1.8} /><MonitorCRT p={[-3.9, 0.745, -2.15]} tex={v} s={1.0} />
      {[-2.2, 2.2].map((x, i) => <Panel key={i} p={[x, 3.35, -2.2]} s={[1.6, 0.05, 0.6]} ei={3} />)}
      <spotLight position={[0, 3.2, -1.5]} angle={0.7} penumbra={1} intensity={60} distance={9} color="#ffe9c8" target-position={[0, 1.8, -4.4]} />
      <pointLight position={[0, 2.8, 0]} color="#ffd9a8" intensity={7} distance={9} decay={2} />
      <Planta p={[-5, 0, 2.5]} />
      <ambientLight intensity={0.3} color="#bfae92" />
    </group>);
};

/* ---------- planos de camara (travelling lento) ---------- */
type Cam = { desde: V3; hasta: V3; mira: V3; miraHasta?: V3 };
export const CAMS_SALAS: Record<string, Cam> = {
  hogar1: { desde: [0.0, 1.25, 3.6], hasta: [0.5, 1.15, 0.6], mira: [0.8, 1.0, -4.0], miraHasta: [0.5, 0.85, -4.0] },
  hogar2: { desde: [1.5, 0.78, -1.6], hasta: [0.6, 0.72, -3.0], mira: [0.3, 0.64, -4.0], miraHasta: [0.2, 0.64, -4.0] },
  hogar3: { desde: [-3.6, 1.4, 2.0], hasta: [-1.0, 1.35, -0.4], mira: [3.0, 1.1, -4.2], miraHasta: [1.2, 1.0, -4.1] },
  lab1: { desde: [0.0, 1.5, 3.2], hasta: [0.0, 1.3, -2.8], mira: [0, 1.0, -11], miraHasta: [0, 0.95, -13] },
  lab2: { desde: [-0.8, 1.0, -1.6], hasta: [-1.6, 0.98, -4.6], mira: [-2.4, 0.98, -6.2], miraHasta: [-2.4, 0.98, -8] },
  lab3: { desde: [0.2, 1.4, -0.2], hasta: [2.4, 1.03, -3.7], mira: [2.4, 1.03, -4.0], miraHasta: [2.4, 1.03, -4.0] },
  srv1: { desde: [0.0, 1.6, 4.0], hasta: [0.0, 1.45, -3.2], mira: [0, 1.4, -13], miraHasta: [0, 1.5, -14] },
  srv2: { desde: [-1.0, 1.3, 2.0], hasta: [-1.0, 1.25, -4.5], mira: [2.5, 1.25, -2.0], miraHasta: [2.5, 1.25, -10] },
  map1: { desde: [-3.6, 1.7, 2.6], hasta: [2.6, 1.8, 1.6], mira: [-1.0, 1.8, -4.4], miraHasta: [1.5, 1.8, -4.4] },
  map2: { desde: [0.6, 1.9, -0.2], hasta: [-1.2, 2.0, -2.6], mira: [-0.8, 2.0, -4.4], miraHasta: [-1.6, 2.1, -4.4] },
};
export const SALAS_IDS = Object.keys(CAMS_SALAS);
export const EsSala = (o: string) => o in CAMS_SALAS;
export const SalaDe: React.FC<{ id: string }> = ({ id }) => {
  if (id.startsWith("hogar")) return <SalaHogar />;
  if (id.startsWith("lab")) return <SalaLab roja={id === "lab3"} />;
  if (id.startsWith("srv")) return <SalaServidores />;
  return <SalaMapa />;
};
