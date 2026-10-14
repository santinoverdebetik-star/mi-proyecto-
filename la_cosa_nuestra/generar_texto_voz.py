#!/usr/bin/env python3
"""Convierte GUION_V2.md en texto limpio para la voz: GUION_V2_texto_voz.txt
(quita sellos y marcas, convierte [PAUSA] en '...', y dice en voz alta 'Regla numero N ... Sello: X')."""
import re, sys
nums = "uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciséis diecisiete dieciocho diecinueve veinte".split()
t = open("GUION_V2.md", encoding="utf-8").read()
body = t.split("## GANCHO", 1)[1].split("## Tabla de sellos", 1)[0]
body = body.split("\n", 1)[1]  # resto de la linea del encabezado (" — música A")
out = []
for line in body.split("\n"):
    s = line.rstrip()
    if not s.strip() or s.strip() == "---":
        continue
    if s.startswith("# PARTE"):
        m = re.match(r"# PARTE (\d) — (.*?) \(música", s)
        n = int(m.group(1)); out.append(f"\nParte {nums[n-1]}. {m.group(2).strip().capitalize()}.\n"); continue
    if s.startswith("## "):
        m = re.match(r'## (\d+)\. "?(.*?)"? — \*\*\[(.*?)\]\*\*', s)
        if m:
            n = int(m.group(1)); out.append(f"\nRegla número {nums[n-1]}. {m.group(2).strip()}. Sello: {m.group(3).split(':')[0].strip().lower()}.\n")
            continue
        m2 = re.match(r"## 19\. (.*?) — ", s)
        if m2:
            out.append(f"\nRegla número diecinueve. {m2.group(1).strip()}. Sello: a medias.\n")
        continue
    s = re.sub(r"\s*`\[PAUSA\]`\s*", " ... ", s).replace("**", "")
    s = re.sub(r"\s*\.\.\.\s*\.\.\.\s*", " ... ", s)
    out.append(s.strip())
txt = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"
open("GUION_V2_texto_voz.txt", "w", encoding="utf-8").write(txt)
w, c = len(txt.split()), len(txt)
print(f"palabras: {w} | minutos a 145 ppm: {w/145:.1f} | caracteres: {c} | creditos aprox: {max(100, round(c/1000*60))}")
