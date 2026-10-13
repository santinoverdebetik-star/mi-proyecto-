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
    segs, _ = m.transcribe(audio_16k(w / 'vocals.wav'), language='es', vad_filter=True, beam_size=5)
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


def pronunciar(texto, reglas):
    """Reescribe nombres y cifras como se dicen (solo para la voz; el texto traducido no cambia)."""
    for patron, reemplazo in reglas:
        texto = re.sub(patron, reemplazo, texto, flags=re.M)
    return texto


def cmd_sintetizar(a):
    w = workdir(a)
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
        tts_a_wav(pronunciar(s['pl'], reglas), raw, a, base)
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
         '-c:a', 'aac', '-b:a', '256k', '-ar', SR, '-metadata:s:a:0', 'language=pol',
         '-movflags', '+faststart', a.salida])
    print(f'Listo: {a.salida} (video sin recomprimir, música original + voz polaca)')


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


def qa_traduccion(q, segs, glosario):
    vacios = [s['id'] for s in segs if not s['pl'].strip()]
    q.add('Traducción: todos los segmentos traducidos', 'FALLO' if vacios else 'OK', f'vacíos: {vacios}' if vacios else f'{len(segs)} segmentos')
    # los nombres propios (con mayúscula) y los términos que el original ya trae (p. ej. «alucín») pueden llevar tildes o ñ
    def con_tilde_ajena(sg):
        base = {w.lower() for w in re.findall(r'\w+', sg['es']) if len(w) >= 4}
        malas = [w for w in sg['pl'].split() if not w[:1].isupper() and w[:1] not in '„"' and re.search(r'[ñáéíúü]', w)
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


def cmd_qa(a):
    w = workdir(a)
    data = cargar_segmentos(w)
    segs = data['segments']
    q = QA()
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
    q.add('Audio: etiqueta de idioma = pol', 'OK' if lang == 'pol' else 'AVISO', str(lang))
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
    voz = leer_wav(w / 'voz_pl.wav')
    mudos = []
    for t in tim:
        i0 = int(t['start'] * SR); seg = voz[i0:i0 + int(t['dur_final'] * SR)]
        if len(seg) == 0 or db(np.sqrt(np.mean(seg ** 2))) < -50:
            mudos.append(t['id'])
    q.add('Cobertura: todos los segmentos tienen voz audible', 'FALLO' if mudos else 'OK', f'sin voz: {mudos}' if mudos else '')
    # --- traducción
    glp = Path(a.glosario) if a.glosario else None
    qa_traduccion(q, segs, json.loads(glp.read_text(encoding='utf-8')) if glp and glp.exists() else {})
    # --- pruebas con reconocimiento de voz (si está faster-whisper)
    try:
        from faster_whisper import WhisperModel
        m = WhisperModel(a.modelo, device='auto', compute_type='auto')
        sg, _ = m.transcribe(audio_16k(w / 'no_vocals.wav'), language='es', vad_filter=True)
        palabras = sum(len(s.text.split()) for s in sg if s.no_speech_prob < 0.4)
        q.add('Voz española eliminada (reconocimiento sobre la música)', 'OK' if palabras <= 8 else 'FALLO', f'{palabras} palabras detectadas')
        sg, info = m.transcribe(audio_16k(w / 'voz_pl.wav'), language='pl', vad_filter=True)
        def palabras(t):      # solo palabras comunes: los nombres propios (mayúscula) se verifican escuchando
            return [x.lower() for x in re.findall(r'\w+', t) if not x[:1].isupper() and not x.isdigit()]
        oido = ' '.join(s.text for s in sg)
        esperado = ' '.join(s['pl'] for s in segs)
        sim = difflib.SequenceMatcher(None, palabras(oido), palabras(esperado), autojunk=False).ratio()
        q.add('Voz polaca dice lo traducido (similitud ≥ 0.80)', 'OK' if sim >= 0.80 else 'FALLO', f'{sim:.2f}')
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
    s = sub.add_parser('transcribir'); s.add_argument('--video'); s.add_argument('--modelo', default='large-v3'); s.set_defaults(f=cmd_transcribir)
    s = sub.add_parser('afinar'); s.add_argument('--ventana', type=float, default=0.4, help='segundos a cada lado donde buscar el inicio real'); s.set_defaults(f=cmd_afinar)
    s = sub.add_parser('sintetizar')
    s.add_argument('--motor', default='piper', choices=['piper', 'edge', 'cmd', 'prueba'])
    s.add_argument('--modelo-voz', default='voices/pl_PL-mc_speech-medium.onnx', help='motor piper: archivo .onnx de la voz (default: mc_speech)')
    s.add_argument('--voz', default='pl-PL-MarekNeural', help='motor edge: voz de edge-tts (pl-PL-MarekNeural / pl-PL-ZofiaNeural)')
    s.add_argument('--tts-cmd', help="motor cmd: plantilla con {texto} y {salida}")
    s.add_argument('--pronunciacion', default='pronunciacion.json', help='json [[patrón, reemplazo], ...] para pronunciar nombres y cifras')
    s.add_argument('--max-acel', type=float, default=1.12, help='aceleración máxima permitida (default 1.12)')
    s.set_defaults(f=cmd_sintetizar)
    s = sub.add_parser('mezclar'); s.add_argument('video'); s.add_argument('salida'); s.set_defaults(f=cmd_mezclar)
    s = sub.add_parser('qa'); s.add_argument('video'); s.add_argument('salida')
    s.add_argument('--glosario', help='json {"término ES": "término PL"}'); s.add_argument('--modelo', default='large-v3'); s.set_defaults(f=cmd_qa)
    a = p.parse_args()
    a.f(a)


if __name__ == '__main__':
    main()
