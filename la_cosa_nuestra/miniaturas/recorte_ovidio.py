#!/usr/bin/env python3
"""Recorta el rostro de assets/ovidio_original.png (captura de baja resolucion) -> assets/ovidio_recorte.png"""
import os, cv2, numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__))
a = cv2.imread(os.path.join(AQUI, "assets", "ovidio_original.png"))[13:, :250]
PAD = 26                                                                       # el pelo toca el borde de arriba: se agrega pared para no recortarlo
pared = np.median(a[3:12, 8:30].reshape(-1, 3), axis=0)
a = np.vstack([np.tile(pared.astype(np.uint8), (PAD, a.shape[1], 1)), a])
big = cv2.resize(a, None, fx=3.5, fy=3.5, interpolation=cv2.INTER_LANCZOS4)
big = cv2.addWeighted(big, 1.5, cv2.GaussianBlur(big, (0, 0), 3), -0.5, 0)
H, W = big.shape[:2]
mask = np.zeros((H, W), np.uint8); bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
cv2.grabCut(big, mask, (int(0.08 * W), int((PAD * 3.5 - 25)), int(0.84 * W), H - int(PAD * 3.5 - 25) - 2), bg, fg, 8, cv2.GC_INIT_WITH_RECT)
m = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
m = np.where(lab == 1 + np.argmax(st[1:, 4]), 255, 0).astype(np.uint8)
# el pelo viene cortado por el borde de la captura: se reconstruye la cupula de rizos reflejando las filas de arriba
ys = np.nonzero(m.max(axis=1) > 0)[0]; y0 = int(ys[0]) + 3
xs = np.nonzero(m[y0 + 2] > 0)[0]; xc, hw = (xs[0] + xs[-1]) / 2, (xs[-1] - xs[0]) / 2
D = 38
for d in range(1, D + 1):
    ancho = hw * 1.04 * max(0.0, 1 - (d / (D + 2)) ** 2.4) ** (1 / 2.4)
    xx = np.arange(W); dentro = (np.abs(xx - xc) <= ancho) & (m[y0 + d] > 0)
    big[y0 - d, dentro] = (big[y0 + d, dentro] * 0.93).astype(np.uint8); m[y0 - d, dentro] = 255
m = cv2.GaussianBlur(m, (0, 0), 3.0)
out = cv2.cvtColor(big, cv2.COLOR_BGR2BGRA); out[..., 3] = m
cv2.imwrite(os.path.join(AQUI, "assets", "ovidio_recorte.png"), out)
prev = np.full_like(big, (30, 30, 190)); al = (m / 255.0)[..., None]
cv2.imwrite(os.environ.get("PREV", "/tmp/prev.jpg"), np.hstack([big, (big * al + prev * (1 - al)).astype(np.uint8)]))
