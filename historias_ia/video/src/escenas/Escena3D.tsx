import React, { useMemo } from "react";
import { AbsoluteFill, interpolate, random, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { Img, staticFile } from "remotion";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { Entorno, RB, SombrasAuto } from "./Realismo";
import { C } from "../estilo";
import { Antena, Calendario, CamaraSeguridad, Dinero, Dominos, Engranajes, Escudo, Hdmi, Latido, Llave, Lupa, Mando, Movil, Nube, Ojo, Paquetes, PcAntiguo, Placa, Password, Reloj, Router, TvPlay } from "./Objetos3D_b";
import { Apagon, Avalancha, Cable, Candado, Codigo, Estanteria, Globo, Sala, CajaStreaming, CasasRed, Duplicacion, Fabrica, Laptop, Manometro, Pulsos, Rack, Radar } from "./Objetos3D";

export type Objeto3D = "router" | "camara" | "movil" | "pc_antiguo" | "reloj" | "calendario" | "placa" | "llave" | "dominos" | "escudo" | "dinero" | "hdmi" | "password" | "engranajes" | "latido" | "paquetes" | "antena" | "lupa" | "mando" | "nube" | "ojo" | "tv_play" | "globo" | "sala" | "estanteria" | "avalancha" | "cable" | "codigo" | "casas_red" | "fabrica" | "candado" | "candado_agujero" | "apagon" | "duplicacion" | "rack" | "radar" | "intrusion" | "contagio" | "manometro" | "cajas15" | "caja_led" | "caja_tv" | "nucleo" | "red" | "puerta" | "pantalla_rota";

/** Camara que se acerca con un leve arco (dolly + deriva), como los planos lentos del video de referencia. */
const Camara: React.FC<{ desde: [number, number, number]; hasta: [number, number, number]; mira: [number, number, number]; miraHasta?: [number, number, number]; total: number }> = ({ desde, hasta, mira, miraHasta, total }) => {
  const f = useCurrentFrame();
  const { camera } = useThree();
  const t = interpolate(f, [0, total], [0, 1], { extrapolateRight: "clamp" });
  const e = t * t * (3 - 2 * t) * 0.6 + t * 0.4;
  const p = desde.map((d, i) => d + (hasta[i] - d) * e);
  const deriva = Math.sin(f / 70) * 0.04;
  const m = miraHasta ? mira.map((v, i) => v + (miraHasta[i] - v) * e) : mira;
  const Z = 0.78;                                                   // plano mas cerrado, como el objeto 'protagonista' del video de referencia
  camera.position.set(m[0] + (p[0] - m[0]) * Z + deriva, m[1] + (p[1] - m[1]) * Z + deriva * 0.6, m[2] + (p[2] - m[2]) * Z);
  camera.lookAt(m[0], m[1], m[2]);
  camera.updateProjectionMatrix();
  return null;
};

const Suelo: React.FC<{ y?: number; color?: string }> = ({ y = -1, color = "#07080a" }) => (
  <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, y, 0]}>
    <planeGeometry args={[60, 60]} />
    <meshStandardMaterial color={color} roughness={0.35} metalness={0.7} />
  </mesh>
);

const CajaTV: React.FC = () => {
  const f = useCurrentFrame();
  const led = (Math.floor(f / 12) % 2) === 0 ? 1 : 0.15;                        // el LED parpadea
  return (
    <group>
      {/* televisor apagado */}
      <mesh position={[0, 0.9, -1.2]}><RB args={[4.2, 2.4, 0.08]} /><meshStandardMaterial color="#0c0d10" roughness={0.3} metalness={0.6} /></mesh>
      <mesh position={[0, 0.9, -1.15]}><planeGeometry args={[4.0, 2.2]} /><meshStandardMaterial color="#05070b" roughness={0.05} metalness={1} emissive="#10243a" emissiveIntensity={1.1} /></mesh>
      <mesh position={[0, -0.35, -1.2]}><RB args={[0.5, 0.35, 0.3]} /><meshStandardMaterial color="#0a0a0c" roughness={0.4} metalness={0.8} /></mesh>
      {/* caja de streaming */}
      <mesh position={[0, -0.78, 0.2]}><RB args={[1.5, 0.22, 1.1]} /><meshStandardMaterial color="#2a2d34" roughness={0.45} metalness={0.35} /></mesh>
      <mesh position={[0.52, -0.67, 0.76]}><sphereGeometry args={[0.035, 16, 16]} /><meshStandardMaterial color={C.naranja} emissive={C.naranja} emissiveIntensity={6 * led} /></mesh>
      <pointLight position={[-1.5, 0.6, 1.5]} color="#4f8fd8" intensity={2.2} distance={8} decay={2} />
      <pointLight position={[0.52, -0.55, 0.9]} color={C.naranja} intensity={9 * led} distance={7} decay={2} />
    </group>
  );
};

