import React from "react";
import { random, useCurrentFrame } from "remotion";
import * as THREE from "three";
import { Caja, Cuarto, Escritorio, M, MonitorCRT, Panel, Plano, Planta, Silla, useLienzo, dibBarras, dibBlanca, dibCajones, dibCorcho, dibLetrero, dibPizarra, dibVerde, dibRoja } from "./Salas";
import type { Cam, V3 } from "./Salas";
import mapa from "../../public/mapa.json";

/* SALAS GENERATIVAS: cada clip 3D es un ambiente NUEVO (paleta, distribucion, muebles, luces y camara distintos segun una semilla). Regla del usuario: nada de 3D repetido. */
const rr = (s: string, k: string) => random(`${s}|${k}`);
const pick = <T,>(s: string, k: string, a: T[]): T => a[Math.floor(rr(s, k) * a.length) % a.length];
const rango = (s: string, k: string, a: number, b: number) => a + (b - a) * rr(s, k);
const PAL = [
  { pared: "#8a7d68", piso: "#6a5036", techo: "#4b4741", luz: "#ffdcae", amb: "#d8c9ae" }, { pared: "#6f8a7a", piso: "#4a5a4e", techo: "#3a4640", luz: "#d6ffe0", amb: "#a8c8b4" },
  { pared: "#6a7d9a", piso: "#3f4a5e", techo: "#2e3644", luz: "#cfe0ff", amb: "#a9bddf" }, { pared: "#8d6a62", piso: "#573c34", techo: "#3f2f2c", luz: "#ffcfb0", amb: "#d8b9a8" },
  { pared: "#8b8f94", piso: "#4a4c50", techo: "#2f3134", luz: "#f0f4ff", amb: "#b8bcc4" }, { pared: "#9a8454", piso: "#5e4a2a", techo: "#46391f", luz: "#ffd27a", amb: "#d8c08a" },
  { pared: "#7a6a96", piso: "#463d5a", techo: "#2f2a3e", luz: "#e6d0ff", amb: "#b8a8d8" }, { pared: "#5f8f96", piso: "#35525a", techo: "#243a40", luz: "#c8f6ff", amb: "#9cc8d0" },
];
const pal = (s: string) => pick(s, "pal", PAL);
type Info = { zona: { x: [number, number]; y: [number, number]; z: [number, number] }; targets: V3[] };

/* ---------------- HOGAR ---------------- */
const pH = (s: string) => ({ P: pal(s), d: rango(s, "d", 7.5, 9.5), w: rango(s, "w", 8.5, 11), tvX: rango(s, "tv", -1.8, 2.0), vent: pick(s, "v", [-3.4, -1.4, 2.4, 3.4]), sofaX: rango(s, "sx", -1, 1),
  sofaC: pick(s, "sc", ["#4a4f63", "#5a3d3d", "#3d5a4a", "#6a5a3a", "#3a3a40", "#5a4a6a"]), alfC: pick(s, "al", ["#5a2d32", "#2d3f5a", "#3a4a3a", "#4a3a2a"]),
  led: pick(s, "led", ["#ff5a1f", "#35ff8a", "#ff2a2a", "#35d9ff"]), lampX: pick(s, "lx", [-3.5, 3.5]), planta: rr(s, "pl") > 0.4, noche: rr(s, "n") > 0.3, ledOn: rr(s, "lo") > 0.2 });
const infoH = (s: string): Info => { const p = pH(s); const rx = p.tvX > 0 ? -3.1 : 3.1;
  return { zona: { x: [-p.w / 2 + 1.4, p.w / 2 - 1.4], y: [1.15, 1.9], z: [-2.2, -4.5 + p.d - 1.0] }, targets: [[p.tvX, 1.1, -4.1], [p.tvX - 0.75, 0.66, -4.0], [p.vent, 1.7, -4.4], [rx, 1.1, -4.2], [p.lampX, 1.2, -1.2]] }; };
