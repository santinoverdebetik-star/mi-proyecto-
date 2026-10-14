#!/usr/bin/env python3
"""Doblaje ES -> PL de un video: quita la voz española (Demucs), conserva la música
original, pone voz polaca limpia a velocidad natural y NO toca el video (-c:v copy).

Requisitos (en tu PC):  ffmpeg + ffprobe, y  pip install demucs faster-whisper piper-tts numpy

Flujo:
  1) python doblar.py extraer   video.mp4      -> work/vocals.wav + work/no_vocals.wav (música)
  2) python doblar.py transcribir               -> work/segments.json (texto ES + presupuesto de caracteres)
  3) (traducción: se completa el campo "pl" de cada segmento en work/segments.json)
  3b) python doblar.py afinar                    -> ajusta los inicios a la voz real (stem de Demucs)
  4) python doblar.py sintetizar                -> work/voz_pl.wav + work/timing.json
  5) python doblar.py mezclar   video.mp4 salida_pl.mp4
  6) python doblar.py qa        video.mp4 salida_pl.mp4   -> work/qa_reporte.md (exit 1 si hay FALLOS)
"""
import argparse, asyncio, difflib, json, os, re, shutil, subprocess, sys, wave
from pathlib import Path

import numpy as np

SR = 48000
ISO3 = {'pl': 'pol', 'de': 'deu', 'en': 'eng', 'pt': 'por', 'fr': 'fra', 'it': 'ita'}   # etiqueta del audio según idioma de destino
CPS_PL = 14.0          # caracteres/segundo aprox. de una voz polaca a velocidad natural
HOLGURA = 0.08         # s de aire antes del siguiente segmento
FF = shutil.which('ffmpeg')
FP = shutil.which('ffprobe')
if not FF:
    try:
        import imageio_ffmpeg
        FF = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit('No se encontró ffmpeg. Instalá ffmpeg (con ffprobe).')
if not FP:
    sys.exit('No se encontró ffprobe (viene con ffmpeg).')


# ---------------------------------------------------------------- utilidades
def run(cmd, check=True):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"Error ejecutando: {' '.join(map(str, cmd))}\n{r.stderr[-1500:]}")
    return r


def probe(path):
    r = run([FP, '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', path])
    return json.loads(r.stdout)


def duracion(path):
    return float(probe(path)['format']['duration'])


def workdir(a):
    w = Path(a.dir)
    w.mkdir(parents=True, exist_ok=True)
    return w


def leer_wav(p):
    with wave.open(str(p)) as f:
        assert f.getsampwidth() == 2 and f.getframerate() == SR, f'{p}: se esperaba 16 bit / {SR} Hz'
        ch = f.getnchannels()
        d = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return d.reshape(-1, ch).mean(axis=1) if ch > 1 else d


def escribir_wav(p, x):
    with wave.open(str(p), 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def lufs(p):
    r = run([FF, '-hide_banner', '-i', p, '-map', '0:a:0', '-af', 'ebur128', '-f', 'null', '-'], check=False).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1])


