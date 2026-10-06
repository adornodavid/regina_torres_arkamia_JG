# Endereza las casas generadas: Liz marcó ~10.5° de inclinación (se van a la derecha al subir). Corte (shear) horizontal
# que vale 0 en la banqueta de abajo de las casas y crece con la altura sobre ella → las verticales quedan verticales.
import cv2, numpy as np, sys
DEG = float(sys.argv[1]) if len(sys.argv) > 1 else 10.5
m = cv2.imread('maskL.png', 0); H, W = m.shape
yb = np.array([np.max(np.where(m[:, x] > 0)[0]) if (m[:, x] > 0).any() else 0 for x in range(W)], np.float32)
yb = np.convolve(np.pad(yb, 60, mode='edge'), np.ones(121)/121, 'valid')
s = np.tan(np.radians(DEG))
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
mapx = (xx + s*np.clip(yb[None, :] - yy, 0, None)).astype(np.float32); mapy = yy.astype(np.float32)
for n in ('finL_al', 'obraL_al'):
    cv2.imwrite(n + '_derecho.png', cv2.remap(cv2.imread(n + '.png'), mapx, mapy, cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE))
ref = cv2.imread('refL.png'); a = (cv2.GaussianBlur(m, (0, 0), 8)/255.)[..., None]
f0 = cv2.imread('finL_al.png'); f1 = cv2.imread('finL_al_derecho.png')
c0 = (f0*a + ref*(1-a)).astype(np.uint8)[0:1300, 1350:2450]; c1 = (f1*a + ref*(1-a)).astype(np.uint8)[0:1300, 1350:2450]
cv2.imwrite('derecho_cmp.jpg', cv2.resize(cv2.hconcat([c0, c1]), None, fx=.45, fy=.45))