const HogarG: React.FC<{ s: string }> = ({ s }) => {
  const f = useCurrentFrame(); const p = pH(s); const led = p.ledOn && Math.floor(f / 14) % 2 === 0; const rx = p.tvX > 0 ? -3.1 : 3.1;
  const tv = useLienzo(256, 144, (ctx, W, H) => { const g = ctx.createLinearGradient(0, 0, W, H); g.addColorStop(0, "#07101c"); g.addColorStop(1, "#02040a"); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); });
  const vcol = p.noche ? "#1c3a6a" : "#ff9a52";
  return (
    <group>
      <Cuarto w={p.w} d={p.d} h={2.9} piso={p.P.piso} pared={p.P.pared} techo={p.P.techo} z0={-4.5 + p.d / 2} />
      <mesh position={[p.vent, 1.7, -4.47]}><planeGeometry args={[2.2, 1.4]} /><meshBasicMaterial color={vcol} toneMapped={false} /></mesh>
      <Caja p={[p.vent, 1.7, -4.46]} s={[2.4, 0.08, 0.06]} c="#e8e2d6" /><Caja p={[p.vent, 0.98, -4.46]} s={[2.4, 0.08, 0.1]} c="#e8e2d6" /><Caja p={[p.vent, 1.7, -4.45]} s={[0.05, 1.4, 0.05]} c="#e8e2d6" />
      <pointLight position={[p.vent, 1.7, -3.2]} color={p.noche ? "#7fa8ff" : "#ffb070"} intensity={9} distance={9} decay={2} />
      {[0, 1].map((i) => <Caja key={i} p={[-3 + i * 5.2 + rr(s, "q" + i), 1.9, -4.46]} s={[0.7, 0.5, 0.04]} c={pick(s, "fr" + i, ["#c8553a", "#3a6a9a", "#d8b04a", "#4a8a5a"])} />)}
      <Caja p={[p.tvX, 0.3, -4.1]} s={[2.1, 0.6, 0.5]} c="#3a2b20" r={0.6} /><Caja p={[p.tvX, 1.17, -4.1]} s={[1.6, 0.92, 0.07]} c="#0b0c0f" /><Plano p={[p.tvX, 1.17, -4.06]} w={1.5} h={0.84} tex={tv} />
      <Caja p={[p.tvX - 0.75, 0.63, -4.0]} s={[0.36, 0.06, 0.24]} c="#15171b" />
      <mesh position={[p.tvX - 0.6, 0.665, -3.89]}><sphereGeometry args={[0.012, 10, 10]} /><meshLambertMaterial color="#000" emissive={led ? p.led : "#241008"} emissiveIntensity={led ? 6 : 0.3} /></mesh>
      {led && <pointLight position={[p.tvX - 0.6, 0.7, -3.7]} color={p.led} intensity={1.8} distance={2.4} decay={2} />}
      <Caja p={[rx, 1.05, -4.2]} s={[1.2, 0.05, 0.4]} c="#3a2b20" /><Caja p={[rx, 1.12, -4.2]} s={[0.4, 0.06, 0.24]} c="#e8e8ea" />
      {[0, 1, 2].map((i) => <mesh key={i} position={[rx - 0.1 + i * 0.05, 1.155, -4.07]}><sphereGeometry args={[0.008, 8, 8]} /><meshLambertMaterial color="#000" emissive="#35ff8a" emissiveIntensity={4} /></mesh>)}
      <Caja p={[p.sofaX, 0.25, 1.4]} s={[2.6, 0.5, 1.0]} c={p.sofaC} /><Caja p={[p.sofaX, 0.7, 1.82]} s={[2.6, 0.55, 0.22]} c={p.sofaC} />
      <Caja p={[p.sofaX - 1.45, 0.45, 1.4]} s={[0.22, 0.7, 1.0]} c={p.sofaC} /><Caja p={[p.sofaX + 1.45, 0.45, 1.4]} s={[0.22, 0.7, 1.0]} c={p.sofaC} />
      <Caja p={[p.sofaX + 0.2, 0.2, -1.4]} s={[1.3, 0.04, 0.7]} c="#2d2118" /><Caja p={[p.sofaX, 0.01, -0.6]} s={[3.2, 0.02, 2.4]} c={p.alfC} />
      <group position={[p.lampX, 0, -1.2]}><mesh position={[0, 0.75, 0]}><cylinderGeometry args={[0.02, 0.02, 1.5, 8]} /><M c="#222" /></mesh>
        <mesh position={[0, 1.55, 0]}><cylinderGeometry args={[0.17, 0.26, 0.3, 18, 1, true]} /><meshLambertMaterial color="#f1d9a8" emissive={p.P.luz} emissiveIntensity={0.9} side={THREE.DoubleSide} /></mesh></group>
      <pointLight position={[p.lampX, 1.5, -1.2]} color={p.P.luz} intensity={8} distance={9} decay={2} />
      {p.planta && <Planta p={[-p.lampX * 0.95, 0, -3.2]} />}
      <ambientLight intensity={0.32} color={p.P.amb} />
    </group>);
};

/* ---------------- LABORATORIO ---------------- */
const pL = (s: string) => { const R = s.startsWith("R"); const cols = !R && rr(s, "c") > 0.5 ? 3 : 2; const n = R ? 4 : 3 + Math.floor(rr(s, "n") * 3); const zB = -1.2 - (n - 1) * 2.4 - 3.0;
  return { R, P: pal(s), cols, n, zB, xs: cols === 3 ? [-3.9, 0, 3.9] : [-2.4, 2.4], w: cols === 3 ? 14.5 : 12, pizarraC: pick(s, "pz", ["#f2f1ea", "#dfe8f2", "#e8f2df"]), cartel: rr(s, "ca") > 0.5 }; };
