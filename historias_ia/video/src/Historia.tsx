import React from "react";
import { AbsoluteFill, Audio, Series, staticFile } from "remotion";
import { Acabado, Fuentes } from "./Capas";
import { FPS } from "./estilo";
import { Titular } from "./escenas/Titular";
import { Diagrama } from "./escenas/Diagrama";
import { Escena3D } from "./escenas/Escena3D";
import { Imagen } from "./escenas/Imagen";
import type { Escena } from "./guion";

export const duracionTotal = (e: Escena[]) => Math.round(e.reduce((s, x) => s + x.dur, 0) * FPS);

export const Historia: React.FC<{ escenas: Escena[]; voz?: string; musica?: string; volMusica?: number }> = ({ escenas, voz, musica, volMusica = 0.12 }) => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Fuentes />
    <Series>
      {escenas.map((e, i) => (
        <Series.Sequence key={i} durationInFrames={Math.round(e.dur * FPS)}>
          {e.tipo === "3d" && <Escena3D objeto={e.objeto} infeccion={e.infeccion} />}
          {e.tipo === "diagrama" && <Diagrama nodos={e.nodos} enlaces={e.enlaces} infecta={e.infecta} titulo={e.titulo} />}
          {e.tipo === "titular" && <Titular lineas={e.lineas} resalta={e.resalta} lado={e.lado} />}
          {e.tipo === "imagen" && <Imagen archivo={e.archivo} brillo={e.brillo} />}
        </Series.Sequence>
      ))}
    </Series>
    <Acabado />
    {voz && <Audio src={staticFile(voz)} />}
    {musica && <Audio src={staticFile(musica)} volume={volMusica} loop />}
  </AbsoluteFill>
);
