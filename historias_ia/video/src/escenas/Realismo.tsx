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
export const Entorno: React.FC<{ intensidad?: number }> = ({ intensidad = 0.9 }) => {
  const { gl, scene } = useThree();
  useLayoutEffect(() => {
    const pm = new THREE.PMREMGenerator(gl);
    const env = pm.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environment = env; (scene as any).environmentIntensity = intensidad;
    return () => { scene.environment = null; env.dispose(); pm.dispose(); };
  }, [gl, scene, intensidad]);
  return null;
};

/** marca todas las mallas hijas para proyectar y recibir sombras (se reaplica en cada fotograma por si aparecen mallas nuevas) */
export const SombrasAuto: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const ref = useRef<THREE.Group>(null);
  useLayoutEffect(() => { ref.current?.traverse((o: any) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } }); });
  return <group ref={ref}>{children}</group>;
};