const infoL = (s: string): Info => { const p = pL(s); const ax = p.cols === 3 ? (rr(s, "ax") > 0.5 ? 1.95 : -1.95) : 0; const hw = p.cols === 3 ? 0.55 : 1.0;
  const tg: V3[] = [[0, 1.75, p.zB + 0.1]]; for (let i = 0; i < 4; i++) tg.push([pick(s, "tx" + i, p.xs), 0.98, -1.2 - Math.floor(rr(s, "tz" + i) * p.n) * 2.4 - 0.15]);
  return { zona: { x: [ax - hw, ax + hw], y: [1.2, 1.95], z: [p.zB + 3.2, 3.2] }, targets: tg }; };
const LabG: React.FC<{ s: string }> = ({ s }) => {
  const p = pL(s); const t1 = useLienzo(512, 384, dibVerde(s + "a")), t2 = useLienzo(512, 384, dibBlanca(s + "b")), t3 = useLienzo(512, 384, dibVerde(s + "c")); const pz = useLienzo(1024, 512, dibPizarra); const roj = useLienzo(512, 384, dibRoja);
  const zF = 4, d = zF - p.zB;
  return (
    <group>
      <Cuarto w={p.w} d={d} h={3.3} piso={p.P.piso} pared={p.P.pared} techo={p.P.techo} z0={(zF + p.zB) / 2} />
      <Plano p={[0, 1.75, p.zB + 0.05]} w={4.4} h={2.2} tex={pz} />
      {p.cartel && [-1, 1].map((l) => <Caja key={l} p={[l * (p.w / 2 - 0.05), 1.8, p.zB / 2]} s={[0.04, 1.0, 1.6]} c={pick(s, "po" + l, ["#c8553a", "#3a6a9a", "#d8b04a"])} />)}
      {p.xs.map((x, ci) => Array.from({ length: p.n }, (_, i) => { const z = -1.2 - i * 2.4; const tex = p.R && ci === 1 && i === 1 ? roj : [t1, t2, t3][(i + ci + Math.floor(rr(s, "m" + ci + i) * 3)) % 3];
        return (<group key={`${ci}_${i}`}><Escritorio p={[x, 0, z]} />{(rr(s, "k" + ci + i) > 0.15 || (p.R && ci === 1 && i === 1)) && <MonitorCRT p={[x, 0.745, z - 0.15]} tex={tex} rotY={(rr(s, "r" + ci + i) - 0.5) * 0.4} />}
          <Silla p={[x + 0.1, 0, z + 0.8]} rotY={Math.PI + (rr(s, "s" + ci + i) - 0.5) * 1.2} /></group>); }))}
      {Array.from({ length: Math.ceil(d / 4.5) }, (_, i) => <Panel key={i} p={[0, 3.25, 1 - i * 4.5]} s={[p.w * 0.6, 0.05, 0.5]} ei={2.6} c={p.P.luz} />)}
      {[1, -3.5, -8, -12].filter((z) => z > p.zB + 1).map((z, i) => <pointLight key={i} position={[0, 3.0, z]} color={p.P.luz} intensity={8} distance={8} decay={2} />)}
      <Planta p={[-p.w / 2 + 0.7, 0, p.zB + 1.2]} />
      <ambientLight intensity={0.55} color={p.P.amb} />
    </group>);
};

/* ---------------- SERVIDORES ---------------- */
const ESQ = [{ c: "#35ff8a", b: "#16331f" }, { c: "#4aa8ff", b: "#14263a" }, { c: "#ffb347", b: "#3a2810" }, { c: "#ff5a5a", b: "#3a1414" }, { c: "#c78bff", b: "#2a1a3a" }];
const pS = (s: string) => { const aw = pick(s, "aw", [1.5, 2.0, 2.6]); const nR = 8 + Math.floor(rr(s, "nr") * 5); return { aw, nR, esq: pick(s, "e", ESQ), P: pal(s), jaula: rr(s, "j") > 0.35, zj: -(5 + Math.floor(rr(s, "zj") * 4)), cart: pick(s, "ct", ["CLÚSTER DE PRUEBAS", "SALA 3 · NODOS", "ACCESO RESTRINGIDO", "RACK 12-24", "ZONA FRÍA"]), zBack: 2.4 - nR * 1.25 - 2.2 }; };
const infoS = (s: string): Info => { const p = pS(s); const tg: V3[] = [[0, 2.0, p.zBack + 0.1]]; for (let i = 0; i < 4; i++) tg.push([(rr(s, "l" + i) > 0.5 ? 1 : -1) * (p.aw + 0.5), 1.3, 2 - rr(s, "z" + i) * (p.nR * 1.2)]);
  return { zona: { x: [-p.aw + 0.6, p.aw - 0.6], y: [1.0, 2.0], z: [p.zBack + 4, 3.8] }, targets: tg }; };
