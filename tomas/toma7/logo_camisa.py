# Cambia el bordado de dos renglones por el logo real "terra regia" en UNA línea (Nano Banana insistía en partirlo).
# Borra solo los pixeles de las letras (máscara por brillo) y los rellena con la tela de alrededor; luego "borda" el
# logo real con la luz y las arrugas de la camisa.
import cv2, numpy as np
from PIL import Image
im = cv2.imread('opcion1.png'); X0, Y0 = 1075, 1376
x0, y0, x1, y1 = X0 + 85, Y0 + 192, X0 + 156, Y0 + 276
reg = cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
m = np.zeros(im.shape[:2], np.uint8); m[y0:y1, x0:x1] = (reg > 150).astype(np.uint8)*255
m = cv2.dilate(m, np.ones((7, 7), np.uint8))
clean = cv2.inpaint(im, m, 4, cv2.INPAINT_TELEA).astype(np.float32)
g = np.random.default_rng(1).normal(0, 4.5, im.shape[:2]).astype(np.float32)          # grano de tela en lo rellenado
mm = cv2.GaussianBlur(m.astype(np.float32)/255, (0, 0), 2)[..., None]
clean = np.clip(clean + g[..., None]*mm, 0, 255).astype(np.uint8)
lg = Image.open('/Users/mercadotecnia.mghm/Downloads/Logotipo Corporate/Png/TR_Logotipo_02.png').convert('RGBA'); lg = lg.crop(lg.getbbox())
Wl = 76; Hl = int(lg.height*Wl/lg.width); a = np.asarray(lg.resize((Wl*4, Hl*4), Image.LANCZOS))[..., 3].astype(np.float32)/255
cx, cy = (x0 + x1)/2 - 3, (y0 + y1)/2 - 6
src = np.float32([[0, 0], [Wl*4, 0], [Wl*4, Hl*4], [0, Hl*4]])
dst = np.float32([[cx - Wl/2, cy - Hl/2 + 2], [cx + Wl/2 - 2, cy - Hl/2 - 3], [cx + Wl/2 - 2, cy + Hl/2 - 2], [cx - Wl/2, cy + Hl/2 + 3]])
A = cv2.warpPerspective(a, cv2.getPerspectiveTransform(src, dst), (im.shape[1], im.shape[0]), flags=cv2.INTER_AREA)
A = cv2.GaussianBlur(A, (0, 0), .5)
lum = cv2.cvtColor(clean, cv2.COLOR_BGR2GRAY).astype(np.float32); shade = np.clip(lum/np.maximum(cv2.GaussianBlur(lum, (0, 0), 20), 1), .9, 1.1)
col = np.array([226, 230, 226], np.float32)[None, None, :]*shade[..., None]
out = clean.astype(np.float32)*(1 - A[..., None]*.92) + col*A[..., None]*.92
cv2.imwrite('opcion1_logo.png', np.clip(out, 0, 255).astype(np.uint8))
z = np.clip(out, 0, 255).astype(np.uint8)[Y0 + 120:Y0 + 340, X0 + 30:X0 + 250]
cv2.imwrite('c_logo4.jpg', cv2.hconcat([cv2.resize(im[Y0 + 120:Y0 + 340, X0 + 30:X0 + 250], None, fx=2, fy=2), cv2.resize(z, None, fx=2, fy=2)]))
