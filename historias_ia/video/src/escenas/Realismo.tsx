import React, { useLayoutEffect, useRef } from "react";
import { extend, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";

extend({ RoundedBoxGeometry });

/** caja con bordes biselados (los objetos reales no tienen aristas perfectas): el radio se adapta al lado mas fino */
export const RB: React.FC<{ args: [number, number, number] }> = ({ args }) => {
  const r = Math.min(0.045, Math.min(args[0], args[1], args[2]) * 0.35);
  // @ts-ignore: elemento registrado con extend()
  return <roundedBoxGeometry args={[args[0], args[1], args[2], 2, r]} />;
};

/** iluminacion basada en imagen (reflejos realistas en metales, plasticos y cristales) con un estudio procedural: no descarga nada */
let _envCache: { gl: any; tex: THREE.Texture } | null = null;
export const Entorno: React.FC<{ intensidad?: number }> = ({ intensidad = 0.9 }) => {
  const { gl, scene } = useThree();
  useLayoutEffect(() => {
    if (!_envCache || _envCache.gl !== gl) {                       // se genera UNA vez por contexto WebGL (regenerarlo en cada fotograma triplicaba el tiempo de render)
      const pm = new THREE.PMREMGenerator(gl);
      _envCache = { gl, tex: pm.fromScene(new RoomEnvironment(), 0.04).texture }; pm.dispose();
    }
    scene.environment = _envCache.tex; (scene as any).environmentIntensity = intensidad;
    return () => { scene.environment = null; };
  }, [gl, scene, intensidad]);
  return null;
};

/** marca todas las mallas hijas para proyectar y recibir sombras (se reaplica en cada fotograma por si aparecen mallas nuevas) */
export const SombrasAuto: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const ref = useRef<THREE.Group>(null);
  useLayoutEffect(() => { ref.current?.traverse((o: any) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } }); });
  return <group ref={ref}>{children}</group>;
};

/* Limite de luces puntuales por clip: el render por software (sin GPU) cuesta casi lineal por luz. Con el entorno HDRI ya hay luz de relleno,
   asi que se conservan solo hasta 2 luces de acento (naranja/rojo/cian) y 1 luz neutra. */
let _acento = 0, _neutra = 0;
export const reiniciarLuces = () => { _acento = 0; _neutra = 0; };
export const PL: React.FC<any> = (props) => {
  const c = String(props.color ?? "").toLowerCase();
  const esAcento = c === "#ff5a1f" || c === "#e0201b" || c === "#35d9ff" || c.startsWith("#ff") || c.startsWith("#d0") || c.startsWith("#c8");
  if (esAcento) { if (_acento++ >= 2) return null; } else { if (_neutra++ >= 1) return null; }
  return <pointLight {...props} />;
};

/** Solo para calibrar: mide la caja envolvente (sin particulas, anillos ni luces) del objeto y la escribe en la consola del navegador. */
export const MedidorBBox: React.FC<{ nombre: string; t: number; children: React.ReactNode }> = ({ nombre, t, children }) => {
  const ref = useRef<THREE.Group>(null);
  useLayoutEffect(() => {
    const g = ref.current; if (!g) return;
    g.updateMatrixWorld(true);
    const box = new THREE.Box3(); let n = 0;
    g.traverse((o: any) => {
      if (!o.isMesh || !o.geometry) return;
      const m = Array.isArray(o.material) ? o.material[0] : o.material;
      if (m && (m.isMeshBasicMaterial || m.transparent)) return;                  // anillos, ondas, cristales
      o.geometry.computeBoundingSphere(); if (o.geometry.boundingSphere.radius < 0.12) return;   // puntos y luces pequeñas
      box.expandByObject(o); n++;
    });
    console.log("BBOX " + JSON.stringify({ nombre, t, n, minY: +box.min.y.toFixed(3), maxY: +box.max.y.toFixed(3), minX: +box.min.x.toFixed(3), maxX: +box.max.x.toFixed(3), minZ: +box.min.z.toFixed(3), maxZ: +box.max.z.toFixed(3) }));
  });
  return <group ref={ref}>{children}</group>;
};
