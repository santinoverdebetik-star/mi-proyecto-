import React from "react";
import { Composition } from "remotion";
import { Historia, duracionTotal } from "./Historia";
import { ALTO, ANCHO, FPS } from "./estilo";
import { DEMO } from "./guion";

export const Root: React.FC = () => (
  <Composition id="Historia" component={Historia} width={ANCHO} height={ALTO} fps={FPS}
    durationInFrames={duracionTotal(DEMO)} defaultProps={{ escenas: DEMO }}
    calculateMetadata={({ props }) => ({ durationInFrames: duracionTotal(props.escenas) })} />
);
