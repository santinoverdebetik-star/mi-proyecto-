#!/usr/bin/env python3
"""Alinea GUION_V2_texto_voz.txt con las palabras transcritas por whisper (palabras.json).
Uso: python3 alinear_guion.py GUION_V2_texto_voz.txt palabras.json timeline.json
Salida: bloques (inicio de cada Parte / Regla / Cierre) y cada palabra del guion con su tiempo."""
import difflib, json, re, sys, unicodedata


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def main(guion, palabras_json, salida):
    lines = [l for l in open(guion, encoding="utf-8").read().split("\n") if l.strip()]
    pal = json.load(open(palabras_json, encoding="utf-8"))
    dur = pal["duracion"]
    W = [(p["w"], p["t0"], p["t1"]) for p in pal["palabras"] if norm(p["w"])]
    # palabras del guion: (texto, indice de linea)
    S = []
    for li, l in enumerate(lines):
        for tok in l.split():
            if norm(tok):
                S.append((tok, li))
    sn, wn = [norm(t) for t, _ in S], [norm(w) for w, _, _ in W]
    sm = difflib.SequenceMatcher(None, sn, wn, autojunk=False)
    t0 = [None] * len(S)
    t1 = [None] * len(S)
    emparejadas = 0
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            t0[a + k], t1[a + k] = W[b + k][1], W[b + k][2]
            emparejadas += 1
    # interpolar las que no coinciden
    i = 0
    while i < len(S):
        if t0[i] is None:
            j = i
            while j < len(S) and t0[j] is None:
                j += 1
            prev = t1[i - 1] if i > 0 else 0.0
            nxt = t0[j] if j < len(S) else dur
            paso = max(0.0, nxt - prev) / (j - i)
            for k in range(i, j):
                t0[k] = prev + (k - i) * paso
                t1[k] = prev + (k - i + 1) * paso
            i = j
        else:
            i += 1
    # bloques: buscar lineas "Parte N." y "Regla numero N."
    bloques = []
    primera = {}
    for idx, (_, li) in enumerate(S):
        primera.setdefault(li, idx)
    for li, l in enumerate(lines):
        m = re.match(r"Parte (\w+)\. (.*)\.$", l.strip())
        r = re.match(r"Regla número (\w+)\. (.*)\. Sello: (.*)\.$", l.strip())
        if m:
            bloques.append({"tipo": "parte", "n": m.group(1), "titulo": m.group(2), "linea": li, "idx": primera[li]})
        elif r:
            bloques.append({"tipo": "regla", "n": r.group(1), "titulo": r.group(2), "sello": r.group(3), "linea": li,
                            "idx": primera[li]})
        elif l.startswith("A cada regla le voy a poner un sello"):
            bloques.append({"tipo": "sellos", "titulo": "Cómo leer este expediente", "linea": li, "idx": primera[li]})
        elif l.startswith("Hagamos cuentas"):
            bloques.append({"tipo": "cierre", "titulo": "Hagamos cuentas", "linea": li, "idx": primera[li]})
    bloques.insert(0, {"tipo": "gancho", "titulo": "Gancho", "linea": 0, "idx": 0})
    for k, b in enumerate(bloques):
        b["t0"] = round(t0[b["idx"]], 2)
        b["t1"] = round(t0[bloques[k + 1]["idx"]] if k + 1 < len(bloques) else dur, 2)
        # momento exacto de la palabra "Sello:" para el sello visual
        if b["tipo"] == "regla":
            for q in range(b["idx"], min(b["idx"] + 40, len(S))):
                if norm(S[q][0]) == "sello":
                    b["t_sello"] = round(t0[q], 2)
                    break
    palabras = [{"w": S[k][0], "t0": round(t0[k], 3), "t1": round(t1[k], 3), "l": S[k][1]} for k in range(len(S))]
    json.dump({"duracion": dur, "bloques": bloques, "palabras": palabras}, open(salida, "w", encoding="utf-8"),
              ensure_ascii=False)
    print(f"palabras del guion: {len(S)} | de whisper: {len(W)} | emparejadas: {emparejadas} "
          f"({100 * emparejadas / len(S):.1f}%) | bloques: {len(bloques)}")
    for b in bloques:
        print(f"{b['t0']:7.1f} s  {b['tipo']:7s} {b.get('n', ''):>10s} {b['titulo'][:60]}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
