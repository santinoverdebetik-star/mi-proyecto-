// Guion visual del video: cada escena = un tramo de la narracion. dur en segundos.
// Para un video real: una escena por frase/idea del guion (plano de 3-7 s), alineadas con los tiempos de la voz.
import type { Luz, Objeto3D } from "./escenas/Escena3D";

export type Escena =
  | { tipo: "3d"; dur: number; objeto: Objeto3D; infeccion?: number; flash?: number; luz?: Luz }
  | { tipo: "diagrama"; dur: number; titulo?: string; escala?: number; ritmo?: number; nodos: any[]; enlaces: [string, string][]; infecta?: string[] }
  | { tipo: "titular"; dur: number; lineas: string[]; resalta?: number; lado?: "izq" | "centro" }
  | { tipo: "imagen"; dur: number; archivo: string; brillo?: string };

export const DEMO: Escena[] = [
  { tipo: "3d", dur: 4, objeto: "caja_tv" },
  { tipo: "diagrama", dur: 4, titulo: "Una casa. Cinco dispositivos.", nodos: [
      { id: "casa", x: 960, y: 520, icono: "casa", etiqueta: "tu casa" }, { id: "tv", x: 960, y: 860, icono: "tv", etiqueta: "tv box" },
      { id: "pc", x: 1380, y: 760, icono: "pc", etiqueta: "laptop" }, { id: "movil", x: 1450, y: 330, icono: "movil", etiqueta: "móvil" },
      { id: "cam", x: 480, y: 330, icono: "camara", etiqueta: "cámara" }, { id: "router", x: 500, y: 760, icono: "router", etiqueta: "router" } ],
    enlaces: [["casa", "tv"], ["casa", "pc"], ["casa", "movil"], ["casa", "cam"], ["casa", "router"]], infecta: ["tv", "pc", "router"] },
  { tipo: "3d", dur: 4, objeto: "red", infeccion: 90 },
  { tipo: "3d", dur: 4, objeto: "nucleo" },
  { tipo: "titular", dur: 3, lineas: ["NEW", "GUEST"], resalta: 1, lado: "izq" },
];