const SrvG: React.FC<{ s: string }> = ({ s }) => {
  const p = pS(s);
  const leds = useLienzo(256, 512, (ctx, W, H, f) => { ctx.fillStyle = "#06080b"; ctx.fillRect(0, 0, W, H);
    for (let r = 0; r < 14; r++) { ctx.fillStyle = "#12161c"; ctx.fillRect(10, 10 + r * 34, W - 20, 28);
      for (let k = 0; k < 8; k++) { const q = random(`l${s}${r}_${k}_${Math.floor(f / (6 + r % 4))}`); ctx.fillStyle = q > 0.86 ? "#ffb347" : q > 0.35 ? p.esq.c : p.esq.b; ctx.fillRect(24 + k * 30, 18 + r * 34, 14, 10); } } });
  const cartel = useLienzo(512, 256, dibLetrero(p.cart, "ACCESO RESTRINGIDO"));
  const racks = Array.from({ length: p.nR }, (_, i) => 2.4 - i * 1.25); const L = 4.5 - p.zBack; const w = 2 * (p.aw + 1.8);
  const jaula = React.useMemo(() => { const q: number[] = []; for (let x = -w / 2; x <= w / 2 + 0.01; x += 0.5) q.push(x, 0, p.zj, x, 3, p.zj); for (let y = 0; y <= 3.01; y += 0.5) q.push(-w / 2, y, p.zj, w / 2, y, p.zj);
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(q, 3)); return g; }, [w, p.zj]);
  return (
    <group>
      <Cuarto w={w} d={L} h={3.2} piso={p.P.piso} pared={p.P.pared} techo="#202225" z0={(4.5 + p.zBack) / 2} />
      {racks.map((z, i) => [-1, 1].map((l) => <group key={`${i}_${l}`}><Caja p={[l * (p.aw + 0.95), 1.1, z]} s={[0.95, 2.2, 0.95]} c="#14161a" /><Plano p={[l * (p.aw + 0.95) - l * 0.485, 1.1, z]} w={0.85} h={2.0} tex={leds} rot={[0, l > 0 ? -Math.PI / 2 : Math.PI / 2, 0]} /></group>))}
      {p.jaula && <lineSegments geometry={jaula}><lineBasicMaterial color="#6a6d72" /></lineSegments>}
      <Plano p={[0, 2.1, p.zBack + 0.05]} w={3.4} h={1.7} tex={cartel} />
      {[2, -2, -6, -10].filter((z) => z > p.zBack + 1).map((z, i) => <Panel key={i} p={[0, 3.15, z]} s={[0.5, 0.05, 2.2]} ei={3.2} c={p.P.luz} />)}
      {[1.5, -4, -10.5].filter((z) => z > p.zBack + 1).map((z, i) => <pointLight key={i} position={[0, 2.8, z]} color={p.esq.c} intensity={5} distance={9} decay={2} />)}
      <ambientLight intensity={0.65} color={p.P.amb} />
    </group>);
};

/* ---------------- OFICINA / ARCHIVO ---------------- */
const pO = (s: string) => ({ P: pal(s), nc: 3 + Math.floor(rr(s, "nc") * 4), w: rango(s, "w", 9, 11.5), corcho: rr(s, "co") > 0.35, lampC: pick(s, "lc", ["#6bd68a", "#ffd27a", "#ff8a6b", "#8ac8ff"]), dobles: rr(s, "do") > 0.5 });
const infoO = (s: string): Info => { const p = pO(s); return { zona: { x: [-2.2, 2.2], y: [1.2, 2.0], z: [-4.6, 2.6] }, targets: [[0, 1.75, -7.9], [-p.w / 2 + 0.7, 1.3, -3], [p.w / 2 - 0.7, 1.3, -2], [0, 0.95, -3.5], [rango(s, "t", -1.5, 1.5), 1.0, -3.6]] }; };
const OfiG: React.FC<{ s: string }> = ({ s }) => {
  const p = pO(s); const cork = useLienzo(1024, 512, p.corcho ? dibCorcho : dibPizarra), caj = useLienzo(256, 512, dibCajones);
  const v1 = useLienzo(512, 384, dibVerde(s + "1")), v2 = useLienzo(512, 384, dibBlanca(s + "2")), v3 = useLienzo(512, 384, dibVerde(s + "3"));
  const cab = Array.from({ length: p.nc }, (_, i) => -6 + i * 1.8);
  return (
    <group>
      <Cuarto w={p.w} d={11} h={3.1} piso={p.P.piso} pared={p.P.pared} techo={p.P.techo} z0={-2.5} />
      <Plano p={[0, 1.75, -7.95]} w={4.6} h={2.3} tex={cork} />
      {cab.map((z, i) => [-1, 1].map((l) => <group key={`${i}_${l}`}><Caja p={[l * (p.w / 2 - 0.45), 0.9, z]} s={[0.7, 1.8, 1.2]} c="#7d8286" /><Plano p={[l * (p.w / 2 - 0.45) - l * 0.352, 0.9, z]} w={1.1} h={1.7} tex={caj} rot={[0, l > 0 ? -Math.PI / 2 : Math.PI / 2, 0]} /></group>))}
      <Escritorio p={[0, 0, -3.5]} ancho={3.2} /><MonitorCRT p={[-0.9, 0.745, -3.7]} tex={v1} /><MonitorCRT p={[0.2, 0.745, -3.7]} tex={v2} rotY={0.15} /><MonitorCRT p={[1.1, 0.745, -3.7]} tex={v3} rotY={-0.2} />
      {p.dobles && <><Escritorio p={[0, 0, 0.2]} ancho={3.2} /><MonitorCRT p={[0.5, 0.745, 0.05]} tex={v2} rotY={Math.PI} /></>}
      <group position={[-1.4, 0.745, -3.3]}><mesh position={[0, 0.2, 0]}><cylinderGeometry args={[0.012, 0.012, 0.3, 8]} /><M c="#222" /></mesh><mesh position={[0, 0.38, 0]}><cylinderGeometry args={[0.08, 0.14, 0.12, 14, 1, true]} /><meshLambertMaterial color={p.lampC} emissive={p.lampC} emissiveIntensity={0.7} side={THREE.DoubleSide} /></mesh></group>
      <pointLight position={[-1.4, 1.2, -3.2]} color={p.lampC} intensity={5} distance={5} decay={2} />
      {[1, -2.5, -6].map((z, i) => <Panel key={i} p={[0, 3.05, z]} s={[2.2, 0.05, 0.5]} ei={2.4} c={p.P.luz} />)}
      {[0.5, -4].map((z, i) => <pointLight key={i} position={[0, 2.8, z]} color={p.P.luz} intensity={9} distance={8} decay={2} />)}
      <Silla p={[-0.6, 0, -2.5]} rotY={Math.PI * 0.9} /><Silla p={[0.8, 0, -2.4]} rotY={Math.PI * 1.1} /><Planta p={[-p.w / 2 + 0.8, 0, -7.2]} />
      <ambientLight intensity={0.5} color={p.P.amb} />
    </group>);
};

