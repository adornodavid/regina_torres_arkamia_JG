# Sustituye el letrero (LUCERNA -> ALBORADAS) en la salida cruda de Genjutsu: cámara fija, se pega solo la caja de letras
# con borde suave y se respeta todo lo que se mueva por encima (brazo de Regina) comparando contra el cuadro 0.
import sys, cv2, numpy as np, subprocess
src, patch_png, out = sys.argv[1:4]
X, Y, PW, PH = 70, 470, 200, 160                    # recorte usado para la edición
BX0, BY0, BX1, BY1 = 38, 64, 166, 108                # caja de letras dentro del recorte
cap = cv2.VideoCapture(src); fps = cap.get(5); W, H = int(cap.get(3)), int(cap.get(4))
patch = cv2.resize(cv2.imread(patch_png), (PW, PH), interpolation=cv2.INTER_AREA).astype(np.float32)
m = np.zeros((PH, PW), np.float32); m[BY0:BY1, BX0:BX1] = 1; m = cv2.GaussianBlur(m, (0, 0), 4)
ok, f0 = cap.read(); cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
ref = f0[Y:Y+PH, X:X+PW].astype(np.float32)
p = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-i',src,
    '-map','0:v','-map','1:a?','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-c:a','copy',out], stdin=subprocess.PIPE)
while True:
    ok, f = cap.read()
    if not ok: break
    roi = f[Y:Y+PH, X:X+PW].astype(np.float32)
    moved = (np.abs(roi - ref).max(2) > 40).astype(np.float32)          # algo pasa por encima del muro
    moved = cv2.GaussianBlur(cv2.dilate(moved, np.ones((7, 7))), (0, 0), 3)
    a = (m * (1 - np.clip(moved * 2, 0, 1)))[..., None]
    # conserva la variación de luz del cuadro (grano/flicker) sumando la diferencia contra el cuadro 0
    f[Y:Y+PH, X:X+PW] = np.clip(roi * (1 - a) + (patch + (roi - ref)) * a, 0, 255).astype(np.uint8)
    p.stdin.write(f.tobytes())
p.stdin.close(); p.wait(); print('ok', out)
