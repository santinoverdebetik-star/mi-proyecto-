#!/usr/bin/env python3
"""Voz de PRUEBA (Microsoft Edge TTS, gratis) para maquetar rapido. La voz final es Voizum (ver ../../la_cosa_nuestra/voizum_generar.py).
Genera un mp3 por frase y devuelve las duraciones. Usa el CA de la red de esta nube (no se desactiva la verificacion TLS).
Uso: python3 voz_prueba_edge.py frases.txt carpeta_salida [voz]"""
import asyncio, os, ssl, subprocess, sys, json
import edge_tts, edge_tts.communicate as ec

ec._SSL_CTX = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt"))


async def una(txt, ruta, voz, ritmo):
    await edge_tts.Communicate(txt, voz, rate=ritmo, pitch="-6Hz").save(ruta)


def dur(ruta):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ruta], capture_output=True, text=True).stdout)


def main(frases_txt, out, voz="es-MX-JorgeNeural", ritmo="-8%"):
    os.makedirs(out, exist_ok=True)
    frases = [l.strip() for l in open(frases_txt, encoding="utf-8") if l.strip()]
    res = []
    for i, f in enumerate(frases):
        r = os.path.join(out, f"frase_{i + 1:02d}.mp3")
        asyncio.run(una(f, r, voz, ritmo)); res.append({"texto": f, "archivo": r, "dur": round(dur(r), 3)})
        print(i + 1, res[-1]["dur"], f[:60], flush=True)
    json.dump(res, open(os.path.join(out, "frases.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:4])