/* ---------------- ALMACEN / FABRICA ---------------- */
const pF = (s: string) => ({ P: pal(s), cajas: pick(s, "cj", [["#b0875a", "#a37a50", "#c09468"], ["#d8d8d8", "#bcbcbc", "#e8e8e8"], ["#3a6a9a", "#2f5a85", "#4a7aab"], ["#6a8a5a", "#58784a", "#7a9a6a"]]),
  glow: pick(s, "gl", ["#ff7a2f", "#35ff8a", "#ff4a6a", "#4aa8ff"]), n: 2 + Math.floor(rr(s, "n") * 3), vel: rango(s, "v", 0.03, 0.05), poste: pick(s, "po", ["#c8681e", "#2a6ac8", "#c82a2a", "#2ac86a"]) });
const infoF = (s: string): Info => ({ zona: { x: [-2.3, 2.3], y: [1.0, 2.5], z: [-9, 3] }, targets: [[0, 0.9, -rango(s, "a", 2, 9)], [-4.6, 1.8, -rango(s, "b", 2, 8)], [4.6, 1.8, -rango(s, "c", 2, 8)], [0, 1.0, -12.5]] });
const FabG: React.FC<{ s: string }> = ({ s }) => {
  const f = useCurrentFrame(); const p = pF(s);
  const cajas = Array.from({ length: 9 }, (_, i) => ({ z: -12.4 + ((i * 1.65 + f * p.vel * 1.2) % 14.8), i, g: i === 3 }));
  const sz = [-10.5, -7.5, -4.5, -1.5].slice(0, p.n + 1);
  return (
    <group>
      <Cuarto w={13} d={19} h={5.2} piso="#5d5f62" pared={p.P.pared} techo="#2a2c2f" z0={-5} />
      <Caja p={[0, 0.5, -5]} s={[1.3, 0.12, 15.6]} c="#222428" /> {[-0.68, 0.68].map((x, i) => <Caja key={i} p={[x, 0.42, -5]} s={[0.07, 0.34, 15.6]} c="#c8a02e" />)}
      {cajas.map((c) => <group key={c.i}><Caja p={[0, 0.82, c.z]} s={[0.7, 0.4, 0.55]} c={c.g ? p.glow : p.cajas[c.i % 3]} e={c.g ? p.glow : undefined} ei={c.g ? 1.4 : 0} />{c.g && <pointLight position={[0, 1.4, c.z]} color={p.glow} intensity={6} distance={4} decay={2} />}</group>)}
      {[-1, 1].map((l) => sz.map((z, i) => <group key={`${l}_${i}`} position={[l * 5.1, 0, z]}>
        {[-1.2, 1.2].map((dz, k) => <Caja key={k} p={[0, 1.7, dz]} s={[0.1, 3.4, 0.1]} c={p.poste} />)}
        {[0.4, 1.4, 2.4].map((y, k) => <group key={k}><Caja p={[0, y, 0]} s={[1.0, 0.07, 2.6]} c="#3a5a8a" />{[-0.8, 0, 0.8].map((dz, j) => <Caja key={j} p={[0, y + 0.3, dz]} s={[0.8, 0.5, 0.6]} c={p.cajas[(i + k + j) % 3]} />)}</group>)}</group>))}
      {[-1, -5, -9, -13].map((z, i) => <Panel key={i} p={[0, 5.1, z]} s={[6, 0.06, 0.5]} ei={2.4} c={p.P.luz} />)}
      {[1, -5, -11].map((z, i) => <pointLight key={i} position={[0, 4.5, z]} color={p.P.luz} intensity={20} distance={13} decay={2} />)}
      <ambientLight intensity={0.5} color={p.P.amb} />
    </group>);
};

