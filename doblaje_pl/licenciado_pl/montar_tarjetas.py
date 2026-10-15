"""Superpone en el video original los recortes ya traducidos (cards/overlays.json) -> video_txt.mp4 (audio original sin tocar)."""
import json, subprocess, sys
video, carpeta, salida = sys.argv[1:4]
meta = json.load(open(f'{carpeta}/overlays.json'))
entradas, filtros, prev = [], [], '0:v'
for k, (ci, m) in enumerate(sorted(meta.items(), key=lambda kv: kv[1]['n0']), start=1):
    x0, y0, x1, y1 = m['box']; w, h = x1 - x0, y1 - y0
    entradas += ['-framerate', '30', '-start_number', str(m['n0']), '-i', f"{carpeta}/f{int(ci):02d}/o_%06d.png"]
    filtros.append(f"[{k}:v]crop={w}:{h}:{x0}:{y0},format=rgb24,setpts=PTS+{m['n0']}/30/TB[a{k}]")
    filtros.append(f"[{prev}][a{k}]overlay={x0}:{y0}:eof_action=pass:format=auto[v{k}]")
    prev = f'v{k}'
open('filtro_tarjetas.txt', 'w').write(';\n'.join(filtros))
cmd = ['ffmpeg', '-v', 'error', '-y', '-i', video] + entradas + ['-filter_complex_script', 'filtro_tarjetas.txt', '-map', f'[{prev}]', '-map', '0:a',
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'copy', '-movflags', '+faststart', salida]
subprocess.run(cmd, check=True)
print('Listo', salida)
