#!/usr/bin/env python3
"""Recorta el rostro (con el pelo completo) de la imagen de referencia del usuario (assets/ref_ovidio_8.png) -> assets/ovidio_recorte2.png"""
import os, cv2, numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__))
a = cv2.imread(os.path.join(AQUI, "assets", "ref_ovidio_8.png"))[50:576, 310:720]
big = cv2.resize(a, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
H, W = big.shape[:2]
mask = np.full((H, W), cv2.GC_PR_BGD, np.uint8)
x0, y0, x1 = int(0.04 * W), int(0.02 * H), int(0.96 * W)
mask[:y0] = cv2.GC_BGD; mask[:, :int(0.03 * W)] = cv2.GC_BGD; mask[:, int(0.97 * W):] = cv2.GC_BGD
mask[y0:, x0:x1] = cv2.GC_PR_FGD
# semillas seguras: centro de la cara
mask[int(0.30 * H):int(0.85 * H), int(0.30 * W):int(0.70 * W)] = cv2.GC_FGD
bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
cv2.grabCut(big, mask, None, bg, fg, 10, cv2.GC_INIT_WITH_MASK)
m = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
m = np.where(lab == 1 + np.argmax(st[1:, 4]), 255, 0).astype(np.uint8)
m = cv2.GaussianBlur(m, (0, 0), 2.2)
out = cv2.cvtColor(big, cv2.COLOR_BGR2BGRA); out[..., 3] = m
cv2.imwrite(os.path.join(AQUI, "assets", "ovidio_recorte2.png"), out)
prev = np.full_like(big, (30, 30, 190)); al = (m / 255.0)[..., None]
cv2.imwrite(os.environ.get("PREV", "/tmp/prev.jpg"), np.hstack([big, (big * al + prev * (1 - al)).astype(np.uint8)]))