/* ---------------- MAPAMUNDI ---------------- */
const MP = [{ o: "#34567d", t: "#dccb9f", b: "#a99768" }, { o: "#2a3a4a", t: "#8fb08a", b: "#5f7f5a" }, { o: "#4a2a2a", t: "#d8b08a", b: "#a77f5a" }, { o: "#1f3f4a", t: "#cfd8dc", b: "#8fa0a8" }, { o: "#3a2a5a", t: "#d8c8e8", b: "#a898c8" }];
const pM = (s: string) => ({ P: pal(s), mp: pick(s, "mp", MP), pin: pick(s, "pin", ["#ff5a1f", "#ffd24a", "#ff3a5a", "#4aff9a", "#4ad0ff"]), w: rango(s, "w", 10, 12), desks: Math.floor(rr(s, "d") * 3), n: 40 + Math.floor(rr(s, "np") * 50) });
const infoM = (s: string): Info => ({ zona: { x: [-3.6, 3.6], y: [1.5, 2.3], z: [-0.8, 3.0] }, targets: [[rango(s, "x", -2.6, 2.6), rango(s, "y", 1.2, 2.5), -4.4], [rango(s, "x2", -2.6, 2.6), rango(s, "y2", 1.2, 2.5), -4.4]] });
const MapaG: React.FC<{ s: string }> = ({ s }) => {
  const p = pM(s);
  const m = useLienzo(1024, 512, (ctx, W, H, f) => { ctx.fillStyle = p.mp.o; ctx.fillRect(0, 0, W, H); ctx.fillStyle = p.mp.t; ctx.strokeStyle = p.mp.b; ctx.lineWidth = 1.5;
    for (const poly of mapa as number[][][]) { ctx.beginPath(); poly.forEach(([lo, la], i) => { const x = (lo + 180) / 360 * W, y = (90 - la) / 180 * H; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }); ctx.closePath(); ctx.fill(); ctx.stroke(); }
    const n = Math.min(p.n, Math.floor(f / 2));
    for (let i = 0; i < n; i++) { const x = (-125 + random(`${s}mo${i}`) * 290 + 180) / 360 * W, y = (90 - (-35 + random(`${s}ma${i}`) * 90)) / 180 * H, pu = 0.5 + 0.5 * Math.sin(f / 6 + i);
      ctx.fillStyle = p.pin; ctx.globalAlpha = 0.28 + 0.2 * pu; ctx.beginPath(); ctx.arc(x, y, 15 + 7 * pu, 0, 7); ctx.fill(); ctx.globalAlpha = 1; ctx.beginPath(); ctx.arc(x, y, 6, 0, 7); ctx.fill(); } });
  const b = useLienzo(512, 384, dibBarras), v = useLienzo(512, 384, dibVerde(s + "m"));
  return (
    <group>
      <Cuarto w={p.w} d={9} h={3.4} piso={p.P.piso} pared={p.P.pared} techo={p.P.techo} z0={-0.5} />
      <Caja p={[0, 1.8, -4.46]} s={[6.5, 3.3, 0.06]} c="#3a2a1d" /><Plano p={[0, 1.8, -4.42]} w={6.3} h={3.1} tex={m} />
      {p.desks > 0 && <><Escritorio p={[3.7, 0, -2.2]} ancho={1.8} /><MonitorCRT p={[3.7, 0.745, -2.35]} tex={b} s={1.15} /></>}
      {p.desks > 1 && <><Escritorio p={[-3.9, 0, -2.0]} ancho={1.8} /><MonitorCRT p={[-3.9, 0.745, -2.15]} tex={v} /></>}
      {[-2.2, 2.2].map((x, i) => <Panel key={i} p={[x, 3.35, -2.2]} s={[1.6, 0.05, 0.6]} ei={3} c={p.P.luz} />)}
      <spotLight position={[0, 3.2, -1.5]} angle={0.7} penumbra={1} intensity={60} distance={9} color={p.P.luz} target-position={[0, 1.8, -4.4]} />
      <pointLight position={[0, 2.8, 0]} color={p.P.luz} intensity={7} distance={9} decay={2} />
      <Planta p={[-p.w / 2 + 0.8, 0, 2.5]} /><ambientLight intensity={0.55} color={p.P.amb} />
    </group>);
};

