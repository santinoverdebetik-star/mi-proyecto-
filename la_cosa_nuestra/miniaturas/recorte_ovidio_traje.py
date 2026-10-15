#!/usr/bin/env python3
"""Recorta a Ovidio (busto con traje) de assets/ovidio_traje.png -> assets/ovidio_traje_recorte.png.
La imagen viene cortada arriba (el pelo toca el borde y hay restos de letras): se descartan las primeras filas."""
import os, cv2, numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__))
a = cv2.imread(os.path.join(AQUI, "assets", "ovidio_traje.png"))[7:, :]
F = 4
a = np.vstack([np.zeros((40, a.shape[1], 3), np.uint8) + a[0:1].mean(axis=(0, 1)).astype(np.uint8), a])      # margen arriba
big = cv2.resize(a, None, fx=F, fy=F, interpolation=cv2.INTER_CUBIC)
big = cv2.addWeighted(big, 1.35, cv2.GaussianBlur(big, (0, 0), 3), -0.35, 0)
H, W = big.shape[:2]
top = 40 * F
mask = np.full((H, W), cv2.GC_PR_BGD, np.uint8)
mask[:top - 6] = cv2.GC_BGD
mask[top:, int(0.14 * W):int(0.86 * W)] = cv2.GC_PR_FGD
mask[int(0.22 * H):, int(0.30 * W):int(0.72 * W)] = cv2.GC_FGD
mask[int(0.90 * H):, int(0.05 * W):int(0.95 * W)] = cv2.GC_FGD
bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
cv2.grabCut(big, mask, None, bg, fg, 10, cv2.GC_INIT_WITH_MASK)
m = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
m = np.where(lab == 1 + np.argmax(st[1:, 4]), 255, 0).astype(np.uint8)
# cupula de pelo reflejando las filas de abajo
# la imagen viene cortada arriba (el pelo toca el borde): no se inventa pelo; en la miniatura el borde superior del cuadro hace de corte
m[:top + 1] = 0
m[top + 1:top + 3, :] = m[top + 3:top + 4, :]
m = cv2.GaussianBlur(m, (0, 0), 2.4)
out = cv2.cvtColor(big, cv2.COLOR_BGR2BGRA); out[..., 3] = m
cv2.imwrite(os.path.join(AQUI, "assets", "ovidio_traje_recorte.png"), out)
prev = np.full_like(big, (30, 30, 190)); al = (m / 255.0)[..., None]
cv2.imwrite(os.environ.get("PREV", "/tmp/prev.jpg"), np.hstack([big, (big * al + prev * (1 - al)).astype(np.uint8)]))
