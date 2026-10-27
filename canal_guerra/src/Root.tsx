import React from 'react';
import {Composition, AbsoluteFill} from 'remotion';
const Test: React.FC = () => <AbsoluteFill style={{background:'#14110d',color:'#e8dcc0',fontFamily:'serif',fontSize:90,justifyContent:'center',alignItems:'center'}}>Prueba Remotion</AbsoluteFill>;
export const Root: React.FC = () => <Composition id="Test" component={Test} durationInFrames={30} fps={30} width={1920} height={1080} />;
