#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Intro de 10 s de aviso de suscripción (obligatoria en cada doblaje; ver CLAUDE.md).
Narración polaca + dos planos del propio video + título «SUBSKRYBUJ» + botón animado Subskrybuj/Subskrybujesz + música original.
VARIAR en cada video: planos (--a-inicio/--b-inicio), frase (--frase 1|2|3|4|5|6|7) y color del nombre (--color), para que no sea siempre igual.

  python crear_intro.py --video original.mp4 --musica work/no_vocals.wav --voz-piper voices/pl_PL-mc_speech-medium.onnx \
      --a-inicio 230 --b-inicio 390 --frase 2 --salida intro.mp4 [--unir doblado.mp4 --final salida_con_intro.mp4]
"""
import argparse, subprocess, sys, types, importlib.util, tempfile, os
from pathlib import Path
import numpy as np

AQUI = Path(__file__).resolve().parent
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
CANAL = 'Królestwo Przestępcze'          # «Reino Criminal» en polaco
FRASES = {
    1: ("Zanim zaczniemy: jeśli lubisz takie historie z półświatka,",
        f"zasubskrybuj kanał {CANAL} i włącz dzwoneczek, żeby nie przegapić kolejnych odcinków."),
    2: ("Jedna sekunda, zanim ruszymy:",
        f"zasubskrybuj kanał {CANAL} i włącz dzwoneczek, a nie ominie cię żadna z tych historii."),
    3: ("Mała prośba na początek: jeśli ta historia cię wciąga,",
        f"zasubskrybuj kanał {CANAL} i kliknij dzwoneczek, by nie przegapić następnej."),
    4: ("Zanim przejdziemy dalej: jeśli podoba ci się ten kanał,",
        f"zasubskrybuj {CANAL} i włącz dzwoneczek, a każdy nowy odcinek trafi prosto do ciebie."),
    5: ("Nim zaczniemy, mała rzecz: jeśli ten film cię zainteresuje,",
        f"zasubskrybuj kanał {CANAL} i dzwoneczek też włącz, żeby nic cię nie ominęło."),
    6: ("Chwileczkę, zanim zaczniemy: jeśli ten kanał ci się podoba,",
        f"zasubskrybuj {CANAL} i uruchom dzwoneczek, a kolejne historie będą czekać na ciebie."),
    7: ("Zanim ruszymy dalej: jeśli lubisz takie opowieści,",
        f"zasubskrybuj {CANAL} i kliknij dzwoneczek, a nowe odcinki same do ciebie trafią."),
}
COLORES = {'naranja': '0xFFB020', 'rojo': '0xFF4D4D', 'blanco': '0xFFFFFF', 'celeste': '0x5CD6FF', 'verde': '0x7CFF6B', 'amarillo': '0xFFE94D', 'rosa': '0xFF7AD9', 'violeta': '0xB38CFF'}


def sh(cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--video', required=True); p.add_argument('--musica', required=True, help='no_vocals.wav del video (música original)')
    p.add_argument('--voz-piper', required=True); p.add_argument('--doblar', default=str(AQUI.parent / 'doblar.py'))
    p.add_argument('--a-inicio', type=float, required=True, help='segundo del plano dramático (sin texto en pantalla)')
    p.add_argument('--b-inicio', type=float, required=True, help='segundo del 2º plano (sin texto en pantalla, ≥4 s de duración)')
    p.add_argument('--musica-inicio', type=float, help='segundo del archivo de música (por defecto = --a-inicio)')
    p.add_argument('--b-dur', type=float, default=3.95, help='duración natural del 2º plano (el resto se congela con zoom)')
    p.add_argument('--relleno', type=float, default=1.0, help='zoom base (p. ej. 1.18) para tapar las barras negras de fotos/planos con marco')
    p.add_argument('--frase', type=int, default=1, choices=FRASES); p.add_argument('--color', default='naranja', choices=COLORES)
    p.add_argument('--salida', required=True)
    p.add_argument('--unir', help='video doblado final (ya recortado) al que se le antepone la intro'); p.add_argument('--final')
    a = p.parse_args()
    spec = importlib.util.spec_from_file_location('doblar', a.doblar); d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
    tmp = Path(tempfile.mkdtemp(prefix='intro_'))
    cfg = types.SimpleNamespace(motor='piper', modelo_voz=a.voz_piper)
    xs = []
    for k, t in zip(('s1', 's2'), FRASES[a.frase]):
        d.tts_a_wav(t, tmp / f'{k}.wav', cfg, tmp / k); xs.append(d.recortar_silencios(d.leer_wav(tmp / f'{k}.wav')))
    SR = d.SR; t1 = 0.35; t2 = t1 + len(xs[0]) / SR + 0.10
    fin = t2 + len(xs[1]) / SR
    if fin > 9.6: sys.exit(f'La narración dura {fin:.1f} s (máx. 9.6): usar otra frase')
    voz = np.zeros(int(10 * SR), dtype=np.float32)
    voz[int(t1 * SR):int(t1 * SR) + len(xs[0])] += xs[0]; voz[int(t2 * SR):int(t2 * SR) + len(xs[1])] += xs[1]
    d.escribir_wav(tmp / 'voz.wav', voz)
    durA = round(t2, 2); durB = round(10 - durA, 2); bnat = min(a.b_dur, durB - 0.2)
    flt = (f"[0:v]setpts=PTS-STARTPTS,scale=1280:720,fps=30,scale=iw*{a.relleno}:-1,crop=1280:720,setsar=1,format=yuv420p[vA];"
           f"[1:v]setpts=PTS-STARTPTS,scale=1280:720,fps=30,tpad=stop_mode=clone:stop_duration={durB - bnat + 0.2:.2f},trim=duration={durB:.2f},setpts=PTS-STARTPTS,"
           f"zoompan=z='min({a.relleno}+0.0011*on,{a.relleno + 0.2})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1280x720:fps=30,setsar=1,setsar=1,format=yuv420p[vB];"
           f"[vA][vB]concat=n=2:v=1:a=0[vc];"
           f"[2:v]format=rgba,setpts=PTS-STARTPTS+{t2 + 0.8:.2f}/TB[btn];[vc][btn]overlay=440:520:eof_action=pass:format=auto[vo];"
           f"[vo]drawtext=fontfile={FONT}:text='SUBSKRYBUJ':fontsize=104:fontcolor=white:borderw=7:bordercolor=black@0.85:shadowx=3:shadowy=4:x=(w-text_w)/2:y=70:alpha='min(1,max(0,(t-{t2 + 0.07:.2f})/0.45))',"
           f"drawtext=fontfile={FONT}:text='{CANAL}':fontsize=54:fontcolor={COLORES[a.color]}:borderw=5:bordercolor=black@0.85:shadowx=2:shadowy=3:x=(w-text_w)/2:y=195:alpha='min(1,max(0,(t-{t2 + 0.4:.2f})/0.45))',"
           f"fade=t=in:st=0:d=0.4,fade=t=out:st=9.7:d=0.3[v]")
    (tmp / 'filtro_v.txt').write_text(flt, encoding='utf-8')
    sh(['ffmpeg', '-v', 'error', '-y', '-ss', a.a_inicio, '-t', durA, '-i', a.video, '-ss', a.b_inicio, '-t', bnat, '-i', a.video,
        '-framerate', 45, '-start_number', 0, '-i', AQUI / 'btn' / '%05d.png', '-filter_complex_script', tmp / 'filtro_v.txt', '-map', '[v]', '-an',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', 26, '-pix_fmt', 'yuv420p', '-r', 30, tmp / 'v.mp4'])
    fa = ("[0:a]aresample=48000,afade=t=in:st=0:d=0.3,afade=t=out:st=9.2:d=0.8[mus];"
          "[1:a]loudnorm=I=-14.6:TP=-1.5:LRA=11,aresample=48000,pan=stereo|c0=c0|c1=c0[vz];"
          "[mus][vz]amix=inputs=2:duration=first:normalize=0,apad=whole_dur=10,atrim=end=10,alimiter=limit=0.708:level=0[a]")
    (tmp / 'filtro_a.txt').write_text(fa)
    sh(['ffmpeg', '-v', 'error', '-y', '-ss', a.musica_inicio if a.musica_inicio is not None else a.a_inicio, '-t', 10, '-i', a.musica, '-i', tmp / 'voz.wav', '-filter_complex_script', tmp / 'filtro_a.txt',
        '-map', '[a]', '-c:a', 'aac', '-b:a', '192k', '-ar', 48000, '-ac', 2, tmp / 'a.m4a'])
    sh(['ffmpeg', '-v', 'error', '-y', '-i', tmp / 'v.mp4', '-i', tmp / 'a.m4a', '-c', 'copy', '-t', 10, '-metadata:s:a:0', 'language=pol', '-movflags', '+faststart', a.salida])
    print(f'Intro lista: {a.salida} (narración {t1:.1f}–{fin:.1f} s; título desde {t2:.1f} s)')
    if a.unir:
        # la intro se hace a 1280x720; si el video es de otra resolución se reescala (y se fija en 300 fotogramas) para que el concat sin recodificar sea válido
        def sonda(f, e):
            return subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', f'stream={e}', '-of', 'csv=p=0', str(f)], capture_output=True, text=True).stdout.strip()
        w, h = (int(x) for x in sonda(a.unir, 'width,height').split(','))
        intro = Path(a.salida).resolve()
        if (w, h) != (1280, 720) or sonda(intro, 'nb_frames') != '300':
            intro = tmp / 'intro_ajustada.mp4'
            sh(['ffmpeg', '-v', 'error', '-y', '-i', a.salida, '-vf', f'scale={w}:{h}:flags=lanczos,setsar=1,format=yuv420p', '-frames:v', 300, '-c:v', 'libx264', '-preset', 'medium', '-crf', 22,
                '-r', 30, '-c:a', 'copy', '-t', 10, '-movflags', '+faststart', intro])
        lista = tmp / 'lista.txt'; lista.write_text(f"file '{intro}'\nfile '{Path(a.unir).resolve()}'\n")
        sh(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', 0, '-i', lista, '-c', 'copy', '-movflags', '+faststart', '-metadata:s:a:0', 'language=pol', a.final])
        print(f'Video final con intro: {a.final}')


if __name__ == '__main__':
    main()