const Nucleo: React.FC = () => {
  const f = useCurrentFrame();
  const r = f / 90;
  return (
    <group position={[0, 0.8, 0]}>
      <mesh rotation={[r * 0.4, r * 0.6, 0]}><icosahedronGeometry args={[1.15, 1]} /><meshStandardMaterial color="#111" wireframe emissive={C.naranja} emissiveIntensity={1.0} /></mesh>
      <mesh><sphereGeometry args={[0.55 + Math.sin(f / 20) * 0.03, 48, 48]} /><meshStandardMaterial color="#220800" emissive={C.naranja} emissiveIntensity={1.25} roughness={0.5} /></mesh>
      {[1.7, 2.1, 2.55].map((rad, i) => (
        <mesh key={i} rotation={[Math.PI / 2 + i * 0.5, r * (0.5 + i * 0.25), i]}><torusGeometry args={[rad, 0.012, 8, 160]} /><meshStandardMaterial color="#000" emissive={i === 1 ? C.cian : C.naranja} emissiveIntensity={1.3} /></mesh>
      ))}
      <pointLight color={C.naranja} intensity={14} distance={9} decay={2} />
    </group>
  );
};

const Red: React.FC<{ infeccion: number }> = ({ infeccion }) => {
  const f = useCurrentFrame();
  const nodos = useMemo(() => Array.from({ length: 42 }, (_, i) => new THREE.Vector3((random(`a${i}`) - 0.5) * 9, random(`b${i}`) * 3.6 - 0.9, (random(`c${i}`) - 0.5) * 7)), []);
  const enlaces = useMemo(() => {
    const out: [number, number][] = [];
    nodos.forEach((n, i) => nodos.forEach((m, j) => { if (j > i && n.distanceTo(m) < 2.6) out.push([i, j]); }));
    return out;
  }, [nodos]);
  const prog = interpolate(f, [10, 10 + infeccion], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const orden = useMemo(() => nodos.map((n) => n.distanceTo(nodos[0])), [nodos]);
  const maxd = Math.max(...orden);
  const inf = (i: number) => orden[i] / maxd < prog;
  return (
    <group>
      {nodos.map((n, i) => <mesh key={i} position={n}><sphereGeometry args={[inf(i) ? 0.09 : 0.06, 12, 12]} /><meshStandardMaterial color="#000" emissive={inf(i) ? C.naranja : C.cian} emissiveIntensity={inf(i) ? 1.8 : 1.0} /></mesh>)}
      {enlaces.map(([a, b], k) => {
        const A = nodos[a], B = nodos[b]; const mid = A.clone().add(B).multiplyScalar(0.5); const len = A.distanceTo(B);
        const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
        const rojo = inf(a) && inf(b);
        return <mesh key={k} position={mid} quaternion={q}><cylinderGeometry args={[0.008, 0.008, len, 4]} /><meshStandardMaterial color="#000" emissive={rojo ? C.naranja : C.cian} emissiveIntensity={rojo ? 1.5 : 0.6} /></mesh>;
      })}
      <pointLight position={[nodos[0].x, nodos[0].y, nodos[0].z]} color={C.naranja} intensity={8} distance={8} />
    </group>
  );
};

const Puerta: React.FC = () => {
  const f = useCurrentFrame();
  const abre = interpolate(f, [30, 110], [0, 1.2], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <group>
      <mesh position={[0, 1, -2]}><RB args={[5, 3.6, 0.2]} /><meshStandardMaterial color="#090a0c" roughness={0.8} /></mesh>
      <group position={[-1, 0, -1.85]} rotation={[0, abre, 0]}><mesh position={[1, 0.95, 0]}><RB args={[2, 3.1, 0.08]} /><meshStandardMaterial color="#14110e" roughness={0.6} metalness={0.2} /></mesh></group>
      <mesh position={[0, 0.95, -2.05]}><planeGeometry args={[2, 3.1]} /><meshStandardMaterial color="#000" emissive={C.naranja} emissiveIntensity={abre * 2.2} /></mesh>
      <pointLight position={[0, 1, -1.5]} color={C.naranja} intensity={abre * 30} distance={10} />
    </group>
  );
};

const PantallaRota: React.FC = () => {
  const f = useCurrentFrame();
  const trozos = useMemo(() => Array.from({ length: 34 }, (_, i) => ({ p: [(random(`x${i}`) - 0.5) * 3.8, (random(`y${i}`) - 0.5) * 2.1 + 0.9, 0], r: [random(`r${i}`) * 3, random(`s${i}`) * 3, random(`t${i}`) * 3], s: 0.25 + random(`z${i}`) * 0.6 })), []);
  const rompe = interpolate(f, [24, 70], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <group>
      <mesh position={[0, 0.9, -0.3]}><planeGeometry args={[4, 2.2]} /><meshStandardMaterial color="#000" emissive={C.naranja} emissiveIntensity={1.4} /></mesh>
      {trozos.map((t, i) => (
        <mesh key={i} position={[t.p[0] * (1 + rompe * 0.5), t.p[1] + rompe * (random(`d${i}`) - 0.7) * 1.2, rompe * (0.2 + random(`q${i}`) * 2.2)]} rotation={[t.r[0] * rompe, t.r[1] * rompe, t.r[2] * rompe]}>
          <RB args={[t.s, t.s * 0.8, 0.01]} /><meshPhysicalMaterial color="#9fb8c8" transmission={0.9} roughness={0.05} metalness={0} transparent opacity={0.55} />
        </mesh>
      ))}
    </group>
  );
};

const Intrusion: React.FC = () => {
  const f = useCurrentFrame();
  const inf = interpolate(f, [55, 100], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <group>
      <CajaStreaming pos={[-2.6, -0.88, 0.3]} />
      <pointLight position={[-2.1, -0.4, 0.9]} color={C.naranja} intensity={5} distance={5} />
      <Laptop pos={[1.4, -0.95, 0]} rotY={-0.5} infeccion={inf} />
      <Pulsos a={[-2.1, -0.75, 0.6]} b={[0.9, 0.2, 0.3]} arco={1.0} desde={8} n={8} />
    </group>
  );
};

const Contagio: React.FC = () => {
  const f = useCurrentFrame();
  const a = interpolate(f, [5, 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const b = interpolate(f, [88, 128], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const c = interpolate(f, [150, 190], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <group>
      <Laptop pos={[-2.8, -0.95, 0.4]} rotY={0.35} infeccion={a} />
      <Laptop pos={[1.2, -0.95, -2.2]} rotY={-0.05} infeccion={b} escala={0.9} />
      <Laptop pos={[5.0, -0.95, -5.2]} rotY={-0.4} infeccion={c} escala={0.8} />
      <Pulsos a={[-2.4, 0.3, 0.2]} b={[0.9, 0.2, -2.1]} arco={1.3} desde={50} hasta={135} n={6} />
      <Pulsos a={[1.3, 0.2, -2.3]} b={[4.7, 0.2, -5.1]} arco={1.4} desde={118} hasta={200} n={6} />
    </group>
  );
};

const Cajas15: React.FC = () => {
  const f = useCurrentFrame();
  const orden = Array.from({ length: 15 }, (_, i) => { const r = Math.floor(i / 5), c = i % 5; return { i, x: ((r % 2 === 0 ? c : 4 - c) - 2) * 2.1, z: -r * 1.9 + 1.0 }; });
  return (
    <group>
      {orden.map((o) => {
        const on = f > 10 + o.i * 5 ? 1 : 0;
        return <CajaStreaming key={o.i} pos={[o.x, -0.88, o.z]} led={on ? C.naranja : C.cian} fase={o.i * 3} activa={on ? 1 : 0.5} />;
      })}
      {orden.slice(1).map((o, k) => {
        const p = orden[k]; const A = new THREE.Vector3(p.x, -0.75, p.z), B = new THREE.Vector3(o.x, -0.75, o.z); const mid = A.clone().add(B).multiplyScalar(0.5);
        const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
        const on = f > 10 + (k + 1) * 5;
        return <mesh key={k} position={mid} quaternion={q}><cylinderGeometry args={[0.014, 0.014, A.distanceTo(B), 6]} /><meshStandardMaterial color="#000" emissive={on ? C.naranja : C.cian} emissiveIntensity={on ? 2 : 0.5} /></mesh>;
      })}
      <pointLight position={[0, 3, -1]} color={C.naranja} intensity={14} distance={14} />
      <pointLight position={[-3, 2.5, 3]} color="#7fb0ff" intensity={6} distance={12} />
    </group>
  );
};

type Cam = { desde: [number, number, number]; hasta: [number, number, number]; mira: [number, number, number]; miraHasta?: [number, number, number] };
const CAMS_NUEVAS: Record<string, Cam> = {
  router: { desde: [0, 1.2, 7.0], hasta: [0.4, 1.0, 5.0], mira: [0, 0.6, 0] },
  camara: { desde: [-2.5, 1.0, 6.8], hasta: [1.6, 0.9, 5.2], mira: [0, 0.6, 0.2] },
  movil: { desde: [0, 0.9, 6.2], hasta: [0.2, 0.8, 4.4], mira: [0, 0.7, 0] },
  pc_antiguo: { desde: [-3.2, 1.2, 7.2], hasta: [0.6, 1.0, 5.4], mira: [0.4, 0.6, 0] },
  reloj: { desde: [0, 0.9, 6.4], hasta: [0, 0.9, 4.4], mira: [0, 0.8, 0] },
  calendario: { desde: [-1, 1.0, 7.4], hasta: [0.3, 0.9, 5.4], mira: [0, 0.8, 0] },
  placa: { desde: [0, 5.2, 9.0], hasta: [0.6, 4.2, 7.4], mira: [0, 0.2, 0] },
  llave: { desde: [1.2, 0.8, 6.4], hasta: [0.1, 0.6, 4.4], mira: [0, 0.5, 0.3] },
  dominos: { desde: [-5.5, 0.4, 5.0], hasta: [2.6, 0.5, 4.8], mira: [-2, -0.5, 0], miraHasta: [3, -0.5, 0] },
  escudo: { desde: [0, 0.9, 6.8], hasta: [0.3, 0.8, 4.8], mira: [0, 0.7, 0] },
  dinero: { desde: [0, 2.2, 6.4], hasta: [0, 1.4, 4.6], mira: [0, -0.4, 0] },
  hdmi: { desde: [-1, 1.0, 6.6], hasta: [0.6, 0.6, 4.6], mira: [0.3, 0.3, 0] },
  password: { desde: [0, 0.9, 7.4], hasta: [0.2, 0.8, 5.6], mira: [0, 0.7, 0] },
  engranajes: { desde: [0, 0.8, 7.4], hasta: [0.3, 0.8, 5.6], mira: [0, 0.7, 0] },
  latido: { desde: [0, 0.6, 8.2], hasta: [0, 0.6, 6.0], mira: [0, 0.5, 0] },
  paquetes: { desde: [-2, 1.2, 8.4], hasta: [2, 1.0, 7.0], mira: [0, 0.4, 0] },
  antena: { desde: [-3, 0.6, 8.0], hasta: [2, 2.0, 7.0], mira: [0, 1.6, 0] },
  lupa: { desde: [0, 0.6, 7.2], hasta: [0.3, 0.5, 5.6], mira: [0, 0.4, 0] },
  mando: { desde: [-2.2, 0.8, 6.4], hasta: [0.8, 0.9, 5.0], mira: [0, 1.0, 0] },
  nube: { desde: [0, 0.6, 7.6], hasta: [0.2, 0.9, 5.6], mira: [0, 0.5, 0] },
  ojo: { desde: [0, 0.9, 6.4], hasta: [0.2, 0.9, 4.6], mira: [0, 0.8, 0] },
  tv_play: { desde: [-1.5, 0.8, 8.0], hasta: [0.5, 0.6, 6.4], mira: [0, 0.4, 0] },

  globo: { desde: [0, 0.9, 6.2], hasta: [0.6, 0.9, 4.4], mira: [0, 0.7, 0] },
  sala: { desde: [-2.5, 1.5, 9.0], hasta: [1.6, 1.0, 7.0], mira: [0, 0.2, -1.5], miraHasta: [0.2, 0.1, -2] },
  estanteria: { desde: [-4.2, 1.2, 6.2], hasta: [3.2, 0.9, 5.4], mira: [-1, 0.5, 0], miraHasta: [1.5, 0.5, 0] },
  avalancha: { desde: [-1.0, 1.6, 9.0], hasta: [1.2, 1.0, 7.0], mira: [0, 0.4, -1] },
  cable: { desde: [-3.6, 1.0, 4.6], hasta: [1.2, 0.8, 4.2], mira: [-1.5, 0.0, 0.5], miraHasta: [1.8, 0.3, 0] },
  codigo: { desde: [0, 0.7, 7.2], hasta: [0.2, 0.7, 5.2], mira: [0, 0.6, -0.5] },
  casas_red: { desde: [-5, 5.6, 6.8], hasta: [4, 4.4, 5.2], mira: [0, -0.6, -2], miraHasta: [1, -0.8, -2.5] },
  fabrica: { desde: [-3.5, 0.9, 5.2], hasta: [2.6, 0.2, 3.9], mira: [0, -0.6, 0], miraHasta: [1.2, -0.7, 0] },
  candado: { desde: [1.2, 0.8, 8.2], hasta: [0.4, 0.5, 6.0], mira: [0, 0.4, 0] },
  candado_agujero: { desde: [1.2, 0.8, 8.2], hasta: [0.2, 0.3, 5.2], mira: [0, 0.4, 0] },
  apagon: { desde: [0, 0.8, 13.0], hasta: [0, 0.6, 10.2], mira: [0, 0.6, -1] },
  duplicacion: { desde: [0, 1.6, 4.2], hasta: [0, 2.8, 7.2], mira: [0, 0.8, -1] },
  rack: { desde: [-3.5, 0.9, 7.4], hasta: [1.8, 0.8, 5.8], mira: [0, 0.6, -1] },
  radar: { desde: [0, 2.6, 5.2], hasta: [0, 2.0, 3.8], mira: [0, 0.2, 0] },
};

const CONFIG: Partial<Record<Objeto3D, Cam>> = {
  intrusion: { desde: [0.6, 1.3, 7.8], hasta: [-0.3, 0.7, 5.4], mira: [-0.5, -0.2, 0] },
  contagio: { desde: [-4.2, 1.6, 6.8], hasta: [1.6, 1.4, 5.2], mira: [-1.5, -0.2, -0.8], miraHasta: [2.2, -0.3, -3.2] },
  manometro: { desde: [0.5, 0.35, 6.4], hasta: [0.1, 0.1, 4.3], mira: [0, 0, 0] },
  cajas15: { desde: [-4.6, 2.5, 6.4], hasta: [3.6, 2.1, 4.8], mira: [0, -0.7, -1.0] },
  caja_led: { desde: [1.5, -0.25, 3.2], hasta: [0.75, -0.55, 1.9], mira: [0.5, -0.62, 0.7] },
  caja_tv: { desde: [2.2, 0.5, 6.6], hasta: [1.0, -0.1, 4.0], mira: [0.2, -0.1, -0.2] },
  nucleo: { desde: [0, 1.0, 7.5], hasta: [0, 0.9, 4.6], mira: [0, 0.8, 0] },
  red: { desde: [-4.5, 1.6, 7.5], hasta: [3.2, 1.3, 6.2], mira: [0, 0.8, 0] },
  puerta: { desde: [0, 0.8, 6.5], hasta: [0, 0.9, 3.2], mira: [0, 0.9, -2] },
  pantalla_rota: { desde: [0, 0.9, 6.2], hasta: [0, 0.9, 3.4], mira: [0, 0.9, 0] },
};

/** Factor de resolucion interna del 3D (0.6 = 36 % de los pixeles). Render por software: bajarlo acelera mucho; el grano y la vineta disimulan la perdida de nitidez. */
const GL_K = 0.6;

/** Nivel de luz segun lo que cuenta la narracion: "noche" = amenaza/misterio, "media" = explicacion, "clara" = datos/ciencia/respiro. */
export type Luz = "noche" | "media" | "clara";
const LUZ: Record<Luz, { fondo: string; ambiente: number; relleno: number; suelo: string; hemi: number }> = {
  noche: { fondo: "#101826", ambiente: 1.5, relleno: 2.0, suelo: "#1b2230", hemi: 0.8 },
  media: { fondo: "#1a2536", ambiente: 2.2, relleno: 2.8, suelo: "#2a3445", hemi: 1.4 },
  clara: { fondo: "#2c3a52", ambiente: 3.0, relleno: 3.6, suelo: "#3a4658", hemi: 2.0 },
};

/** Fondo de FOTO REAL (habitacion / lugar) detras del 3D: desenfoque leve, gradacion segun la luz y un lento empuje de camara. */
const FondoFoto: React.FC<{ archivo: string; luz: Luz; pos?: string }> = ({ archivo, luz, pos = "50% 50%" }) => {
  const f = useCurrentFrame(); const { durationInFrames } = useVideoConfig();
  const t = interpolate(f, [0, durationInFrames], [0, 1]);
  const br = { noche: 0.66, media: 0.8, clara: 0.95 }[luz];
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#0b0e14" }}>
      <Img src={staticFile(archivo)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: pos, transform: `scale(${1.04 + 0.07 * t})`,
        filter: `blur(4px) brightness(${br}) contrast(1.06) saturate(0.95)` }} />
    </AbsoluteFill>
  );
};

/** sombra suave en el suelo bajo el objeto (para que no flote sobre la foto) */
const SombraSuelo: React.FC = () => (
  <group position={[0, -0.985, 0]} rotation={[-Math.PI / 2, 0, 0]}>
    {[[3.4, 0.10], [2.4, 0.12], [1.5, 0.14]].map(([r, o], i) => <mesh key={i}><circleGeometry args={[r, 48]} /><meshBasicMaterial color="#000" transparent opacity={o} depthWrite={false} /></mesh>)}
  </group>
);

export const Escena3D: React.FC<{ objeto: Objeto3D; infeccion?: number; luz?: Luz; inv?: boolean; fondo?: string; fondoPos?: string }> = ({ objeto, infeccion = 120, luz = "noche", inv = false, fondo, fondoPos }) => {
  const L = LUZ[luz];
  const { width, height, durationInFrames } = useVideoConfig();
  const c0 = (CAMS_NUEVAS[objeto] ?? CONFIG[objeto])!;
  const c: Cam = inv ? { ...c0, desde: c0.hasta, hasta: c0.desde, mira: c0.miraHasta ?? c0.mira, miraHasta: c0.miraHasta ? c0.mira : undefined } : c0;
  return (
    <AbsoluteFill style={{ background: L.fondo }}>
      {fondo && <FondoFoto archivo={fondo} luz={luz} pos={fondoPos} />}
      <div style={{ width: width * GL_K, height: height * GL_K, transform: `scale(${1 / GL_K})`, transformOrigin: "0 0" }}>
      <ThreeCanvas width={width * GL_K} height={height * GL_K} camera={{ fov: 38, near: 0.1, far: 80, position: c.desde }} shadows gl={{ antialias: false, alpha: !!fondo }}>
        {!fondo && <color attach="background" args={[L.fondo]} />}
        {!fondo && <fog attach="fog" args={[L.fondo, 7, 22]} />}
        <Entorno intensidad={0.55 + 0.12 * (L.ambiente - 1.5)} />
        <ambientLight intensity={L.ambiente * 0.45} />
        <hemisphereLight args={["#bcd4ff", "#201a18", L.hemi * 0.5]} />
        <directionalLight position={[-4, 5, 4]} intensity={L.relleno * 0.6} color="#7fb0ff" />
        <directionalLight position={[3, 6, 5]} intensity={2.3} color="#fff1dc" castShadow shadow-mapSize={[512, 512]} shadow-camera-left={-7} shadow-camera-right={7} shadow-camera-top={7} shadow-camera-bottom={-7} shadow-camera-near={1} shadow-camera-far={22} shadow-bias={-0.0004} />
        <directionalLight position={[5, 2, 3]} intensity={0.35} color="#ffb48a" />
        <Camara desde={c.desde} hasta={c.hasta} mira={c.mira} miraHasta={c.miraHasta} total={durationInFrames} />
        {objeto !== "manometro" && !fondo && <Suelo color={L.suelo} />}
        {fondo && objeto !== "manometro" && <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.985, 0]} receiveShadow><planeGeometry args={[40, 40]} /><shadowMaterial opacity={0.5} /></mesh>}
        <SombrasAuto>
        {(objeto === "caja_tv" || objeto === "caja_led") && <CajaTV />}
        {objeto === "nucleo" && <Nucleo />}
        {objeto === "intrusion" && <Intrusion />}
        {objeto === "contagio" && <Contagio />}
        {objeto === "manometro" && <Manometro total={durationInFrames} />}
        {objeto === "cajas15" && <Cajas15 />}
        {objeto === "casas_red" && <CasasRed />}
        {objeto === "globo" && <Globo />}
        {objeto === "router" && <Router />}
        {objeto === "camara" && <CamaraSeguridad />}
        {objeto === "movil" && <Movil />}
        {objeto === "pc_antiguo" && <PcAntiguo />}
        {objeto === "reloj" && <Reloj />}
        {objeto === "calendario" && <Calendario />}
        {objeto === "placa" && <Placa />}
        {objeto === "llave" && <Llave />}
        {objeto === "dominos" && <Dominos />}
        {objeto === "escudo" && <Escudo />}
        {objeto === "dinero" && <Dinero />}
        {objeto === "hdmi" && <Hdmi />}
        {objeto === "password" && <Password />}
        {objeto === "engranajes" && <Engranajes />}
        {objeto === "latido" && <Latido />}
        {objeto === "paquetes" && <Paquetes />}
        {objeto === "antena" && <Antena />}
        {objeto === "lupa" && <Lupa />}
        {objeto === "mando" && <Mando />}
        {objeto === "nube" && <Nube />}
        {objeto === "ojo" && <Ojo />}
        {objeto === "tv_play" && <TvPlay />}

        {objeto === "sala" && <Sala pared={!fondo} />}
        {objeto === "estanteria" && <Estanteria />}
        {objeto === "avalancha" && <Avalancha />}
        {objeto === "cable" && <Cable />}
        {objeto === "codigo" && <Codigo />}
        {objeto === "fabrica" && <Fabrica />}
        {objeto === "candado" && <Candado />}
        {objeto === "candado_agujero" && <Candado agujero />}
        {objeto === "apagon" && <Apagon />}
        {objeto === "duplicacion" && <Duplicacion />}
        {objeto === "rack" && <Rack />}
        {objeto === "radar" && <Radar />}
        {objeto === "red" && <Red infeccion={infeccion} />}
        {objeto === "puerta" && <Puerta />}
        {objeto === "pantalla_rota" && <PantallaRota />}
        </SombrasAuto>
      </ThreeCanvas>
      </div>
    </AbsoluteFill>
  );
};
