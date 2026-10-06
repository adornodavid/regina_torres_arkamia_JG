# Compone el piso limpiado (Nano Banana sobre la placa mediana) en la zona de las manchas, cuadro por cuadro,
# excluyendo a Regina (matte) y las espigas de lavanda que se mueven. Cámara fija → la placa queda pegada.
import cv2, numpy as np, subprocess, os, sys
src, mdir, out = sys.argv[1:4]
FF = os.path.expanduser('~/arkamia-reels/bin/ffmpeg')
med = cv2.imread('plate8.png'); H, W = med.shape[:2]
cl = cv2.resize(cv2.imread('plate8_clean_raw.png'), (W, H), interpolation=cv2.INTER_LANCZOS4)
# alineación ECC (homografía) usando solo la parte de arriba del piso/edificio, sin las manchas
g1, g2 = [cv2.cvtColor(x, cv2.COLOR_BGR2GRAY).astype(np.float32)/255 for x in (med, cl)]
msk = np.zeros((H, W), np.uint8); msk[900:1700] = 255; msk[1300:1580, 560:1060] = 0
Wm = np.eye(3, dtype=np.float32)
_, Wm = cv2.findTransformECC(g1, g2, Wm, cv2.MOTION_HOMOGRAPHY, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), msk, 5)
cl = cv2.warpPerspective(cl, Wm, (W, H), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP).astype(np.float32)
# igualar tono global de la zona (por si Nano Banana movió la exposición)
Z = np.zeros((H, W), np.float32); cv2.rectangle(Z, (560, 1300), (1060, 1580), 1, -1)
ring = cv2.dilate(Z, np.ones((61, 61), np.uint8)) - Z
for c in range(3): cl[..., c] *= med[..., c][ring > 0].mean()/max(cl[..., c][ring > 0].mean(), 1)
Zs = cv2.GaussianBlur(Z, (0, 0), 14)
cap = cv2.VideoCapture(src); p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                      '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
nm = len(os.listdir(mdir)); i = 0
while True:
    r, f = cap.read()
    if not r: break
    m = cv2.imread(f'{mdir}/m_{min(i, nm - 1):05d}.png', 0).astype(np.float32)/255
    m = cv2.GaussianBlur(cv2.dilate(m, np.ones((11, 11), np.uint8)), (0, 0), 2)
    mov = np.clip((cv2.absdiff(f, med).max(2).astype(np.float32) - 22)/20, 0, 1)
    mov = cv2.GaussianBlur(cv2.dilate(mov, np.ones((5, 5), np.uint8)), (0, 0), 2)
    a = (Zs*(1 - m)*(1 - mov))[..., None]
    p.stdin.write(np.clip(f*(1 - a) + cl*a, 0, 255).astype(np.uint8).tobytes()); i += 1
p.stdin.close(); p.wait()
