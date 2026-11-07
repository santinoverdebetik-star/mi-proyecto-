// Temas visuales tipo After Effects: cada escena con texto/foto/grafico usa uno distinto (color de acento, gradacion y mezcla) para que NO se vea siempre igual.
export type Estilo = { n: string; a: string; b: string; filtro: string; tinte: string; fondo1: string; fondo2: string };
export const ESTILOS: Estilo[] = [
  { n: "naranja", a: "#ff5a1f", b: "#35d9ff", filtro: "contrast(1.22) saturate(1.1) brightness(0.8)", tinte: "#ff5a1f", fondo1: "#2a3244", fondo2: "#05060a" },
  { n: "rojo", a: "#ff2a3a", b: "#ffe0d0", filtro: "contrast(1.32) saturate(1.25) sepia(0.25) hue-rotate(-12deg) brightness(0.78)", tinte: "#e0141f", fondo1: "#4a1018", fondo2: "#08040a" },
  { n: "cian", a: "#35d9ff", b: "#ffb347", filtro: "contrast(1.28) saturate(0.95) hue-rotate(18deg) brightness(0.84)", tinte: "#1fb8ff", fondo1: "#10344a", fondo2: "#03070d" },
  { n: "verde", a: "#45ff9a", b: "#ffd24a", filtro: "contrast(1.3) saturate(0.8) hue-rotate(55deg) brightness(0.82)", tinte: "#1fd37a", fondo1: "#0f3a2a", fondo2: "#030a07" },
  { n: "magenta", a: "#ff3ad1", b: "#4ad0ff", filtro: "contrast(1.3) saturate(1.2) hue-rotate(-40deg) brightness(0.8)", tinte: "#c81fd3", fondo1: "#3a1050", fondo2: "#07030d" },
  { n: "amarillo", a: "#ffd24a", b: "#ff5a1f", filtro: "grayscale(0.4) contrast(1.38) sepia(0.3) brightness(0.82)", tinte: "#ffb800", fondo1: "#4a3a0f", fondo2: "#0a0803" },
  { n: "bn", a: "#ffffff", b: "#ff3a3a", filtro: "grayscale(1) contrast(1.45) brightness(0.8)", tinte: "#ffffff", fondo1: "#2a2a2e", fondo2: "#030303" },
];
export const estilo = (i?: number) => ESTILOS[((i ?? 0) % ESTILOS.length + ESTILOS.length) % ESTILOS.length];
