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
