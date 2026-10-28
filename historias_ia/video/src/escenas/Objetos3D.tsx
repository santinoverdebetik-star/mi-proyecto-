import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import * as THREE from "three";
import { C } from "../estilo";

const mezcla = (a: string, b: string, t: number) => new THREE.Color(a).lerp(new THREE.Color(b), Math.min(1, Math.max(0, t)));

/** Laptop 3D: base metalica, teclado, pantalla que se enciende en el color indicado (azul = normal, naranja = infectada). */
export const Laptop: React.FC<{ pos: [number, number, number]; rotY?: number; infeccion: number; escala?: number }> = ({ pos, rotY = 0, infeccion, escala = 1 }) => {
  const f = useCurrentFrame();
  const parpadeo = infeccion > 0.05 && infeccion < 1 ? 0.7 + 0.3 * Math.sin(f * 1.9) : 1;
  const col = mezcla("#1c3b66", C.naranja, infeccion);
  const intens = (0.5 + 0.85 * infeccion) * parpadeo;
  return (
    <group position={pos} rotation={[0, rotY, 0]} scale={escala}>
      <mesh position={[0, 0.045, 0]}><boxGeometry args={[2.4, 0.09, 1.6]} /><meshStandardMaterial color="#2a2d34" roughness={0.35} metalness={0.7} /></mesh>
      <mesh position={[0, 0.095, 0.1]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[2.1, 1.0]} /><meshStandardMaterial color="#0f1115" roughness={0.6} emissive={col} emissiveIntensity={0.08 + 0.25 * infeccion} /></mesh>
      <mesh position={[0, 0.098, 0.62]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[0.7, 0.32]} /><meshStandardMaterial color="#1a1c21" roughness={0.5} /></mesh>
      <group position={[0, 0.09, -0.78]} rotation={[-0.32, 0, 0]}>
        <mesh position={[0, 0.76, 0]}><boxGeometry args={[2.4, 1.52, 0.06]} /><meshStandardMaterial color="#202329" roughness={0.3} metalness={0.8} /></mesh>
        <mesh position={[0, 0.76, 0.034]}><planeGeometry args={[2.22, 1.34]} /><meshStandardMaterial color="#02060a" emissive={col} emissiveIntensity={intens} /></mesh>
      </group>
      <pointLight position={[0, 1.0, 1.2]} color={col} intensity={(1.2 + 7 * infeccion) * parpadeo} distance={7} decay={2} />
    </group>
  );
};

/** Tren de pulsos luminosos que viaja de A a B siguiendo un arco (la "señal" / el intento de intrusion). */
export const Pulsos: React.FC<{ a: [number, number, number]; b: [number, number, number]; arco?: number; desde: number; hasta?: number; n?: number; color?: string }> = ({ a, b, arco = 1.1, desde, hasta = 9999, n = 7, color = C.naranja }) => {
  const f = useCurrentFrame();
  if (f < desde || f > hasta) return null;
  const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b);
  const M = A.clone().add(B).multiplyScalar(0.5).add(new THREE.Vector3(0, arco, 0));
  return (
    <group>
      {Array.from({ length: n }, (_, i) => {
        const t = (((f - desde) / 70 + i / n) % 1);
        const u = 1 - t;
        const p = A.clone().multiplyScalar(u * u).add(M.clone().multiplyScalar(2 * u * t)).add(B.clone().multiplyScalar(t * t));
        const s = 0.05 + 0.05 * Math.sin(Math.PI * t);
        return <mesh key={i} position={p}><sphereGeometry args={[s, 12, 12]} /><meshStandardMaterial color="#000" emissive={color} emissiveIntensity={2.4} /></mesh>;
      })}
      <pointLight position={A.clone().lerp(B, ((f - desde) / 70) % 1).add(new THREE.Vector3(0, arco * 0.8, 0))} color={color} intensity={2.5} distance={4} />
    </group>
  );
};

