# Kling borroneó el logo de la camisa al girar al agente: se rastrea el pecho (KLT + homografía) y se vuelve a pegar el
# logo limpio del still en cada cuadro, con la luz de la tela del cuadro.
import cv2, numpy as np, subprocess, os
FF = os.path.expanduser('~/arkamia-reels/bin/ffmpeg')
cap = cv2.VideoCapture('kling7.mp4'); fr = []
while True:
    r, f = cap.read()
    if not r: break
    fr.append(f)
H, W = fr[0].shape[:2]; st = cv2.imread('opcion1_logo.png'); sc = W/st.shape[1]
# capa del logo en coordenadas del still → cuadro 0
from PIL import Image
lg = Image.open('/Users/mercadotecnia.mghm/Downloads/Logotipo Corporate/Png/TR_Logotipo_02.png').convert('RGBA'); lg = lg.crop(lg.getbbox())
X0, Y0 = 1075, 1376; x0, y0, x1, y1 = X0 + 85, Y0 + 192, X0 + 156, Y0 + 276
Wl = 76; Hl = int(lg.height*Wl/lg.width); a = np.asarray(lg.resize((Wl*4, Hl*4), Image.LANCZOS))[..., 3].astype(np.float32)/255
cx, cy = (x0 + x1)/2 - 3, (y0 + y1)/2 - 6
src = np.float32([[0, 0], [Wl*4, 0], [Wl*4, Hl*4], [0, Hl*4]])
dst = np.float32([[cx - Wl/2, cy - Hl/2 + 2], [cx + Wl/2 - 2, cy - Hl/2 - 3], [cx + Wl/2 - 2, cy + Hl/2 - 2], [cx - Wl/2, cy + Hl/2 + 3]])*sc
A0 = cv2.warpPerspective(a, cv2.getPerspectiveTransform(src, dst), (W, H), flags=cv2.INTER_AREA)
ys, xs = np.where(A0 > .05); bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max(), ys.max()
# puntos a rastrear: tela del pecho alrededor del logo (sin el logo mismo)
g0 = cv2.cvtColor(fr[0], cv2.COLOR_BGR2GRAY); roi = np.zeros_like(g0)
roi[by0 - 70:by1 + 90, bx0 - 50:bx1 + 40] = 255; roi[by0 - 4:by1 + 4, bx0 - 4:bx1 + 4] = 0
p0 = cv2.goodFeaturesToTrack(g0, 200, .005, 5, mask=roi); print('puntos', len(p0))
Hs = [np.eye(3)]; prev = g0; pp = p0; Hacc = np.eye(3); P0 = p0.copy()
for i in range(1, len(fr)):
    g = cv2.cvtColor(fr[i], cv2.COLOR_BGR2GRAY)
    pn, s, _ = cv2.calcOpticalFlowPyrLK(prev, g, pp, None, winSize=(25, 25), maxLevel=3)
    k = s.ravel() == 1; P0, pn = P0[k], pn[k]
    Hm, _ = cv2.estimateAffine2D(P0, pn, method=cv2.RANSAC, ransacReprojThreshold=2.0)
    Hs.append(np.vstack([Hm, [0, 0, 1]])); prev, pp = g, pn
# suavizado temporal de las esquinas
c = np.float32([[bx0, by0], [bx1, by0], [bx1, by1], [bx0, by1]])
PJ = np.array([cv2.perspectiveTransform(c[None], h)[0] for h in Hs]); PJ = np.array([PJ[max(0, i-2):i+3].mean(0) for i in range(len(PJ))])
p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '24', '-i', '-',
                      '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', 'kling7_logo.mp4'], stdin=subprocess.PIPE)
for i, f in enumerate(fr):
    M = cv2.getPerspectiveTransform(c, np.float32(PJ[i])); A = cv2.warpPerspective(A0, M, (W, H))
    # borra el borrón de Kling bajo el logo: mancha clara → tela (inpaint sólo de pixeles claros cerca del logo)
    zone = cv2.dilate((A > .02).astype(np.uint8), np.ones((15, 15), np.uint8))
    gl = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY); base = cv2.medianBlur(gl, 21)
    bright = ((gl.astype(np.int16) - base) > 14).astype(np.uint8)*zone
    f2 = cv2.inpaint(f, cv2.dilate(bright, np.ones((3, 3), np.uint8))*255, 3, cv2.INPAINT_TELEA) if bright.any() else f
    lum = cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY).astype(np.float32); shade = np.clip(lum/np.maximum(cv2.GaussianBlur(lum, (0, 0), 14), 1), .9, 1.1)
    col = np.array([226, 230, 226], np.float32)[None, None, :]*shade[..., None]
    out = f2.astype(np.float32)*(1 - A[..., None]*.92) + col*A[..., None]*.92
    p.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
