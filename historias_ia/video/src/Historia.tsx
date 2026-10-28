import React from "react";
import { AbsoluteFill, Audio, Series, staticFile } from "remotion";
import { Acabado, Fuentes, Flash } from "./Capas";
import { FPS } from "./estilo";
import { Titular } from "./escenas/Titular";
import { Diagrama } from "./escenas/Diagrama";
import { Escena3D } from "./escenas/Escena3D";
import { Imagen } from "./escenas/Imagen";
import { Foto } from "./escenas/Foto";
import { Dato, Flujo, Frase, Terminal } from "./escenas/Inserto";
import type { Escena } from "./guion";

export const duracionTotal = (e: Escena[]) => Math.round(e.reduce((s, x) => s + x.dur, 0) * FPS);

export const Historia: React.FC<{ escenas: Escena[]; voz?: string; musica?: string; volMusica?: number }> = ({ escenas, voz, musica, volMusica = 0.12 }) => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Fuentes />
    <Series>
      {escenas.map((e, i) => (
        <Series.Sequence key={i} durationInFrames={Math.round(e.dur * FPS)}>
          {e.tipo === "3d" && <Escena3D objeto={e.objeto} infeccion={e.infeccion} luz={e.luz} inv={e.inv} fondo={e.fondo} fondoPos={e.fondoPos} />}
          {e.tipo === "diagrama" && <Diagrama nodos={e.nodos} enlaces={e.enlaces} infecta={e.infecta} titulo={e.titulo} escala={e.escala} ritmo={e.ritmo} />}
          {e.tipo === "titular" && <><Titular lineas={e.lineas} resalta={e.resalta} lado={e.lado} fondo={e.fondo} /><Flash en={2} color="#ff5a1f" /></>}
          {e.tipo === "frase" && <Frase texto={e.texto} v={e.v} />}
          {e.tipo === "terminal" && <Terminal v={e.v} />}
          {e.tipo === "dato" && <Dato valor={e.valor} etiqueta={e.etiqueta} />}
          {e.tipo === "flujo" && <Flujo v={e.v} />}
          {e.tipo === "foto" && <Foto archivo={e.archivo} luz={e.luz} v={e.v} pos={e.pos} />}
          {e.tipo === "imagen" && <Imagen archivo={e.archivo} brillo={e.brillo} />}
        </Series.Sequence>
      ))}
    </Series>
    <Acabado />
    {voz && <Audio src={staticFile(voz)} />}
    {musica && <Audio src={staticFile(musica)} volume={volMusica} loop />}
  </AbsoluteFill>
);