/** Caja de streaming con LED parpadeante. */
export const CajaStreaming: React.FC<{ pos: [number, number, number]; led?: string; fase?: number; activa?: number; escala?: number }> = ({ pos, led = C.naranja, fase = 0, activa = 1, escala = 1 }) => {
  const f = useCurrentFrame();
  const on = Math.floor((f + fase) / 12) % 2 === 0 ? 1 : 0.2;
  return (
    <group position={pos} scale={escala}>
      <mesh><boxGeometry args={[1.3, 0.2, 0.95]} /><meshStandardMaterial color="#3b3f49" roughness={0.45} metalness={0.4} emissive="#2b3345" emissiveIntensity={1.0} /></mesh>
      <mesh position={[0.45, 0.02, 0.485]}><sphereGeometry args={[0.055, 12, 12]} /><meshStandardMaterial color="#000" emissive={led} emissiveIntensity={3.5 * on * activa + 0.3} /></mesh>
    </group>
  );
};

/** Manometro analogico 3D: aguja que sube hacia la zona roja ("peligrosamente cerca"). */
export const Manometro: React.FC<{ total: number }> = ({ total }) => {
  const f = useCurrentFrame();
  const u = interpolate(f, [10, total - 8], [0.34, 0.735], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) + Math.sin(f / 5) * 0.004 * (f / total);
  const ang = (-135 + 270 * u) * Math.PI / 180;
  const marcas = Array.from({ length: 41 }, (_, i) => {
    const uu = i / 40, th = (-135 + 270 * uu) * Math.PI / 180, mayor = i % 5 === 0, rojo = uu >= 0.72;
    return { th, mayor, rojo };
  });
  return (
    <group>
      <mesh rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[1.62, 1.62, 0.12, 64]} /><meshStandardMaterial color="#8a867e" roughness={0.6} /></mesh>
      <mesh position={[0, 0, 0.065]}><circleGeometry args={[1.56, 64]} /><meshStandardMaterial color="#bdb7aa" roughness={0.7} emissive="#1c1913" emissiveIntensity={0.25} /></mesh>
      <mesh position={[0, 0, 0.1]}><torusGeometry args={[1.64, 0.09, 16, 96]} /><meshStandardMaterial color="#a9aeb6" roughness={0.25} metalness={0.9} /></mesh>
      {marcas.map((m, i) => (
        <mesh key={i} position={[Math.sin(m.th) * 1.33, Math.cos(m.th) * 1.33, 0.075]} rotation={[0, 0, -m.th]}>
          <boxGeometry args={[m.mayor ? 0.05 : 0.025, m.mayor ? 0.3 : 0.17, 0.01]} />
          <meshStandardMaterial color={m.rojo ? "#d01a14" : "#171717"} emissive={m.rojo ? "#d01a14" : "#000"} emissiveIntensity={m.rojo ? 0.9 : 0} />
        </mesh>
      ))}
      <mesh position={[0, 0, 0.08]}><ringGeometry args={[1.0, 1.07, 48, 1, -Math.PI / 4, (75.6 * Math.PI) / 180]} /><meshBasicMaterial color="#d01a14" /></mesh>
      <group position={[0, 0, 0.13]} rotation={[0, 0, -ang]}>
        <mesh position={[0, 0.5, 0]}><boxGeometry args={[0.045, 1.35, 0.02]} /><meshStandardMaterial color="#0a0a0a" emissive="#300" emissiveIntensity={0.3} /></mesh>
        <mesh position={[0, -0.2, 0]}><boxGeometry args={[0.07, 0.4, 0.02]} /><meshStandardMaterial color="#0a0a0a" /></mesh>
      </group>
      <mesh position={[0, 0, 0.14]}><sphereGeometry args={[0.1, 24, 24]} /><meshStandardMaterial color="#111" metalness={0.8} roughness={0.3} /></mesh>
      <pointLight position={[2.2, 1.8, 3]} color="#ffd9b0" intensity={6} distance={9} />
      <pointLight position={[-2.2, -0.4, 2]} color={C.rojo} intensity={5} distance={8} />
    </group>
  );
};

/* ---------- escenas de "lo que dice la narracion" (parte 2): casas, fabrica, candado, apagon, duplicacion, rack, radar ---------- */
const rnd = (s: string) => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return ((h >>> 0) % 10000) / 10000; };

