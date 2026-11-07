import React from "react";
import { AbsoluteFill, Audio, Series, staticFile } from "remotion";
import { Acabado, Fuentes, Flash } from "./Capas";
import { FPS } from "./estilo";
import { Titular } from "./escenas/Titular";
import { Diagrama } from "./escenas/Diagrama";
import { Escena3D } from "./escenas/Escena3D";
import { Imagen } from "./escenas/Imagen";
import { Foto } from "./escenas/Foto";
import { Comparar, Roja, Transicion } from "./escenas/Pantallas";
import { Casa, Grilla, MapaPuntos, Numero, Puerta } from "./escenas/Info2D";
import { Anillos, Barras, Cuadricula, Dato, Flujo, Frase, Globo2D, Lluvia, Ondas, Radar, Terminal } from "./escenas/Inserto";
import type { Escena } from "./guion";
const HUE = [0, -18, 150, 95, -65, 40, 0];                           // variedad de color en los graficos 2D (hue-rotate segun el tema de la escena)

export const duracionTotal = (e: Escena[]) => Math.round(e.reduce((s, x) => s + x.dur, 0) * FPS);

export const Historia: React.FC<{ escenas: Escena[]; voz?: string; musica?: string; volMusica?: number }> = ({ escenas, voz, musica, volMusica = 0.12 }) => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Fuentes />
    <Series>
      {escenas.map((e, i) => (
        <Series.Sequence key={i} durationInFrames={Math.round(e.dur * FPS)}>
          <Transicion tipo={e.trans} est={e.est}>
          <AbsoluteFill style={["radar", "barras", "globo2d", "terminal", "diagrama"].includes(e.tipo) ? { filter: `hue-rotate(${HUE[(e.est ?? 0) % 7]}deg)${(e.est ?? 0) % 7 === 6 ? " grayscale(0.85)" : ""}` } : undefined}>
          {e.tipo === "3d" && <Escena3D objeto={e.objeto} infeccion={e.infeccion} luz={e.luz} inv={e.inv} fondo={e.fondo} fondoPos={e.fondoPos} calidad={e.calidad} />}
          {e.tipo === "diagrama" && <Diagrama nodos={e.nodos} enlaces={e.enlaces} infecta={e.infecta} titulo={e.titulo} escala={e.escala} ritmo={e.ritmo} />}
          {e.tipo === "titular" && <><Titular lineas={e.lineas} resalta={e.resalta} lado={e.lado} fondo={e.fondo} est={e.est} lay={e.lay} /><Flash en={2} color="#ff5a1f" /></>}
          {e.tipo === "frase" && <Frase texto={e.texto} v={e.v} />}
          {e.tipo === "terminal" && <Terminal v={e.v} />}
          {e.tipo === "dato" && <Dato valor={e.valor} etiqueta={e.etiqueta} fondo={e.fondo} est={e.est} lay={e.lay} />}
          {e.tipo === "ondas" && <Ondas est={e.est} v={e.v} />}
          {e.tipo === "anillos" && <Anillos est={e.est} v={e.v} />}
          {e.tipo === "numero" && <Numero valor={e.valor} etiqueta={e.etiqueta} est={e.est} />}
          {e.tipo === "mapapuntos" && <MapaPuntos valor={e.valor} etiqueta={e.etiqueta} est={e.est} />}
          {e.tipo === "casa" && <Casa est={e.est} />}
          {e.tipo === "puerta" && <Puerta est={e.est} />}
          {e.tipo === "grilla" && <Grilla n={e.n} etiqueta={e.etiqueta} est={e.est} />}
          {e.tipo === "radar" && <Radar v={e.v} />}
          {e.tipo === "cuadricula" && <Cuadricula v={e.v} />}
          {e.tipo === "barras" && <Barras v={e.v} />}
          {e.tipo === "globo2d" && <Globo2D v={e.v} />}
          {e.tipo === "lluvia" && <Lluvia v={e.v} />}
          {e.tipo === "flujo" && <Flujo v={e.v} />}
          {e.tipo === "foto" && <Foto archivo={e.archivo} luz={e.luz} v={e.v} pos={e.pos} est={e.est} marco={e.marco} />}
          {e.tipo === "imagen" && <Imagen archivo={e.archivo} brillo={e.brillo} />}
          {e.tipo === "roja" && <Roja variante={e.variante} etiqueta={e.etiqueta} v={e.v} est={e.est} />}
          {e.tipo === "comparar" && <Comparar izq={e.izq} der={e.der} centro={e.centro} tema={e.tema} />}
          </AbsoluteFill>
          </Transicion>
        </Series.Sequence>
      ))}
    </Series>
    <Acabado />
    {voz && <Audio src={staticFile(voz)} />}
    {musica && <Audio src={staticFile(musica)} volume={volMusica} loop />}
  </AbsoluteFill>
);
