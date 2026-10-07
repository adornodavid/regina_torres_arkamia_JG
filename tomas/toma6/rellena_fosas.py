# Rellena por código las fosas de alberca de la obra negra (Nano Banana Pro no las quitó): inpaint + grano de tierra.
# Liz pidió casas sin alberca (2026-10-07). Respeta la palma que tapa parte de dos fosas.
import cv2, numpy as np
a = cv2.imread('casas_obraL.png'); H, W = a.shape[:2]
P = [[(1130, 204), (1209, 204), (1199, 237), (1118, 237)],
     [(1660, 164), (1745, 164), (1760, 218), (1690, 218)],
     [(967, 219), (1017, 219), (999, 265), (970, 265)],
     [(1487, 30), (1629, 30), (1635, 53), (1490, 53)],
     [(1162, 58), (1309, 58), (1309, 76), (1165, 76)],
     [(851, 96), (948, 96), (948, 117), (851, 117)]]
m = np.zeros((H, W), np.uint8)
for p in P: cv2.fillPoly(m, [np.int32(p)], 255)
m = cv2.dilate(m, np.ones((5, 5), np.uint8))
hsv = cv2.cvtColor(a, cv2.COLOR_BGR2HSV)
verde = ((hsv[..., 0] > 30) & (hsv[..., 0] < 90) & (hsv[..., 1] > 60)).astype(np.uint8)*255
verde = cv2.dilate(verde, np.ones((3, 3), np.uint8))
pal = cv2.dilate(verde, np.ones((9, 9), np.uint8)) & cv2.dilate(m, np.ones((41, 41), np.uint8))   # palma cerca de la fosa
m[verde > 0] = 0
o = cv2.inpaint(a, m | pal, 9, cv2.INPAINT_TELEA).astype(np.float32)   # la palma no presta color al relleno
g = np.random.default_rng(1).normal(0, 5, (H, W, 1)).astype(np.float32)
o = np.where(m[..., None] > 0, o + cv2.GaussianBlur(g, (0, 0), .8)[..., None] * 1.6, o)
mm = cv2.GaussianBlur(m, (0, 0), 1.5).astype(np.float32)[..., None]/255
cv2.imwrite('casas_obraL_sa.png', np.clip(a*(1 - mm) + o*mm, 0, 255).astype(np.uint8))