/* ---------------- CALLE DE NOCHE (casas con ventanas) ---------------- */
const pC = (s: string) => ({ n: 8 + Math.floor(rr(s, "n") * 4), cielo: pick(s, "ci", ["#070b18", "#10081a", "#08141a", "#1a0e0a"]), farol: pick(s, "fa", ["#ffd27a", "#cfe0ff", "#ffb070"]), lit: rango(s, "lit", 0.35, 0.75), tv: rr(s, "tv") > 0.5 });
const infoC = (s: string): Info => ({ zona: { x: [-1.6, 1.6], y: [1.4, 3.0], z: [-12, 7] }, targets: [[-5.6, 2.2, -rango(s, "a", 2, 12)], [5.6, 2.2, -rango(s, "b", 2, 12)], [0, 2.0, -26]] });
const CalleG: React.FC<{ s: string }> = ({ s }) => {
  const p = pC(s);
  const casas = Array.from({ length: p.n * 2 }, (_, i) => { const l = i % 2 ? 1 : -1; const k = Math.floor(i / 2); return { l, z: 6 - k * 4.6 - rr(s, "z" + i) * 0.8, h: 3 + rr(s, "h" + i) * 2, w: 3.4 + rr(s, "w" + i) * 1.2, c: pick(s, "c" + i, ["#9a8a7a", "#7a8a9a", "#a86a6a", "#8a9a7a", "#b0b0a0", "#8a7a9a"]), i }; });
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[60, 70]} /><meshLambertMaterial color="#25272b" /></mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, -10]}><planeGeometry args={[0.2, 60]} /><meshLambertMaterial color="#d8c060" emissive="#d8c060" emissiveIntensity={0.15} /></mesh>
      {[-1, 1].map((l) => <Caja key={l} p={[l * 3.3, 0.08, -10]} s={[1.6, 0.16, 60]} c="#4a4b4e" />)}
      {casas.map((c) => <group key={c.i} position={[c.l * (6.4 + c.w / 2), 0, c.z]}>
        <Caja p={[0, c.h / 2, 0]} s={[c.w, c.h, 3.6]} c={c.c} /><Caja p={[0, c.h + 0.35, 0]} s={[c.w + 0.3, 0.7, 3.9]} c="#2f2a28" />
        {[0, 1].map((a) => [0, 1].map((b) => { const on = rr(s, `w${c.i}${a}${b}`) < p.lit; const col = on ? (p.tv && rr(s, `t${c.i}${a}${b}`) > 0.6 ? "#7fa8ff" : "#ffcf70") : "#0b0e14";
          return <mesh key={`${a}${b}`} position={[-c.l * (c.w / 2 + 0.01), 1.2 + b * 1.4, (a - 0.5) * 1.8]} rotation={[0, c.l * Math.PI / 2, 0]}><planeGeometry args={[0.9, 0.9]} /><meshBasicMaterial color={col} toneMapped={false} /></mesh>; }))}
      </group>)}
      {[4, -3, -10].map((z, i) => <group key={i} position={[i % 2 ? 3.4 : -3.4, 0, z]}><mesh position={[0, 2.2, 0]}><cylinderGeometry args={[0.05, 0.06, 4.4, 8]} /><M c="#2a2c30" /></mesh>
        <mesh position={[0, 4.4, 0]}><sphereGeometry args={[0.28, 12, 12]} /><meshLambertMaterial color="#fff" emissive={p.farol} emissiveIntensity={2.5} /></mesh><pointLight position={[0, 4.2, 0]} color={p.farol} intensity={45} distance={13} decay={2} /></group>)}
      <mesh position={[18, 18, -45]}><sphereGeometry args={[2, 16, 16]} /><meshBasicMaterial color="#e8eefc" toneMapped={false} /></mesh>
      <color attach="background" args={[p.cielo]} /><fog attach="fog" args={[p.cielo, 12, 48]} />
      <ambientLight intensity={1.2} color="#8fa0d8" />
    </group>);
};