def audio_16k(path):
    """Audio mono a 16 kHz como array float32 (lo decodifica ffmpeg, sin depender de PyAV)."""
    r = subprocess.run([FF, '-v', 'error', '-i', str(path), '-vn', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True)
    if r.returncode != 0:
        sys.exit(f'No se pudo leer el audio de {path}: {r.stderr.decode(errors="ignore")[-500:]}')
    return np.frombuffer(r.stdout, dtype=np.float32)


def db(x):
    return 20 * np.log10(max(float(x), 1e-9))


def cargar_segmentos(w):
    p = w / 'segments.json'
    if not p.exists():
        sys.exit(f'Falta {p}. Corré antes: python doblar.py transcribir')
    return json.loads(p.read_text(encoding='utf-8'))


# ---------------------------------------------------------------- 1) extraer
def cmd_extraer(a):
    w = workdir(a)
    audio = w / 'audio.wav'
    run([FF, '-y', '-v', 'error', '-i', a.video, '-vn', '-ac', '2', '-ar', 44100, '-c:a', 'pcm_s16le', audio])
    run([sys.executable, '-m', 'demucs', '--two-stems=vocals', '-n', 'htdemucs', '-o', w / 'demucs', audio])
    src = w / 'demucs' / 'htdemucs' / 'audio'
    for n in ('vocals', 'no_vocals'):
        run([FF, '-y', '-v', 'error', '-i', src / f'{n}.wav', '-ac', 2, '-ar', SR, '-c:a', 'pcm_s16le', w / f'{n}.wav'])
    print(f'Listo: {w / "vocals.wav"} (voz ES, se descarta) y {w / "no_vocals.wav"} (música conservada)')


# ---------------------------------------------------------------- 2) transcribir
def cmd_transcribir(a):
    from faster_whisper import WhisperModel
    w = workdir(a)
    vd = duracion(a.video) if a.video else duracion(w / 'no_vocals.wav')
    m = WhisperModel(a.modelo, device='auto', compute_type='auto')
    segs, _ = m.transcribe(audio_16k(w / 'vocals.wav'), language=a.idioma, vad_filter=True, beam_size=5)
    out = [{'start': round(s.start, 3), 'end': round(s.end, 3), 'es': s.text.strip()} for s in segs if s.text.strip()]
    for i, s in enumerate(out):
        s['id'] = i + 1
        nxt = out[i + 1]['start'] if i + 1 < len(out) else vd
        s['slot'] = round(nxt - s['start'] - HOLGURA, 3)           # tiempo máximo disponible
        s['max_chars_pl'] = int(s['slot'] * CPS_PL)                  # presupuesto para la traducción
        s['pl'] = ''
    (w / 'segments.json').write_text(json.dumps({'video_dur': vd, 'segments': out}, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{len(out)} segmentos -> {w / "segments.json"}. Falta completar "pl" en cada uno.')


# ---------------------------------------------------------------- 3) afinar tiempos
def cmd_afinar(a):
    """Ajusta el inicio de cada frase al instante real en que empieza la voz española (stem de Demucs)."""
    w = workdir(a)
    orig = w / 'segments.orig.json'
    if orig.exists():
        shutil.copy(orig, w / 'segments.json')                  # repetible: siempre parte de los tiempos originales
    else:
        shutil.copy(w / 'segments.json', orig)
    data = cargar_segmentos(w)
    segs, vd = data['segments'], data['video_dur']
    x = leer_wav(w / 'vocals.wav')
    hop = int(0.02 * SR)
    n = len(x) // hop
    rms = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(axis=1))
    voz = 20 * np.log10(np.maximum(rms, 1e-9)) > -40          # el stem queda en silencio digital en las pausas
    calma = 6                                                   # 0.12 s de silencio antes de un inicio
    ini = np.array([i * 0.02 for i in range(calma, n) if voz[i] and not voz[i - calma:i].any()])
    cambios, prev = [], -10.0
    for s in segs:
        cand = ini[(ini >= s['start'] - a.ventana) & (ini <= s['start'] + a.ventana)]
        nuevo = float(cand[np.argmin(np.abs(cand - s['start']))]) if len(cand) else s['start']
        nuevo = round(max(nuevo, prev + 0.5), 3)
        cambios.append(nuevo - s['start'])
        s['start'], prev = nuevo, nuevo
    for i, s in enumerate(segs):
        nxt = segs[i + 1]['start'] if i + 1 < len(segs) else vd
        s['end'] = round(nxt, 3)
        s['slot'] = round(nxt - s['start'] - HOLGURA, 3)
        s['max_chars_pl'] = int(s['slot'] * CPS_PL)
    (w / 'segments.json').write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    c = np.array(cambios)
    print(f'Inicios ajustados a la voz real: {int((np.abs(c) > 0.01).sum())} de {len(segs)} cambiaron. '
          f'Ajuste mediano {np.median(c):+.2f} s, mayor {c[np.argmax(np.abs(c))]:+.2f} s. Copia original: segments.orig.json')


# ---------------------------------------------------------------- 4) sintetizar
_PIPER = {}


def cargar_piper(ruta):
    if ruta not in _PIPER:
        from piper import PiperVoice
        if not Path(ruta).exists():
            sys.exit(f'Falta la voz de Piper: {ruta}\nBajala de https://huggingface.co/rhasspy/piper-voices (pl/pl_PL/mc_speech/medium)')
        _PIPER[ruta] = PiperVoice.load(ruta)
    return _PIPER[ruta]


def tts_a_wav(texto, destino, a, tmp):
    """Genera `destino` (wav 48 kHz mono 16 bit) con la voz polaca, a velocidad natural."""
    if a.motor == 'piper':     # voz local y gratis: pl_PL-mc_speech-medium (Piper), velocidad natural
        crudo = tmp.with_suffix('.piper.wav')
        with wave.open(str(crudo), 'wb') as f:
            cargar_piper(a.modelo_voz).synthesize_wav(texto, f)
    elif a.motor == 'edge':
        import edge_tts
        crudo = tmp.with_suffix('.mp3')
        proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')   # solo hay proxy en entornos de nube
        asyncio.run(edge_tts.Communicate(texto, a.voz, proxy=proxy).save(str(crudo)))
    elif a.motor == 'cmd':     # voz propia: --tts-cmd 'mi_tts --in {texto} --out {salida}'
        txt = tmp.with_suffix('.txt'); txt.write_text(texto, encoding='utf-8')
        crudo = tmp.with_suffix('.cmd.wav')
        subprocess.run(a.tts_cmd.format(texto=txt, salida=crudo), shell=True, check=True)
    elif a.motor == 'prueba':  # SOLO para probar el pipeline: tono de duración ~ largo del texto
        crudo = tmp.with_suffix('.prueba.wav')
        run([FF, '-y', '-v', 'error', '-f', 'lavfi', '-i', f'sine=f=220:d={max(0.3, len(texto) / CPS_PL):.3f}', crudo])
    else:
        sys.exit(f'Motor desconocido: {a.motor}')
    run([FF, '-y', '-v', 'error', '-i', crudo, '-ac', 1, '-ar', SR, '-c:a', 'pcm_s16le', destino])


def recortar_silencios(x, umbral=0.003, pad=int(0.02 * SR)):
    idx = np.where(np.abs(x) > umbral)[0]
    if len(idx) == 0:
        return x
    return x[max(0, idx[0] - pad): idx[-1] + pad]


MESES_DE = 'Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember'
PREP_N = 'am|vom|zum|im|beim|bis|seit|nach|vor|den|dem|um|auf|zu|von|ab|mit|an|in|gegen'   # tras estas palabras el ordinal lleva -n


def numeros_de(t):
    """Cifras, fechas, horas y porcentajes en alemán, escritos como se dicen (con la declinación correcta)."""
    from num2words import num2words as n
    de = lambda v, **k: n(int(v), lang='de', **k)
    t = re.sub(r'(\d{1,2})[:.](\d{2}) Uhr', lambda m: f'{de(m[1])} Uhr {de(m[2])}', t)
    t = re.sub(rf'vom (\d{{1,2}})\. auf den (\d{{1,2}})\. ({MESES_DE})',
               lambda m: f'vom {de(m[1], to="ordinal")}n auf den {de(m[2], to="ordinal")}n {m[3]}', t)
    def fecha(m):
        prep = m.group(1) or ''
        dia = de(m.group(2), to='ordinal')
        if prep.strip().lower() in PREP_N.split('|'):
            dia += 'n'
        return f'{prep}{dia} {m.group(3)}'
    t = re.sub(rf'(\b(?:{PREP_N})\s+)?(\d{{1,2}})\. ({MESES_DE})\b', fecha, t, flags=re.I)
    t = re.sub(r'\b(1\d{3}|20\d{2})\b', lambda m: de(m[1], to='year'), t)
    t = re.sub(r'(\d+)\s?%', lambda m: f'{de(m[1])} Prozent', t)
    t = re.sub(r'\b\d{1,3}\b', lambda m: de(m[0]), t)
    return t


def pronunciar(texto, reglas):
    """Reescribe nombres y cifras como se dicen (solo para la voz; el texto traducido no cambia)."""
    for patron, reemplazo in reglas:
        texto = re.sub(patron, reemplazo, texto, flags=re.M)
    return texto


def cmd_sintetizar(a):
    w = workdir(a)
    solo = {int(x) for x in a.solo.split(',')} if a.solo else set()
    reglas = json.loads(Path(a.pronunciacion).read_text(encoding='utf-8')) if a.pronunciacion and Path(a.pronunciacion).exists() else []
    print(f'Diccionario de pronunciación: {len(reglas)} reglas' + ('' if reglas else ' (no se encontró el archivo)'))
    data = cargar_segmentos(w)
    vd, segs = data['video_dur'], data['segments']
    faltan = [s['id'] for s in segs if not s['pl'].strip()]
    if faltan:
        sys.exit(f'Segmentos sin traducción ("pl" vacío): {faltan}')
    (w / 'tts').mkdir(exist_ok=True)
    pista = np.zeros(int(round(vd * SR)), dtype=np.float32)
    timing = []
    for s in segs:
        base = w / 'tts' / f'seg_{s["id"]:04d}'
        raw = base.with_suffix('.wav')
        texto_voz = pronunciar(s['pl'], reglas)
        if a.idioma == 'de':
            texto_voz = numeros_de(texto_voz)
        if not (solo and s['id'] not in solo and raw.exists()):     # --solo: reutiliza el audio ya generado de las demás frases
            tts_a_wav(texto_voz, raw, a, base)
        x = recortar_silencios(leer_wav(raw))
        t = len(x) / SR
        d_max = s['slot']
        factor, estado = 1.0, 'OK'
        if t > d_max:
            factor = t / d_max
            if factor <= a.max_acel:
                estado = 'ACELERADO'
            else:
                factor, estado = a.max_acel, 'DEMASIADO_LARGO'
            tmp_in, tmp_out = base.with_suffix('.pre.wav'), base.with_suffix('.fit.wav')
            escribir_wav(tmp_in, x)
            run([FF, '-y', '-v', 'error', '-i', tmp_in, '-filter:a', f'atempo={factor:.4f}', '-ar', SR, '-ac', 1, '-c:a', 'pcm_s16le', tmp_out])
            x = leer_wav(tmp_out)
        i0 = int(round(s['start'] * SR))
        fin = min(len(pista), i0 + len(x))
        pista[i0:fin] += x[:fin - i0]
        timing.append({'id': s['id'], 'start': s['start'], 'slot': d_max, 'dur_tts': round(t, 3),
                       'factor': round(factor, 4), 'dur_final': round(len(x) / SR, 3), 'estado': estado})
    escribir_wav(w / 'voz_pl.wav', pista)
    (w / 'timing.json').write_text(json.dumps(timing, indent=1), encoding='utf-8')
    malos = [t['id'] for t in timing if t['estado'] == 'DEMASIADO_LARGO']
    print(f'Voz polaca: {w / "voz_pl.wav"}. Segmentos aun muy largos (acortar la traducción): {malos or "ninguno"}')


# ---------------------------------------------------------------- 5) mezclar
def cmd_mezclar(a):
    w = workdir(a)
    vd = duracion(a.video)
    ref = w / 'vocals.wav'                       # la voz polaca se iguala a la sonoridad de la voz española original
    objetivo = min(-12.0, max(-30.0, lufs(ref))) if ref.exists() else -16.0
    print(f'Sonoridad objetivo de la voz polaca: {objetivo:.1f} LUFS')
    filtro = (f'[1:a]loudnorm=I={objetivo:.1f}:TP=-1.5:LRA=11,aresample={SR},pan=stereo|c0=c0|c1=c0[v];'
              f'[0:a][v]amix=inputs=2:duration=first:normalize=0,'
              f'apad=whole_dur={vd:.3f},atrim=end={vd:.3f},alimiter=limit=0.708:level=0[m]')
    run([FF, '-y', '-v', 'error', '-i', w / 'no_vocals.wav', '-i', w / 'voz_pl.wav', '-i', a.video,
         '-filter_complex', filtro, '-map', '2:v:0', '-map', '[m]', '-c:v', 'copy',
         '-c:a', 'aac', '-b:a', '256k', '-ar', SR, '-metadata:s:a:0', f'language={ISO3.get(a.idioma, a.idioma)}',
         '-movflags', '+faststart', a.salida])
    print(f'Listo: {a.salida} (video sin recomprimir, música original + voz polaca)')


# ---------------------------------------------------------------- 5b) compactar: quitar las pausas sobrantes (corta video, música y voz a la vez)
def _curva(n, x, inicio=0.0, fin=1.0):
    return np.linspace(inicio, fin, n, dtype=np.float32).reshape((-1,) + (1,) * (x.ndim - 1))


def trocear_audio(x, cortes, fps, cruce=0, borde=0.004):
    """Concatena los tramos [f0, f1) (en fotogramas) de `x`. `cruce` > 0: fundido cruzado de equal-power entre tramos."""
    partes, prev_fin = [], None
    nb = int(borde * SR)
    for j, (f0, f1) in enumerate(cortes):
        a0, a1 = int(round(f0 / fps * SR)), int(round(f1 / fps * SR))
        seg = x[a0:a1].copy()
        if j > 0 and prev_fin is not None and a0 != prev_fin:        # tramo no contiguo en el original
            if cruce > 0:
                n = min(cruce, len(seg), len(x) - prev_fin)
                if n > 0:
                    t = _curva(n, x)
                    seg[:n] = seg[:n] * np.sqrt(t) + x[prev_fin:prev_fin + n] * np.sqrt(1 - t)
            elif nb > 0 and len(seg) > 2 * nb:                        # solo evitar chasquidos
                seg[:nb] *= _curva(nb, x, 0, 1)
        if cruce == 0 and nb > 0 and len(seg) > 2 * nb:
            seg[-nb:] *= _curva(nb, x, 1, 0)
        partes.append(seg)
        prev_fin = a1
    return np.concatenate(partes) if partes else x[:0]


def cmd_recortar_pausas(a):
    """Receta estándar (paso final de cada doblaje): detecta los silencios sobre la VOZ LIMPIA, no sobre el mix con música;
    acorta las pausas >= umbral dejando `respiro` s; no toca las pausas cortas; corta video y audio del video final juntos."""
    import math
    w = workdir(a)
    voz = leer_wav(Path(a.voz) if a.voz else w / 'voz_pl.wav')
    vs = [s for s in probe(a.video)['streams'] if s['codec_type'] == 'video'][0]
    num, den = vs['r_frame_rate'].split('/')
    fps = int(num) / int(den)
    dur = duracion(a.video)
    total = int(round(dur * fps))
    if str(vs.get('nb_frames', '')).isdigit():
        total = min(total, int(vs['nb_frames']))                  # la duración redondeada puede pasarse de los fotogramas reales
    if a.hasta:
        total = min(total, int(a.hasta * fps))
    # --- silencios de la voz limpia (ventanas de 10 ms)
    hop = int(0.01 * SR)
    n = len(voz) // hop
    rms = np.sqrt((voz[:n * hop].reshape(n, hop) ** 2).mean(axis=1))
    habla = 20 * np.log10(np.maximum(rms, 1e-9)) > a.silencio_db
    idx = np.where(habla)[0]
    if len(idx) == 0:
        sys.exit('No se detectó voz en el archivo de voz limpia.')
    primero, ultimo = idx[0], idx[-1]
    quitar, i = [], primero
    while i <= ultimo:
        if habla[i]:
            i += 1
            continue
        j = i
        while j <= ultimo and not habla[j]:
            j += 1
        t0, t1 = i * 0.01, j * 0.01                          # pausa entre dos tramos de voz (no se tocan el inicio ni el final del video)
        if t1 - t0 >= a.umbral:
            h = a.respiro / 2
            r0, r1 = int(math.ceil((t0 + h) * fps)), int(math.floor((t1 - h) * fps))
            if r1 > r0 and r0 < total:
                quitar.append((r0, min(r1, total)))
        i = j
    # --- tramos que se conservan
    cortes, pos = [], 0
    for r0, r1 in quitar:
        if r0 > pos:
            cortes.append((pos, r0))
        pos = r1
    if pos < total:
        cortes.append((pos, total))
    total_out = sum(f1 - f0 for f0, f1 in cortes)
    dur_out = total_out / fps
    quitado = (total - total_out) / fps
    print(f'{len(quitar)} pausas >= {a.umbral:.1f} s acortadas a {a.respiro:.1f} s. Se quitan {quitado/60:.1f} min: {total/fps/60:.1f} -> {dur_out/60:.1f} min')
    # --- mapa de frases -> video nuevo (para el control de calidad)
    ids, nuevos = [], []
    segf = w / 'segments.json'
    if segf.exists():
        offs, acum = [], 0
        for f0, f1 in cortes:
            offs.append(acum); acum += f1 - f0
        for sg in json.loads(segf.read_text(encoding='utf-8'))['segments']:
            f = int(round(sg['start'] * fps))
            for (c0, c1), off in zip(cortes, offs):
                if c0 <= f < c1:
                    ids.append(sg['id']); nuevos.append(round((off + f - c0) / fps, 3)); break
    (w / 'cortes.json').write_text(json.dumps({'fps': fps, 'cortes': cortes, 'total_frames': total_out, 'dur': dur_out, 'ids': ids,
                                               'nuevo_inicio': nuevos, 'umbral': a.umbral, 'respiro': a.respiro}, indent=1), encoding='utf-8')
    # --- audio: el del video final ya montado, cortado con los mismos fotogramas
    run([FF, '-y', '-v', 'error', '-i', a.video, '-vn', '-ac', '2', '-ar', SR, '-c:a', 'pcm_s16le', w / 'mix_final.wav'])
    escribir_wav_estereo(w / 'mix_c.wav', trocear_audio(leer_wav_estereo(w / 'mix_final.wav'), cortes, fps, cruce=int(0.12 * SR)))
    escribir_wav(w / 'voz_c.wav', trocear_audio(voz, cortes, fps, cruce=0))
    if (w / 'no_vocals.wav').exists():
        escribir_wav_estereo(w / 'musica_c.wav', trocear_audio(leer_wav_estereo(w / 'no_vocals.wav'), cortes, fps, cruce=int(0.12 * SR)))
    expr = '+'.join(f'between(n,{f0},{f1 - 1})' for f0, f1 in cortes)
    (w / 'filtro.txt').write_text(f"[0:v]select='{expr}',setpts=N/({fps:.6f}*TB)[v];"
                                  f'[1:a]apad=whole_dur={dur_out:.3f},atrim=end={dur_out:.3f},alimiter=limit=0.708:level=0[m]', encoding='utf-8')
    run([FF, '-y', '-v', 'error', '-i', a.video, '-i', w / 'mix_c.wav', '-filter_complex_script', w / 'filtro.txt',
         '-map', '[v]', '-map', '[m]', '-c:v', 'libx264', '-preset', a.preset, '-crf', a.crf, '-pix_fmt', 'yuv420p', '-r', f'{fps:.6f}',
         '-c:a', 'aac', '-b:a', f'{a.audio_kbps}k', '-ar', SR, '-metadata:s:a:0', f'language={ISO3.get(a.idioma, a.idioma)}',
         '-movflags', '+faststart', a.salida])
    print(f'Listo: {a.salida}')


def leer_wav_estereo(p):
    with wave.open(str(p)) as f:
        assert f.getsampwidth() == 2 and f.getframerate() == SR, f'{p}: se esperaba 16 bit / {SR} Hz'
        ch = f.getnchannels()
        d = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return d.reshape(-1, ch)


def escribir_wav_estereo(p, x):
    with wave.open(str(p), 'wb') as f:
        f.setnchannels(x.shape[1]); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


# ---------------------------------------------------------------- 6) QA
class QA:
    def __init__(self):
        self.filas = []

    def add(self, nombre, estado, detalle=''):
        self.filas.append((nombre, estado, detalle))
        print(f'[{estado:8}] {nombre}: {detalle}')


def md5_video(p):
    return run([FF, '-v', 'error', '-i', p, '-map', '0:v:0', '-c', 'copy', '-f', 'md5', '-']).stdout.strip()


def paquetes_video(p):
    r = run([FP, '-v', 'error', '-count_packets', '-select_streams', 'v:0', '-show_entries',
             'stream=nb_read_packets,codec_name,width,height,r_frame_rate', '-of', 'json', p])
    return json.loads(r.stdout)['streams'][0]


def qa_traduccion(q, segs, glosario, idioma='pl'):
    vacios = [s['id'] for s in segs if not s['pl'].strip()]
    q.add('Traducción: todos los segmentos traducidos', 'FALLO' if vacios else 'OK', f'vacíos: {vacios}' if vacios else f'{len(segs)} segmentos')
    # los nombres propios (con mayúscula) y los términos que el original ya trae (p. ej. «alucín») pueden llevar tildes o ñ
    ajenos = r'[ñáéíú]' if idioma == 'de' else r'[ñáéíúü]'     # en alemán la ü es propia
    def con_tilde_ajena(sg):
        base = {w.lower() for w in re.findall(r'\w+', sg['es']) if len(w) >= 4}
        malas = [w for w in sg['pl'].split() if not w[:1].isupper() and w[:1] not in '„"' and re.search(ajenos, w)
                 and not any(w.lower().strip('.,;:!?„”"').startswith(b) for b in base)]
        return bool(re.search(r'[¿¡]', sg['pl'])) or bool(malas)
    es_chars = [s['id'] for s in segs if con_tilde_ajena(s)]
    q.add('Traducción: sin caracteres exclusivos del español', 'FALLO' if es_chars else 'OK', f'segmentos: {es_chars}' if es_chars else '')
    def numeros(t):       # «577 mil» y «577.000» son la misma cifra
        t = re.sub(r'(\d+)\s*mil\b', lambda m: str(int(m.group(1)) * 1000), t)
        t = re.sub(r'(\d{1,3})\.(\d{3})\b', r'\1\2', t)
        return set(re.findall(r'\d+', t))
    inventadas, revisar = [], []
    for s in segs:
        n_es, n_pl = numeros(s['es']), numeros(s['pl'])
        if not n_pl <= n_es:
            inventadas.append(s['id'])            # cifra en el polaco que no está en el original
        elif not n_es <= n_pl:
            revisar.append(s['id'])               # cifra escrita con letras: revisar a mano
    q.add('Traducción: ninguna cifra inventada o alterada', 'FALLO' if inventadas else 'OK', f'segmentos: {inventadas}' if inventadas else '')
    q.add('Traducción: cifras escritas con letras (revisar a mano)', 'AVISO' if revisar else 'OK', f'segmentos: {revisar}' if revisar else '')
    ratio = [s['id'] for s in segs if s['pl'].strip() and not 0.6 <= len(s['pl']) / max(1, len(s['es'])) <= 2.0]
    q.add('Traducción: longitud razonable respecto al original', 'AVISO' if ratio else 'OK', f'revisar manualmente: {ratio}' if ratio else '')
    gl = []
    for s in segs:
        for es, pl in glosario.items():
            if es.lower() in s['es'].lower() and pl.lower() not in s['pl'].lower():
                gl.append((s['id'], es, pl))
    q.add('Traducción: términos del glosario', 'FALLO' if gl else ('OK' if glosario else 'OMITIDO'),
          str(gl) if gl else ('' if glosario else 'sin glosario'))


def qa_video_compacto(q, a, w, cj):
    """Comprobaciones del video recortado: contenido fiel al original, cortes solo en silencios, voz en su sitio."""
    fps, cortes = cj['fps'], cj['cortes']
    vi, vo = paquetes_video(a.video), None
    info = [s for s in probe(a.salida)['streams'] if s['codec_type'] == 'video'][0]
    orig = [s for s in probe(a.video)['streams'] if s['codec_type'] == 'video'][0]
    r = run([FP, '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', a.salida])
    n_out = int(r.stdout.strip().split(',')[0])
    q.add('Video: mismo tamaño y fps que el original, códec h264',
          'OK' if (info['width'], info['height'], info['r_frame_rate'], info['codec_name']) == (orig['width'], orig['height'], orig['r_frame_rate'], 'h264') else 'FALLO',
          f"{info['codec_name']} {info['width']}x{info['height']} {info['r_frame_rate']}")
    q.add('Video: fotogramas = suma de los tramos conservados (sin duplicar ni perder ninguno)', 'OK' if n_out == cj['total_frames'] else 'FALLO', f"salida={n_out} esperado={cj['total_frames']}")
    do, da = duracion(a.salida), float([s for s in probe(a.salida)['streams'] if s['codec_type'] == 'audio'][0]['duration'])
    q.add('Duración del video = duración esperada (±0.10 s)', 'OK' if abs(do - cj['dur']) <= 0.10 else 'FALLO', f"salida={do:.2f}s esperado={cj['dur']:.2f}s (original {duracion(a.video):.1f}s)")
    q.add('Audio y video con la misma duración (±0.10 s)', 'OK' if abs(do - da) <= 0.10 else 'FALLO', f'video={do:.2f}s audio={da:.2f}s')
    # fidelidad visual: se comparan fotogramas de la salida con el fotograma de origen que les corresponde
    offs, acum = [], 0
    for f0, f1 in cortes:
        offs.append(acum); acum += f1 - f0
    import random
    rnd = random.Random(7)
    tope = n_out - 3                           # al pie exacto del archivo ffmpeg no devuelve imagen: se evitan los últimos fotogramas
    muestras = {int(i * tope / 15) for i in range(16)} | {rnd.randrange(tope) for _ in range(12)}
    paso = max(1, len(cortes) // 40)           # primer y último fotograma de cada tramo: ahí se nota cualquier desfase
    for (f0, f1), off in list(zip(cortes, offs))[::paso]:
        for k in (off, off + (f1 - f0) - 1):
            if 0 <= k < tope:
                muestras.add(k)
    muestras = sorted(muestras)
    carp = w / 'qa_frames'; carp.mkdir(exist_ok=True)
    valores, faltan = [], []
    for k in muestras:
        for (f0, f1), off in zip(cortes, offs):
            if off <= k < off + (f1 - f0):
                src = f0 + (k - off); break
        for nombre, arch, fr in (('o', a.salida, k), ('s', a.video, src)):
            png = carp / f'{nombre}.png'
            png.unlink(missing_ok=True)                                   # nunca comparar contra una imagen vieja
            # ffmpeg devuelve el primer fotograma con pts >= -ss: se pide justo antes del pts exacto
            run([FF, '-y', '-v', 'error', '-ss', f'{max(0.0, (fr - 0.25) / fps):.4f}', '-i', arch, '-frames:v', '1', png])
        if not (carp / 'o.png').exists() or not (carp / 's.png').exists():
            faltan.append((k, src)); continue
        rr = run([FF, '-hide_banner', '-i', carp / 'o.png', '-i', carp / 's.png', '-lavfi', 'ssim', '-f', 'null', '-'], check=False).stderr
        valores.append((float(re.findall(r'All:([\d.]+)', rr)[-1]), k, src))
    shutil.rmtree(carp, ignore_errors=True)
    v = np.array([x[0] for x in valores]) if valores else np.array([0.0])
    desfasados = [(k, src, round(x, 3)) for x, k, src in valores if x < 0.85]     # ~0.45 = otro fotograma; 0.9-0.98 = solo compresión
    ok_v = not desfasados and not faltan and v.mean() >= 0.95
    q.add(f'Video: {len(valores)} fotogramas (bordes de cada corte + azar) coinciden con su fotograma de origen', 'OK' if ok_v else 'FALLO',
          f'SSIM medio {v.mean():.3f}, mínimo {v.min():.3f}; sin desfase de fotogramas' if ok_v else f'desfasados: {desfasados[:6]} sin imagen: {faltan[:4]} medio {v.mean():.3f}')
    # los cortes caen en silencio y la voz está en su sitio
    voz = leer_wav(w / 'voz_c.wav')
    ids, nu = cj['ids'], cj['nuevo_inicio']
    tim = {t['id']: t for t in json.loads((w / 'timing.json').read_text())}
    en_frase = []
    for (f0, f1), off in list(zip(cortes, offs))[:-1]:
        t_fin = (off + f1 - f0) / fps
        seg = voz[max(0, int((t_fin - 0.08) * SR)):int(t_fin * SR)]
        if len(seg) and db(np.sqrt(np.mean(seg ** 2))) > -50:
            en_frase.append(round(t_fin, 2))
    q.add('Cortes: ninguno cae dentro de una frase (silencio de voz en los 80 ms previos)', 'FALLO' if en_frase else 'OK', f'cortes con voz en: {en_frase[:10]}' if en_frase else f'{len(cortes) - 1} cortes, todos en pausa')
    mudos = []
    for i, t0 in zip(ids, nu):
        seg = voz[int(t0 * SR):int((t0 + tim[i]['dur_final']) * SR)]
        if len(seg) == 0 or db(np.sqrt(np.mean(seg ** 2))) < -50:
            mudos.append(i)
    q.add('Sincronía: cada frase suena en su sitio dentro del video nuevo', 'FALLO' if mudos else 'OK', f'sin voz: {mudos}' if mudos else f'{len(ids)} frases')
    gaps = [nu[i + 1] - nu[i] - tim[ids[i]]['dur_final'] for i in range(len(ids) - 1)]
    if gaps:
        g = np.array(gaps)
        q.add('Ritmo: pausas entre frases (media / mediana / máxima)', 'OK' if g.max() <= 3.0 else 'AVISO',
              f'{g.mean():.2f}s / {np.median(g):.2f}s / {g.max():.2f}s; {int((g > 1.5).sum())} pausas > 1.5 s, {int((g < 0.1).sum())} < 0.1 s')


def cmd_qa(a):
    w = workdir(a)
    data = cargar_segmentos(w)
    segs = data['segments']
    q = QA()
    voz_wav, mus_wav = (w / 'voz_c.wav', w / 'musica_c.wav') if a.compacto else (w / 'voz_pl.wav', w / 'no_vocals.wav')
    if a.compacto:
        qa_video_compacto(q, a, w, json.loads((w / 'cortes.json').read_text()))
    else:
        # --- video intacto
        vi, vo = paquetes_video(a.video), paquetes_video(a.salida)
        q.add('Video: mismo códec/resolución/fps/paquetes', 'OK' if vi == vo else 'FALLO', f'in={vi} out={vo}' if vi != vo else f'{vo["codec_name"]} {vo["width"]}x{vo["height"]} {vo["r_frame_rate"]} {vo["nb_read_packets"]} paquetes')
        mi, mo = md5_video(a.video), md5_video(a.salida)
        q.add('Video: contenido idéntico (md5 del stream, sin recomprimir ni ralentizar)', 'OK' if mi == mo else 'FALLO', mo)
        # --- duración
        di, do = duracion(a.video), duracion(a.salida)
        q.add('Duración igual a la original (±0.10 s)', 'OK' if abs(di - do) <= 0.10 else 'FALLO', f'in={di:.3f}s out={do:.3f}s')
    # --- audio
    au = [s for s in probe(a.salida)['streams'] if s['codec_type'] == 'audio']
    ok = len(au) == 1 and au[0]['codec_name'] == 'aac' and int(au[0]['sample_rate']) == SR
    q.add('Audio: 1 pista AAC a 48 kHz', 'OK' if ok else 'FALLO', f'{[(s["codec_name"], s["sample_rate"], s["channels"]) for s in au]}')
    lang = au[0].get('tags', {}).get('language') if au else None
    q.add(f'Audio: etiqueta de idioma = {ISO3.get(a.idioma, a.idioma)}', 'OK' if lang == ISO3.get(a.idioma, a.idioma) else 'AVISO', str(lang))
    r = run([FF, '-hide_banner', '-i', a.salida, '-map', '0:a:0', '-af', 'volumedetect,ebur128=peak=true', '-f', 'null', '-'], check=False).stderr
    mx = float(re.findall(r'max_volume:\s*(-?[\d.]+) dB', r)[-1])
    q.add('Audio: sin clipping (pico ≤ -0.9 dB)', 'OK' if mx <= -0.9 else 'FALLO', f'max_volume={mx} dB')
    l_out, l_in = lufs(a.salida), lufs(a.video)
    q.add('Audio: sonoridad similar al video original (±3 LU)', 'OK' if abs(l_out - l_in) <= 3 else 'FALLO', f'original={l_in} LUFS, doblado={l_out} LUFS')
    # --- tiempos de la voz
    tim = json.loads((w / 'timing.json').read_text())
    largos = [t['id'] for t in tim if t['estado'] == 'DEMASIADO_LARGO']
    q.add('Tiempos: ningún segmento excede su hueco ni se acelera más del límite', 'FALLO' if largos else 'OK',
          f'acortar traducción de: {largos}' if largos else f'{sum(t["estado"] == "ACELERADO" for t in tim)} acelerados (≤ límite), {sum(t["estado"] == "OK" for t in tim)} a velocidad natural')
    mf = max((t['factor'] for t in tim), default=1.0)
    q.add('Tiempos: aceleración máxima aplicada', 'OK' if mf <= 1.15 else 'FALLO', f'x{mf}')
    voz = leer_wav(voz_wav)
    mudos = []
    for t in ([] if a.compacto else tim):
        i0 = int(t['start'] * SR); seg = voz[i0:i0 + int(t['dur_final'] * SR)]
        if len(seg) == 0 or db(np.sqrt(np.mean(seg ** 2))) < -50:
            mudos.append(t['id'])
    q.add('Cobertura: todos los segmentos tienen voz audible', 'FALLO' if mudos else 'OK', f'sin voz: {mudos}' if mudos else '')
    # --- traducción
    glp = Path(a.glosario) if a.glosario else None
    qa_traduccion(q, segs, json.loads(glp.read_text(encoding='utf-8')) if glp and glp.exists() else {}, a.idioma)
    # --- pruebas con reconocimiento de voz (si está faster-whisper)
    try:
        from faster_whisper import WhisperModel
        m = WhisperModel(a.modelo, device='auto', compute_type='auto')
        sg, _ = m.transcribe(audio_16k(mus_wav), language='es', vad_filter=True)
        palabras = sum(len(s.text.split()) for s in sg if s.no_speech_prob < 0.4)
        q.add('Voz española eliminada (reconocimiento sobre la música)', 'OK' if palabras <= 8 else 'FALLO', f'{palabras} palabras detectadas')
        sg, info = m.transcribe(audio_16k(voz_wav), language=a.idioma, vad_filter=True)
        def palabras(t):      # solo palabras comunes: los nombres propios (mayúscula) se verifican escuchando
            return [x.lower() for x in re.findall(r'\w+', t) if not x[:1].isupper() and not x.isdigit()]
        oido = ' '.join(s.text for s in sg)
        esperado = ' '.join(s['pl'] for s in segs)
        sim = difflib.SequenceMatcher(None, palabras(oido), palabras(esperado), autojunk=False).ratio()
        q.add('La voz doblada dice lo traducido (similitud ≥ 0.80)', 'OK' if sim >= 0.80 else 'FALLO', f'{sim:.2f}')
    except ImportError:
        q.add('Voz española eliminada / voz polaca verificada por reconocimiento', 'OMITIDO', 'instalá faster-whisper para estas dos pruebas')
    # --- informe
    fallos = [f for f in q.filas if f[1] == 'FALLO']
    md = ['# Informe QA doblaje ES→PL', '', '| Prueba | Estado | Detalle |', '|---|---|---|']
    md += [f'| {n} | {e} | {d} |' for n, e, d in q.filas]
    md += ['', f'**Resultado: {"APROBADO" if not fallos else f"{len(fallos)} FALLO(S)"}**']
    (w / 'qa_reporte.md').write_text('\n'.join(md), encoding='utf-8')
    print(f'\nResultado: {"APROBADO" if not fallos else str(len(fallos)) + " FALLO(S)"}  ->  {w / "qa_reporte.md"}')
    sys.exit(1 if fallos else 0)


# ---------------------------------------------------------------- CLI
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--dir', default='work', help='carpeta de trabajo (default: work)')
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('extraer'); s.add_argument('video'); s.set_defaults(f=cmd_extraer)
    s = sub.add_parser('transcribir'); s.add_argument('--video'); s.add_argument('--idioma', default='es', help='idioma hablado en el video (default es)'); s.add_argument('--modelo', default='large-v3'); s.set_defaults(f=cmd_transcribir)
    s = sub.add_parser('afinar'); s.add_argument('--ventana', type=float, default=0.4, help='segundos a cada lado donde buscar el inicio real'); s.set_defaults(f=cmd_afinar)
    s = sub.add_parser('sintetizar')
    s.add_argument('--motor', default='piper', choices=['piper', 'edge', 'cmd', 'prueba'])
    s.add_argument('--modelo-voz', default='voices/pl_PL-mc_speech-medium.onnx', help='motor piper: archivo .onnx de la voz (default: mc_speech)')
    s.add_argument('--voz', default='pl-PL-MarekNeural', help='motor edge: voz de edge-tts (pl-PL-MarekNeural / pl-PL-ZofiaNeural)')
    s.add_argument('--tts-cmd', help="motor cmd: plantilla con {texto} y {salida}")
    s.add_argument('--idioma', default='pl', help='idioma de destino (pl, de); de convierte cifras y fechas a palabras')
    s.add_argument('--solo', help='ids a regenerar, separados por coma (ej. 101,160); el resto reutiliza su audio')
    s.add_argument('--pronunciacion', default='pronunciacion.json', help='json [[patrón, reemplazo], ...] para pronunciar nombres y cifras')
    s.add_argument('--max-acel', type=float, default=1.12, help='aceleración máxima permitida (default 1.12)')
    s.set_defaults(f=cmd_sintetizar)
    s = sub.add_parser('mezclar'); s.add_argument('video'); s.add_argument('salida'); s.add_argument('--idioma', default='pl', help='idioma de destino (pl, de, ...)'); s.set_defaults(f=cmd_mezclar)
    s = sub.add_parser('recortar-pausas', help='paso final: acorta las pausas largas del video ya montado')
    s.add_argument('video', help='video final ya montado (con la voz doblada y la música)'); s.add_argument('salida')
    s.add_argument('--voz', help='voz limpia sin música (default work/voz_pl.wav)'); s.add_argument('--idioma', default='pl')
    s.add_argument('--umbral', type=float, default=0.7, help='pausas de este largo o más se acortan (s)')
    s.add_argument('--respiro', type=float, default=0.4, help='pausa que se deja (s)')
    s.add_argument('--silencio-db', type=float, default=-45, help='nivel por debajo del cual la voz se considera en silencio')
    s.add_argument('--crf', default='24'); s.add_argument('--preset', default='medium'); s.add_argument('--audio-kbps', default='192')
    s.add_argument('--hasta', type=float, help='solo los primeros N segundos (prueba)'); s.set_defaults(f=cmd_recortar_pausas)
    s = sub.add_parser('qa'); s.add_argument('video'); s.add_argument('salida'); s.add_argument('--compacto', action='store_true', help='el video fue recortado con «compactar»'); s.add_argument('--idioma', default='pl', help='idioma de destino (pl, de, ...)')
    s.add_argument('--glosario', help='json {"término ES": "término PL"}'); s.add_argument('--modelo', default='large-v3'); s.set_defaults(f=cmd_qa)
    a = p.parse_args()
    a.f(a)


if __name__ == '__main__':
    main()
