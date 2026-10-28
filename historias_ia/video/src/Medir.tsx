import React from "react";
import { Sequence, Series } from "remotion";
import { Escena3D, type Objeto3D } from "./escenas/Escena3D";

export const OBJETOS: Objeto3D[] = ["router", "camara", "movil", "pc_antiguo", "reloj", "calendario", "placa", "llave", "dominos", "escudo", "dinero", "hdmi", "password", "engranajes", "latido", "paquetes", "antena", "lupa", "mando", "nube", "ojo", "tv_play", "globo", "sala", "estanteria", "avalancha", "cable", "codigo", "casas_red", "fabrica", "candado", "candado_agujero", "apagon", "duplicacion", "rack", "radar", "intrusion", "contagio", "manometro", "cajas15", "caja_led", "caja_tv", "nucleo", "red", "puerta", "pantalla_rota"];
export const TIEMPOS = [0, 40, 90, 150];

/** composicion de calibracion: cada objeto en 4 instantes de su animacion (1 fotograma cada uno); la consola registra su caja envolvente */
export const Medir: React.FC = () => (
  <Series>
    {OBJETOS.flatMap((o) => TIEMPOS.map((t) => (
      <Series.Sequence key={o + t} durationInFrames={1}><Sequence from={-t}><Escena3D objeto={o} luz="media" medir={t} /></Sequence></Series.Sequence>
    )))}
  </Series>
);