/* ---------------- TIENDA (pasillo de estanterias) ---------------- */
const pT = (s: string) => ({ P: pal(s), fam: pick(s, "f", [["#d8423a", "#f0c040", "#3a8ad8"], ["#4aa86a", "#e8e8e8", "#d87a2a"], ["#8a4ad8", "#40c0d8", "#e8d84a"], ["#d84a8a", "#4a6ad8", "#e8e8e8"]]), n: 8 + Math.floor(rr(s, "n") * 5), aw: pick(s, "aw", [1.4, 1.9]) });
const infoT = (s: string): Info => { const p = pT(s); return { zona: { x: [-p.aw + 0.5, p.aw - 0.5], y: [1.1, 1.9], z: [-p.n * 1.1 + 2, 4.2] }, targets: [[(rr(s, "a") > 0.5 ? 1 : -1) * (p.aw + 0.6), 1.2, -rango(s, "b", 0, p.n)], [0, 1.4, -p.n * 1.2 - 1]] }; };
const TiendaG: React.FC<{ s: string }> = ({ s }) => {
  const p = pT(s); const L = p.n * 1.2 + 8;
  const suelo = useLienzo(128, 128, (ctx, W, H) => { ctx.fillStyle = "#c8c4b8"; ctx.fillRect(0, 0, W, H); ctx.fillStyle = "#8a8678"; ctx.fillRect(0, 0, W / 2, H / 2); ctx.fillRect(W / 2, H / 2, W / 2, H / 2); });
  suelo.wrapS = suelo.wrapT = THREE.RepeatWrapping; suelo.repeat.set(p.aw * 3, L / 1.2);
  return (
    <group>
      <Cuarto w={2 * (p.aw + 1.6)} d={L} h={3.2} piso="#999" pared={p.P.pared} techo="#d8d8d4" z0={4.5 - L / 2} />
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.004, 4.5 - L / 2]}><planeGeometry args={[2 * p.aw, L]} /><meshBasicMaterial map={suelo} toneMapped={false} /></mesh>
      {[-1, 1].map((l) => Array.from({ length: p.n }, (_, i) => <group key={`${l}_${i}`} position={[l * (p.aw + 0.5), 0, 3 - i * 1.2]}>
        <Caja p={[0, 1.0, 0]} s={[0.7, 2.0, 1.1]} c="#e8e6e0" />
        {[0.3, 0.8, 1.3, 1.8].map((y, k) => [-0.3, 0, 0.3].map((dz, j) => <Caja key={`${k}_${j}`} p={[-l * 0.25, y, dz * 1.4]} s={[0.12, 0.34, 0.3]} c={p.fam[(i + k + j) % 3]} />))}</group>))}
      {Array.from({ length: Math.ceil(L / 4) }, (_, i) => <Panel key={i} p={[0, 3.15, 3 - i * 4]} s={[1.0, 0.05, 2.4]} ei={3} c="#f4f8ff" />)}
      {[2, -4].map((z, i) => <pointLight key={i} position={[0, 2.8, z]} color="#f4f8ff" intensity={10} distance={9} decay={2} />)}
      <ambientLight intensity={0.7} color="#d8dce8" />
    </group>);
};

/* ---------------- selector y camara generativa ---------------- */
const INFO: Record<string, (s: string) => Info> = { hogar: infoH, lab: infoL, srv: infoS, ofi: infoO, fab: infoF, mapa: infoM, calle: infoC, tienda: infoT };
export const TIPOS_GEN = Object.keys(INFO);
export const SalaGen: React.FC<{ id: string }> = ({ id }) => {
  const [, tipo, s] = id.split(":");
  if (tipo === "hogar") return <HogarG s={s} />; if (tipo === "lab") return <LabG s={s} />; if (tipo === "srv") return <SrvG s={s} />; if (tipo === "ofi") return <OfiG s={s} />;
  if (tipo === "fab") return <FabG s={s} />; if (tipo === "mapa") return <MapaG s={s} />; if (tipo === "calle") return <CalleG s={s} />; return <TiendaG s={s} />;
};
export const camGen = (id: string): Cam => {
  const [, tipo, s] = id.split(":");
  if (tipo === "lab" && s.startsWith("R")) return { desde: [0.2, 1.4, -0.2], hasta: [2.4, 1.03, -3.7], mira: [2.4, 1.03, -4.0] };      // entra en el monitor rojo
  const info = INFO[tipo](s); const { x, y, z } = info.zona;
  const tg = info.targets[Math.floor(rr(s, "t") * info.targets.length) % info.targets.length]; const k = Math.floor(rr(s, "c") * 5);
  const P = (fx: number, fy: number, fz: number): V3 => [x[0] + (x[1] - x[0]) * fx, y[0] + (y[1] - y[0]) * fy, z[0] + (z[1] - z[0]) * fz];
  const a = rr(s, "a"), b = rr(s, "b"), tg2: V3 = [tg[0] + (rr(s, "j1") - 0.5) * 1.2, tg[1] + (rr(s, "j2") - 0.5) * 0.5, tg[2]];
  if (k === 0) return { desde: P(a, 0.4, 1.0), hasta: P(b, 0.5, 0.3), mira: tg, miraHasta: tg2 };                // avance
  if (k === 1) return { desde: P(a, 0.5, 0.3), hasta: P(b, 0.4, 1.0), mira: tg2, miraHasta: tg };                // retroceso
  if (k === 2) return { desde: P(0, 0.5, 0.35 + 0.4 * a), hasta: P(1, 0.5, 0.35 + 0.4 * b), mira: tg, miraHasta: tg2 };   // travelling lateral
  if (k === 3) return { desde: P(1, 0.3, 0.8), hasta: P(0, 0.7, 0.55), mira: tg2, miraHasta: tg };               // arco
  return { desde: P(0.5, 0.0, 0.9), hasta: P(0.5, 1.0, 0.45), mira: tg, miraHasta: tg2 };                       // grua
};