/** Barrio visto desde arriba: cada casa con su ventana; las ventanas pasan de cian a naranja en oleadas (el contagio). */
export const CasasRed: React.FC = () => {
  const f = useCurrentFrame();
  const filas = 6, cols = 10;
  const semillas = [[2, 1], [7, 4], [5, 0], [9, 2]];
  const casas = Array.from({ length: filas * cols }, (_, i) => {
    const r = Math.floor(i / cols), c = i % cols;
    const d = Math.min(...semillas.map(([sc, sr]) => Math.hypot(c - sc, r - sr)));
    return { x: (c - cols / 2) * 1.5 + (rnd("x" + i) - 0.5) * 0.3, z: (r - filas / 2) * 1.5 + (rnd("z" + i) - 0.5) * 0.3, d, w: 0.7 + rnd("w" + i) * 0.2, h: 0.5 + rnd("h" + i) * 0.35, i };
  });
  return (
    <group position={[0, -0.9, -2]}>
      {casas.map((k) => {
        const inf = interpolate(f, [14 + k.d * 9, 34 + k.d * 9], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const col = mezcla("#2fd3ff", C.naranja, inf);
        return (
          <group key={k.i} position={[k.x, 0, k.z]}>
            <mesh position={[0, k.h / 2, 0]}><boxGeometry args={[k.w, k.h, k.w]} /><meshStandardMaterial color="#4a505d" roughness={0.7} emissive="#1a1f2a" emissiveIntensity={0.6} /></mesh>
            <mesh position={[0, k.h + 0.22, 0]} rotation={[0, Math.PI / 4, 0]}><coneGeometry args={[k.w * 0.78, 0.45, 4]} /><meshStandardMaterial color="#2c313b" roughness={0.8} emissive="#10131a" emissiveIntensity={0.6} /></mesh>
            <mesh position={[0, k.h * 0.5, k.w / 2 + 0.01]}><planeGeometry args={[k.w * 0.45, k.h * 0.42]} /><meshStandardMaterial color="#000" emissive={col} emissiveIntensity={1.0 + 2.2 * inf} /></mesh>
          </group>
        );
      })}
      <pointLight position={[0, 4, 0]} color={C.naranja} intensity={interpolate(f, [10, 120], [2, 14], { extrapolateRight: "clamp" })} distance={14} />
    </group>
  );
};

/** Cinta transportadora con cajas; una de ellas brilla en naranja (ya sale infectada de fabrica). */
export const Fabrica: React.FC = () => {
  const f = useCurrentFrame();
  const cajas = Array.from({ length: 6 }, (_, i) => ({ i, x: -6 + i * 2.4 + (f * 0.03) % 2.4 }));
  const marcada = 3;
  return (
    <group>
      <mesh position={[0, -0.97, 0]}><boxGeometry args={[18, 0.14, 2.2]} /><meshStandardMaterial color="#181a1f" roughness={0.5} metalness={0.6} /></mesh>
      {Array.from({ length: 26 }, (_, k) => <mesh key={k} position={[-8.6 + ((k * 0.7 + f * 0.03) % 17.8), -0.895, 0]}><boxGeometry args={[0.06, 0.02, 2.1]} /><meshStandardMaterial color="#2c3038" /></mesh>)}
      {cajas.map((c) => {
        const mala = (c.i + Math.floor(f * 0.03 / 2.4)) % 6 === marcada;
        return (
          <group key={c.i}>
            <CajaStreaming pos={[c.x, -0.78, 0]} led={mala ? C.naranja : C.cian} activa={mala ? 1 : 0.5} />
            {mala && <pointLight position={[c.x, -0.3, 0.7]} color={C.naranja} intensity={6} distance={5} />}
          </group>
        );
      })}
    </group>
  );
};

/** Candado 3D: el arco se abre solo; por la cerradura se escapa una luz naranja. */
export const Candado: React.FC<{ agujero?: boolean }> = ({ agujero = false }) => {
  const f = useCurrentFrame();
  const abre = interpolate(f, [28, 64], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <group position={[0, 0.1, 0]} rotation={[0, Math.sin(f / 60) * 0.18, 0]}>
      <mesh><boxGeometry args={[1.7, 1.3, 0.6]} /><meshStandardMaterial color="#6b7079" roughness={0.4} metalness={0.8} emissive="#15171b" emissiveIntensity={0.6} /></mesh>
      <group position={[0.55 - 0.55 * 0, 0.65, 0]} rotation={[0, 0, -abre * 0.45]}>
        <mesh position={[-0.55 * (1 - 0), abre * 0.28, 0]} rotation={[0, 0, 0]}><torusGeometry args={[0.55, 0.12, 16, 40, Math.PI]} /><meshStandardMaterial color="#c3c7ce" roughness={0.25} metalness={0.95} /></mesh>
      </group>
      <mesh position={[0, 0.05, 0.31]}><circleGeometry args={[0.16, 24]} /><meshStandardMaterial color="#000" emissive={agujero ? C.naranja : "#111"} emissiveIntensity={agujero ? 3.2 : 0} /></mesh>
      <mesh position={[0, -0.22, 0.31]}><planeGeometry args={[0.1, 0.34]} /><meshStandardMaterial color="#000" emissive={agujero ? C.naranja : "#111"} emissiveIntensity={agujero ? 3.2 : 0} /></mesh>
      {agujero && <pointLight position={[0, 0, 1.4]} color={C.naranja} intensity={9} distance={7} />}
    </group>
  );
};

/** Muro de pantallas: giran el circulo de carga ... y se van apagando una a una (la web que "se cae"). */
export const Apagon: React.FC = () => {
  const f = useCurrentFrame();
  const orden = [3, 9, 1, 12, 6, 0, 14, 8, 4, 11, 2, 13, 7, 5, 10];
  return (
    <group position={[0, 0.6, -1]}>
      {Array.from({ length: 15 }, (_, i) => {
        const c = i % 5, r = Math.floor(i / 5);
        const t = 40 + orden.indexOf(i) * 7;
        const viva = f < t ? 1 : Math.max(0, 1 - (f - t) / 6);
        return (
          <group key={i} position={[(c - 2) * 2.3, (1 - r) * 1.5, 0]}>
            <mesh position={[0, 0, -0.03]}><boxGeometry args={[2.1, 1.25, 0.05]} /><meshStandardMaterial color="#0b0c0f" roughness={0.3} metalness={0.7} /></mesh>
            <mesh><planeGeometry args={[1.95, 1.1]} /><meshStandardMaterial color="#02050a" emissive="#12345f" emissiveIntensity={1.2 * viva} /></mesh>
            {viva > 0.05 && <mesh position={[0, 0, 0.01]} rotation={[0, 0, -f * 0.18 - i]}><ringGeometry args={[0.2, 0.26, 24, 1, 0, Math.PI * 1.5]} /><meshBasicMaterial color="#9fd1ff" transparent opacity={viva} /></mesh>}
          </group>
        );
      })}
      <pointLight position={[0, 1, 5]} color="#4f8fd8" intensity={interpolate(f, [30, 150], [9, 0.5], { extrapolateRight: "clamp" })} distance={14} />
      <pointLight position={[0, -1.5, 3]} color={C.rojo} intensity={interpolate(f, [60, 150], [0, 6], { extrapolateRight: "clamp" })} distance={9} />
    </group>
  );
};

/** Arbol de duplicacion: 1 → 2 → 4 → 8 → 16 → 32 nodos (cada generacion aparece cada ~1 s). */
export const Duplicacion: React.FC = () => {
  const f = useCurrentFrame();
  const gens = 6, paso = 28;
  const pos = (g: number, i: number): [number, number, number] => {
    const n = 2 ** g, ang = (i / n) * Math.PI * 2 + g * 0.3, r = g === 0 ? 0 : 0.55 + g * 0.62;
    return [Math.cos(ang) * r, 0.8 + Math.sin(ang * 1.5 + g) * 0.2, Math.sin(ang) * r - 1];
  };
  const out: React.ReactNode[] = [];
  for (let g = 0; g < gens; g++) {
    const vis = interpolate(f, [g * paso, g * paso + 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    if (vis <= 0) continue;
    for (let i = 0; i < 2 ** g; i++) {
      const p = pos(g, i);
      out.push(<mesh key={`n${g}_${i}`} position={p} scale={vis}><sphereGeometry args={[0.2 - g * 0.02, 14, 14]} /><meshStandardMaterial color="#000" emissive={C.naranja} emissiveIntensity={1.8} /></mesh>);
      if (g > 0) {
        const q = pos(g - 1, i >> 1), A = new THREE.Vector3(...p), B = new THREE.Vector3(...q);
        const quat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
        out.push(<mesh key={`l${g}_${i}`} position={A.clone().add(B).multiplyScalar(0.5)} quaternion={quat} scale={[1, vis, 1]}><cylinderGeometry args={[0.008, 0.008, A.distanceTo(B), 4]} /><meshStandardMaterial color="#000" emissive={C.naranja} emissiveIntensity={1.2} /></mesh>);
      }
    }
  }
  return <group>{out}<pointLight position={[0, 1.5, 0]} color={C.naranja} intensity={8} distance={9} /></group>;
};

/** Racks de servidores con luces: se apagan cuando "llamas al dueño". */
export const Rack: React.FC = () => {
  const f = useCurrentFrame();
  const apaga = interpolate(f, [80, 96], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <group position={[0, 0.5, -1]}>
      {[-2.2, 0, 2.2].map((x, k) => (
        <group key={k} position={[x, 0, 0]}>
          <mesh><boxGeometry args={[1.5, 3.2, 1.1]} /><meshStandardMaterial color="#14161b" roughness={0.4} metalness={0.7} /></mesh>
          {Array.from({ length: 14 }, (_, r) => {
            const on = (Math.floor((f + r * 5 + k * 9) / 7) % 3) !== 0;
            const v = (k === 1 ? apaga : 1);
            return <mesh key={r} position={[0, 1.4 - r * 0.2, 0.56]}><planeGeometry args={[1.3, 0.12]} /><meshStandardMaterial color="#05070a" emissive={on ? C.cian : "#143040"} emissiveIntensity={(on ? 1.5 : 0.3) * v} /></mesh>;
          })}
        </group>
      ))}
      <pointLight position={[0, 1, 3]} color={C.cian} intensity={5} distance={10} />
    </group>
  );
};

/** Radar: barrido giratorio; los puntos naranjas ("ruido sospechoso") se iluminan cuando el haz pasa. */
export const Radar: React.FC = () => {
  const f = useCurrentFrame();
  const ang = f * 0.055;
  const puntos = Array.from({ length: 9 }, (_, i) => ({ a: rnd("a" + i) * Math.PI * 2, r: 0.4 + rnd("r" + i) * 1.1 }));
  return (
    <group rotation={[-0.95, 0, 0]} position={[0, 0.2, 0]}>
      <mesh><circleGeometry args={[1.8, 64]} /><meshStandardMaterial color="#04100f" emissive="#06201e" emissiveIntensity={0.8} /></mesh>
      {[0.6, 1.2, 1.8].map((r, i) => <mesh key={i} position={[0, 0, 0.005]}><ringGeometry args={[r - 0.012, r, 64]} /><meshBasicMaterial color="#1f8f86" /></mesh>)}
      <mesh position={[0, 0, 0.006]} rotation={[0, 0, -ang]}><circleGeometry args={[1.8, 32, 0, 0.6]} /><meshBasicMaterial color="#39e6d0" transparent opacity={0.28} /></mesh>
      {puntos.map((p, i) => {
        const d = ((ang - 0 + Math.PI * 2 * 100) - (Math.PI * 2 - p.a)) % (Math.PI * 2);
        const luz = Math.max(0, 1 - d / 2.6);
        return <mesh key={i} position={[Math.cos(p.a) * p.r, Math.sin(p.a) * p.r, 0.03]}><sphereGeometry args={[0.07, 12, 12]} /><meshStandardMaterial color="#000" emissive={C.naranja} emissiveIntensity={0.3 + 3 * luz} /></mesh>;
      })}
      <pointLight position={[0, 0, 2.5]} color="#39e6d0" intensity={4} distance={8} />
    </group>
  );
};

/* ---------- objetos 3D nuevos (más variedad): globo, sala, estantería, avalancha, cable, código ---------- */

/** Globo terraqueo: puntos de luz repartidos por todo el planeta que pasan de cian a naranja ("repartidos por todo el mundo"). */
export const Globo: React.FC = () => {
  const f = useCurrentFrame();
  const pts = Array.from({ length: 90 }, (_, i) => {
    const lat = Math.asin(2 * rnd("la" + i) - 1), lon = rnd("lo" + i) * Math.PI * 2, r = 1.56;
    return { p: [r * Math.cos(lat) * Math.cos(lon), r * Math.sin(lat), r * Math.cos(lat) * Math.sin(lon)] as [number, number, number], t: 10 + rnd("t" + i) * 110 };
  });
  return (
    <group position={[0, 0.7, 0]} rotation={[0.25, f * 0.007, 0]}>
      <mesh><sphereGeometry args={[1.5, 48, 48]} /><meshStandardMaterial color="#0e1a2b" roughness={0.6} emissive="#0a1626" emissiveIntensity={0.7} /></mesh>
      <mesh><sphereGeometry args={[1.53, 24, 16]} /><meshBasicMaterial color="#2a6f9a" wireframe transparent opacity={0.35} /></mesh>
      {pts.map((q, i) => {
        const inf = interpolate(f, [q.t, q.t + 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return <mesh key={i} position={q.p}><sphereGeometry args={[0.035 + 0.03 * inf, 10, 10]} /><meshStandardMaterial color="#000" emissive={mezcla("#2fd3ff", C.naranja, inf)} emissiveIntensity={1.4 + 2 * inf} /></mesh>;
      })}
      <pointLight position={[3, 2, 3]} color="#ffd9b0" intensity={8} distance={10} />
    </group>
  );
};

/** Sala de estar: sofá, lámpara, televisor encendido en azul y la cajita con su luz. */
export const Sala: React.FC = () => {
  const f = useCurrentFrame();
  const led = (Math.floor(f / 14) % 2) === 0 ? 1 : 0.2;
  return (
    <group>
      <mesh position={[0, 1.2, -2.6]}><planeGeometry args={[14, 5]} /><meshStandardMaterial color="#1a1f29" roughness={0.9} /></mesh>
      <mesh position={[0, 0.6, -2.5]}><boxGeometry args={[3.6, 2.0, 0.08]} /><meshStandardMaterial color="#0b0c0f" roughness={0.3} metalness={0.7} /></mesh>
      <mesh position={[0, 0.6, -2.45]}><planeGeometry args={[3.4, 1.85]} /><meshStandardMaterial color="#04070b" emissive="#1c4a80" emissiveIntensity={1.1 + 0.25 * Math.sin(f / 9)} /></mesh>
      <mesh position={[0, -0.45, -2.3]}><boxGeometry args={[3.0, 0.5, 0.5]} /><meshStandardMaterial color="#2b2f38" roughness={0.6} /></mesh>
      <CajaStreaming pos={[0.3, -0.12, -2.2]} escala={0.8} />
      <mesh position={[0, -0.55, 1.4]}><boxGeometry args={[3.6, 0.55, 1.3]} /><meshStandardMaterial color="#3a2f35" roughness={0.9} /></mesh>
      <mesh position={[0, -0.05, 1.95]}><boxGeometry args={[3.6, 0.9, 0.35]} /><meshStandardMaterial color="#44363c" roughness={0.9} /></mesh>
      <mesh position={[-1.95, -0.3, 1.5]}><boxGeometry args={[0.35, 0.8, 1.3]} /><meshStandardMaterial color="#44363c" roughness={0.9} /></mesh>
      <mesh position={[1.95, -0.3, 1.5]}><boxGeometry args={[0.35, 0.8, 1.3]} /><meshStandardMaterial color="#44363c" roughness={0.9} /></mesh>
      <mesh position={[-3.6, 0.7, -1.2]}><cylinderGeometry args={[0.03, 0.03, 3.4, 8]} /><meshStandardMaterial color="#222" /></mesh>
      <mesh position={[-3.6, 2.35, -1.2]}><coneGeometry args={[0.5, 0.5, 20, 1, true]} /><meshStandardMaterial color="#ffd9a8" emissive="#ffb866" emissiveIntensity={1.6} side={THREE.DoubleSide} /></mesh>
      <pointLight position={[-3.6, 2.1, -1.0]} color="#ffb866" intensity={7} distance={9} />
      <pointLight position={[0, 0.6, -1.2]} color="#4f8fd8" intensity={5} distance={8} />
      <pointLight position={[0.8, -0.1, -1.7]} color={C.naranja} intensity={2.5 * led} distance={3} />
    </group>
  );
};

/** Estantería de tienda con cajas de cartón; una brilla en naranja desde dentro. */
export const Estanteria: React.FC = () => {
  const f = useCurrentFrame();
  const mala = [[1, 2], [0, 5]];
  return (
    <group position={[0, 0.3, 0]}>
      {[-0.9, 0.5, 1.9].map((y, r) => <mesh key={r} position={[0, y - 0.55, 0]}><boxGeometry args={[11, 0.08, 1.2]} /><meshStandardMaterial color="#59606c" metalness={0.7} roughness={0.4} /></mesh>)}
      {[-5.4, 5.4].map((x) => <mesh key={x} position={[x, 0.5, 0]}><boxGeometry args={[0.1, 3.4, 1.2]} /><meshStandardMaterial color="#59606c" metalness={0.7} roughness={0.4} /></mesh>)}
      {[0, 1, 2].map((r) => Array.from({ length: 8 }, (_, c) => {
        const m = mala.some(([rr, cc]) => rr === r && cc === c);
        return (
          <group key={`${r}-${c}`} position={[-4.6 + c * 1.3, [-0.9, 0.5, 1.9][r] - 0.1, 0]}>
            <mesh><boxGeometry args={[1.0, 0.8, 0.9]} /><meshStandardMaterial color="#8a6a49" roughness={0.9} emissive={m ? C.naranja : "#2a1d10"} emissiveIntensity={m ? 0.9 + 0.4 * Math.sin(f / 7) : 0.5} /></mesh>
            <mesh position={[0, 0.05, 0.46]}><planeGeometry args={[0.7, 0.3]} /><meshStandardMaterial color="#e9e3d3" emissive="#8f8a7c" emissiveIntensity={0.6} /></mesh>
            {m && <pointLight position={[0, 0.2, 0.9]} color={C.naranja} intensity={4} distance={3.5} />}
          </group>
        );
      }))}
      <pointLight position={[0, 3, 4]} color="#cfd9ff" intensity={9} distance={14} />
    </group>
  );
};

/** Avalancha de peticiones: cientos de puntos naranjas desde casas lejanas hacia un servidor que se pone rojo. */
export const Avalancha: React.FC = () => {
  const f = useCurrentFrame();
  const n = 140;
  const sat = interpolate(f, [20, 120], [0.25, 1], { extrapolateRight: "clamp" });
  return (
    <group position={[0, 0, -1]}>
      <group position={[3.2, 0.3, 0]}>
        <mesh><boxGeometry args={[1.5, 3.0, 1.1]} /><meshStandardMaterial color="#1b1e25" roughness={0.4} metalness={0.7} /></mesh>
        {Array.from({ length: 10 }, (_, r) => <mesh key={r} position={[0, 1.2 - r * 0.24, 0.56]}><planeGeometry args={[1.25, 0.12]} /><meshStandardMaterial color="#05070a" emissive={mezcla(C.cian, C.rojo, sat)} emissiveIntensity={1.0 + 2 * sat * ((f + r * 3) % 6 < 3 ? 1 : 0.3)} /></mesh>)}
        <pointLight position={[-1, 0.5, 1.5]} color={mezcla(C.cian, C.rojo, sat)} intensity={6} distance={8} />
      </group>
      {Array.from({ length: 6 }, (_, k) => <mesh key={k} position={[-5.6 + (k % 3) * 0.8, -0.8, -2 + Math.floor(k / 3) * 2.4]}><boxGeometry args={[0.6, 0.45, 0.6]} /><meshStandardMaterial color="#39424f" emissive="#202733" emissiveIntensity={0.8} /></mesh>)}
      {Array.from({ length: n }, (_, i) => {
        const o = rnd("o" + i), vis = (i / n) < sat;
        if (!vis) return null;
        const p = ((f / 60 + o) % 1), sx = -5.2 + rnd("sx" + i) * 1.2, sy = -0.6 + rnd("sy" + i) * 0.4, sz = -2 + rnd("sz" + i) * 4.4;
        const x = sx + (3.2 - 0.9 - sx) * p, y = sy + (0.3 - sy + 0.3) * p + Math.sin(p * Math.PI) * (0.8 + rnd("h" + i) * 1.0), z = sz * (1 - p);
        return <mesh key={i} position={[x, y, z]}><sphereGeometry args={[0.055, 8, 8]} /><meshStandardMaterial color="#000" emissive={C.naranja} emissiveIntensity={2.4} /></mesh>;
      })}
    </group>
  );
};

/** Cable ethernet serpenteando hacia un router; pulsos de luz recorren el cable. */
export const Cable: React.FC = () => {
  const f = useCurrentFrame();
  const curva = new THREE.CatmullRomCurve3([new THREE.Vector3(-5.5, -0.7, 1.5), new THREE.Vector3(-3, -0.2, 0.4), new THREE.Vector3(-1.2, 0.5, 1.1), new THREE.Vector3(0.4, 0.0, -0.2), new THREE.Vector3(1.6, 0.35, 0.3)]);
  const fin = curva.getPoint(1), tan = curva.getTangent(1);
  return (
    <group>
      <mesh><tubeGeometry args={[curva, 160, 0.07, 12, false]} /><meshStandardMaterial color="#14161b" roughness={0.45} metalness={0.2} /></mesh>
      {Array.from({ length: 6 }, (_, i) => {
        const t = ((f / 90 + i / 6) % 1), p = curva.getPoint(t);
        return <mesh key={i} position={p}><sphereGeometry args={[0.1, 12, 12]} /><meshStandardMaterial color="#000" emissive={C.naranja} emissiveIntensity={3} /></mesh>;
      })}
      <group position={fin} quaternion={new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(1, 0, 0), tan)}>
        <mesh position={[0.28, 0, 0]}><boxGeometry args={[0.6, 0.3, 0.26]} /><meshStandardMaterial color="#cfe6f2" transparent opacity={0.55} roughness={0.1} emissive="#4f7f9a" emissiveIntensity={0.7} /></mesh>
        {Array.from({ length: 8 }, (_, i) => <mesh key={i} position={[0.42, -0.1 + i * 0.026 - 0.01, 0]}><boxGeometry args={[0.18, 0.012, 0.2]} /><meshStandardMaterial color="#d9a441" metalness={0.9} roughness={0.25} emissive="#ff8a1f" emissiveIntensity={1.1} /></mesh>)}
      </group>
      <mesh position={[3.1, 0.35, 0]}><boxGeometry args={[2.6, 0.5, 1.3]} /><meshStandardMaterial color="#2c3139" roughness={0.4} metalness={0.5} emissive="#161a21" emissiveIntensity={0.8} /></mesh>
      {[-0.8, -0.35, 0.1, 0.55, 1.0].map((z, i) => <mesh key={i} position={[1.78, 0.38, z * 0.6]}><boxGeometry args={[0.04, 0.16, 0.2]} /><meshStandardMaterial color="#000" emissive={i === 2 ? C.naranja : C.cian} emissiveIntensity={(Math.floor((f + i * 5) / 10) % 2) ? 2.5 : 0.5} /></mesh>)}
      <pointLight position={[0, 1.6, 2.4]} color="#9fc4ff" intensity={5} distance={10} />
    </group>
  );
};

/** Paneles de código que se escriben línea a línea; algunas líneas resaltan en naranja ("escrito de antemano por un humano"). */
export const Codigo: React.FC = () => {
  const f = useCurrentFrame();
  const panel = (x: number, z: number, ry: number, semilla: string, inicio: number) => (
    <group position={[x, 0.6, z]} rotation={[0, ry, 0]}>
      <mesh><boxGeometry args={[3.6, 2.4, 0.06]} /><meshStandardMaterial color="#0b0f16" roughness={0.4} metalness={0.6} emissive="#0c1624" emissiveIntensity={0.9} /></mesh>
      {Array.from({ length: 14 }, (_, i) => {
        const w = 0.4 + rnd(semilla + i) * 2.2, sangria = (rnd(semilla + "s" + i) > 0.55 ? 0.35 : 0), hot = rnd(semilla + "h" + i) > 0.86;
        const k = interpolate(f, [inicio + i * 4, inicio + i * 4 + 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return <mesh key={i} position={[-1.6 + sangria + (w * k) / 2, 1.0 - i * 0.15, 0.04]}><boxGeometry args={[Math.max(0.001, w * k), 0.055, 0.01]} /><meshStandardMaterial color="#000" emissive={hot ? C.naranja : C.cian} emissiveIntensity={hot ? 2.2 : 1.5} /></mesh>;
      })}
    </group>
  );
  return <group>{panel(-1.8, 0, 0.35, "a", 4)}{panel(2.1, -1.6, -0.3, "b", 30)}<pointLight position={[0, 2, 3]} color="#7fd3ff" intensity={6} distance={10} /></group>;
};
