# Toma 6 (v2, proporción real): drone horizontal DJI_0052 seg. 16–26 → ventana vertical 9:16 que sigue al parque.
# El fondo es el cuadro ORIGINAL (solo recorte + zoom, sin deformar); las casas (obra negra → terminadas) se llevan a
# cada cuadro con la homografía del suelo y se construyen por celdas de cerca hacia lejos. Speed ramp de entrada/salida.
import cv2, numpy as np, subprocess, os
FF = os.path.expanduser('~/arkamia-reels/bin/ffmpeg'); FPS = 30; L = 4.60; OW, OH = 1080, 1920
ease = lambda p: 1 - (1 - min(max(p, 0), 1))**3
cap = cv2.VideoCapture('droneL.mp4'); FR = []
while True:
    r, f = cap.read()
    if not r: break
    FR.append(f)
N = len(FR); H, W = FR[0].shape[:2]; HL = np.load('HL_to_ref.npy')[:N]
corn = np.float32([[0, 0], [W, 0], [W, H], [0, H]])
PJ = np.array([cv2.perspectiveTransform(corn[None], h)[0] for h in HL])
HL = [cv2.getPerspectiveTransform(corn, np.float32(PJ[max(0, j-4):j+5].mean(0))) for j in range(N)]
OBRA = cv2.imread('obraL_al_derecho.png').astype(np.float32); FIN = cv2.imread('finL_al_derecho.png').astype(np.float32)
HM = cv2.GaussianBlur(cv2.imread('maskL.png', 0), (0, 0), 6).astype(np.float32)/255
yy, xx = np.mgrid[0:H, 0:W]; FE = 60.
HM *= np.clip(np.minimum.reduce([yy/FE, xx/FE, (W - 1 - xx)/FE]), 0, 1)
CELL = 64; rng = np.random.default_rng(6); cells = []
for y in range(0, H, CELL):
    for x in range(0, W, CELL):
        if HM[y:y+CELL, x:x+CELL].mean() > .1: cells.append((x, y))
ys = np.array([c[1] for c in cells]); order = np.argsort(-(ys + rng.normal(0, 70, len(cells))))
DB = .22
def starts(t0, t1): return {cells[k]: t0 + (t1 - t0 - DB)*r/len(cells) for r, k in enumerate(order)}
SO, SF = starts(.40, 1.75), starts(1.80, 3.30)
def build(st, t):
    m = np.zeros((H, W), np.float32)
    for (x, y), s in st.items():
        u = ease((t - s)/DB)
        if u <= 0: continue
        h = int(CELL*u); m[y+CELL-h:y+CELL, x:x+CELL] = 1
    return cv2.GaussianBlur(m, (0, 0), 2)*HM
# la ventana sigue a la casa club (punto fijo del suelo en la referencia), suavizado
TGT = np.float32([[[1840, 760]]])
cx = np.array([cv2.perspectiveTransform(TGT, np.linalg.inv(h))[0, 0, 0] for h in HL])
cx = np.convolve(np.pad(cx, 20, mode='edge'), np.ones(41)/41, 'valid')
tt = np.arange(int(round(L*FPS)))/FPS
# solo el tramo central del drone (cuadros 105–195, alrededor de la referencia): con poco desplazamiento lateral las
# casas, que tienen altura, no se tuercen al seguir el suelo. Va en cámara lenta suave (3 s de drone en 4.6 s).
A0, A1 = 105, 195
pos = A0 + (A1 - A0)*tt/tt[-1]; v = np.full_like(tt, (A1 - A0)/len(tt)*N/(N - 1))
def radial_blur(img, amt, c):
    if amt < .05: return img
    acc = img.copy(); n = 6
    for k in range(1, n + 1):
        M = cv2.getRotationMatrix2D(c, 0, 1 + amt*.012*k); acc += cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), borderMode=cv2.BORDER_REFLECT)
    return acc/(n + 1)
p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', 's6.mp4'], stdin=subprocess.PIPE)
for n, t in enumerate(tt):
    sp = pos[n]; spd = v[n]*(N - 1)/np.cumsum(v)[-1]; k = int(round(sp))
    ks = range(max(0, k - int(spd//2)), min(N, k + int(spd//2) + 1))
    z = 1.22 + .07*(1 - ease(t/.45))                              # encuadre más arriba: casas + parque, menos calle
    c = float(np.clip(cx[min(k, N - 1)], OW/(2*z) + 1, W - OW/(2*z) - 1)); cy = OH/(2*z)   # pegado al borde de arriba
    Mz = np.array([[z, 0, OW/2 - z*c], [0, z, OH/2 - z*cy], [0, 0, 1.]])
    j0 = int(sp); f = sp - j0; j1 = min(j0 + 1, N - 1)
    src = FR[j0].astype(np.float32)*(1 - f) + FR[j1].astype(np.float32)*f
    out = cv2.warpAffine(src, Mz[:2], (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    G = Mz @ np.linalg.inv(HL[min(k, N - 1)])
    for st_, IMG in ((SO, OBRA), (SF, FIN)):
        m = build(st_, t)
        if m.max() <= 0: continue
        mw = cv2.warpPerspective(m, G, (OW, OH), flags=cv2.INTER_LINEAR)[..., None]
        out = out*(1 - mw) + cv2.warpPerspective(IMG, G, (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)*mw
    p.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
