# Quita al hombre de traje detrás de la mesa de mapas (toma 4): placa sin él (Nano Banana sobre la mediana),
# alineada por ECC y compuesta en su zona cuadro por cuadro, sin tocar a Regina (matte).
import cv2, numpy as np, subprocess, os, sys
src, mdir, out = sys.argv[1:4]
FF = os.path.expanduser('~/arkamia-reels/bin/ffmpeg')
med = cv2.imread('plate4.png'); H, W = med.shape[:2]
cl = cv2.resize(cv2.imread('plate4_sin-hombre_raw.png'), (W, H), interpolation=cv2.INTER_LANCZOS4)
g1, g2 = [cv2.cvtColor(x, cv2.COLOR_BGR2GRAY).astype(np.float32)/255 for x in (med, cl)]
msk = np.full((H, W), 255, np.uint8); msk[600:1000, 650:960] = 0; msk[:, 300:780] = 0     # fuera la zona del hombre y de Regina
Wm = np.eye(3, dtype=np.float32)
_, Wm = cv2.findTransformECC(g1, g2, Wm, cv2.MOTION_HOMOGRAPHY, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), msk, 5)
cl = cv2.warpPerspective(cl, Wm, (W, H), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP).astype(np.float32)
Z = np.zeros((H, W), np.float32); cv2.rectangle(Z, (690, 670), (935, 952), 1, -1)
ring = cv2.dilate(Z, np.ones((41, 41), np.uint8)) - Z; ring[:, :780] = 0
for c in range(3): cl[..., c] *= med[..., c][ring > 0].mean()/max(cl[..., c][ring > 0].mean(), 1)
Zs = cv2.GaussianBlur(Z, (0, 0), 10)
cap = cv2.VideoCapture(src); nm = len(os.listdir(mdir)); i = 0
p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                      '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
while True:
    r, f = cap.read()
    if not r: break
    m = cv2.imread(f'{mdir}/m_{min(i, nm - 1):05d}.png', 0)
    m = cv2.resize(m, (W, H)).astype(np.float32)/255
    m[:, 900:] = 0                                            # el matte también agarra al hombre: Regina nunca pasa de x≈900
    # dentro de la zona del hombre, el matte solo vale donde hay piel/top claro de Regina (su mano/brazo), no el traje oscuro
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV); light = ((hsv[..., 2] > 135) & ~((hsv[..., 0] > 95) & (hsv[..., 0] < 135) & (hsv[..., 1] > 60))).astype(np.float32)
    light = cv2.morphologyEx(light, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    m = np.where(Z > 0, m*light, m)
    # la cabeza/camisa blanca del hombre también es clara: fuera de la silueta conectada al cuerpo de Regina
    reg = (m > .3).astype(np.uint8); n, lb, st, _ = cv2.connectedComponentsWithStats(reg)
    if n > 1: k = 1 + np.argmax(st[1:, 4]); m = m*(lb == k)
    md = cv2.GaussianBlur(cv2.dilate(m, np.ones((9, 9), np.uint8)), (0, 0), 2)          # fuera de la zona: margen normal
    mz = cv2.GaussianBlur(cv2.erode(m, np.ones((3, 3), np.uint8)), (0, 0), 1.0)         # en la zona: borde justo, sin traje
    m = np.where(cv2.dilate(Z, np.ones((25, 25), np.uint8)) > 0, mz, md)
    a = (Zs*(1 - m))[..., None]
    p.stdin.write(np.clip(f*(1 - a) + cl*a, 0, 255).astype(np.uint8).tobytes()); i += 1
p.stdin.close(); p.wait()
