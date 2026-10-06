# Acabado de cámara real sobre un still generado (quita el look de render): roll-off de altas luces, negros levantados,
# halación/bloom en luces, suavidad de lente, aberración cromática en orillas, viñeta y grano de sensor por luminancia.
import cv2, numpy as np, sys
src, out = sys.argv[1], sys.argv[2]
im = cv2.imread(src).astype(np.float32)/255; H, W = im.shape[:2]
# 1) suavidad de lente (el render es demasiado nítido) + micro-contraste más bajo
soft = cv2.GaussianBlur(im, (0, 0), .8); im = im*.65 + soft*.35
# 2) curva fílmica: negros levantados y altas luces que se queman suave
im = .012 + im*.988; k = .78; im = np.where(im > k, k + (1 - k)*(1 - np.exp(-(im - k)/(1 - k)*1.3))/(1 - np.exp(-1.3)), im)   # solo las altas luces se queman suave
# 3) halación/bloom alrededor de lo más brillante (cielo, ventanales, lámparas)
lum = im.mean(2, keepdims=True); hi = np.clip((lum - .78)/.22, 0, 1)*im
bloom = cv2.GaussianBlur(hi, (0, 0), 14)*.16 + cv2.GaussianBlur(hi, (0, 0), 50)*.10
bloom[..., 2] *= 1.15; bloom[..., 0] *= .85               # un poco cálido, como halación
im = 1 - (1 - im)*(1 - bloom)
# 4) aberración cromática radial (rojo hacia afuera, azul hacia adentro)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); cx, cy = W/2, H/2
def radial(ch, k): return cv2.remap(ch, (cx + (xx - cx)*(1 + k)).astype(np.float32), (cy + (yy - cy)*(1 + k)).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
im[..., 2] = radial(im[..., 2], -.0012); im[..., 0] = radial(im[..., 0], .0012)
# 5) viñeta suave
r = np.sqrt(((xx - cx)/cx)**2 + ((yy - cy)/cy)**2); im *= (1 - .22*np.clip(r - .45, 0, 1)**1.6)[..., None]
# 6) saturación un poco más baja en verdes y morados muy limpios
hsv = cv2.cvtColor(np.clip(im, 0, 1).astype(np.float32), cv2.COLOR_BGR2HSV); hsv[..., 1] *= .92; im = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
# 7) grano de sensor (más en sombras), con algo de tamaño
rng = np.random.default_rng(3); g = rng.normal(0, 1, (H, W)).astype(np.float32)
g = cv2.GaussianBlur(g, (0, 0), .7); g /= g.std()
amp = .022*(1.2 - im.mean(2))
im = im + (g*amp)[..., None] + rng.normal(0, .004, im.shape).astype(np.float32)
cv2.imwrite(out, np.clip(im*255, 0, 255).astype(np.uint8))
