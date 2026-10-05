# Limpia la entrada para Genjutsu: borra el micrófono de solapa y oscurece los puños claros de los jeans
# (motion_control copia ambos a Regina). Uso: python3 fix_wardrobe.py in.mp4 out.mp4  |  --frame in.png out.png
import cv2, numpy as np, subprocess, sys, os
def fix(f):
    H, W = f.shape[:2]; hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV); h, s, v = cv2.split(hsv)
    # micrófono: pixel oscuro y neutro rodeado de tela blanca, en la franja del torso
    white = ((s < 45) & (v > 165)).astype(np.uint8)*255
    near_white = cv2.dilate(white, np.ones((41,41), np.uint8))
    dark = (((v < 120) & (s < 80)) | (v < 70)).astype(np.uint8)*255
    m = cv2.bitwise_and(dark, near_white); m[:int(H*.30)] = 0; m[int(H*.55):] = 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    keep = np.zeros_like(m)
    for k in range(1, n):
        x, y, w, hh, a = st[k]
        lim = (25000, 220) if os.environ.get('MEDIO') else (4000, 90)
        if 40 < a < lim[0] and w < lim[1] and hh < lim[1]:   # blob compacto = mic (no el cabello)
            keep[lab == k] = 255
    keep = cv2.dilate(keep, np.ones((25,25) if os.environ.get('MEDIO') else (9,9), np.uint8))
    if keep.any(): f = cv2.inpaint(f, keep, 9, cv2.INPAINT_TELEA)
    # puños de mezclilla clara -> mismo tono oscuro del pantalón
    cuff = ((h > 84) & (h < 135) & (s > 12) & (v > 38) & (v < 220)).astype(np.uint8)*255
    cuff[:int(H*.78)] = 0
    if os.environ.get('MEDIO'): cuff[:] = 0
    cuff = cv2.GaussianBlur(cuff, (7,7), 0).astype(np.float32)[...,None]/255
    dark_jean = np.array([14, 10, 8], np.float32)  # BGR del pantalón
    f = (f.astype(np.float32)*(1-cuff) + (dark_jean + (f.astype(np.float32)-f.mean())*0.0)*cuff).clip(0,255).astype(np.uint8)
    if not os.environ.get('MEDIO'): f = pantalon(f)
    return f
def pantalon(f):
    # alarga la pierna del pantalón: estira la tela real de arriba del puño hasta la punta del zapato (sin puños)
    H, W = f.shape[:2]; hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    fg = 255 - cv2.inRange(hsv, (38,110,90), (85,255,255)); ys = np.where(fg.any(1))[0]
    if not len(ys): return f
    yb = ys.max(); y0 = int(yb - H*.068); yt = y0 - int(H*.085); yh = int(yb - H*.014)
    xs = np.where(fg[y0] > 0)[0]
    if len(xs) < 20: return f
    xa, xb = max(xs.min()-25, 0), min(xs.max()+25, W-1)
    out = f.copy(); G = np.array([64,177,0], np.float32)
    rows = np.arange(yt, yh+1); src = yt + (rows - yt) * (y0 - yt) / (yh - yt)
    mapy = np.repeat(src[:,None], xb-xa+1, 1).astype(np.float32); mapx = np.repeat(np.arange(xa, xb+1)[None,:], len(rows), 0).astype(np.float32)
    patch = cv2.remap(f, mapx, mapy, cv2.INTER_LINEAR); pm = cv2.remap(fg, mapx, mapy, cv2.INTER_LINEAR).astype(np.float32)[...,None]/255
    patch = patch.astype(np.float32)*pm + G*(1-pm)
    # oscurece un poco hacia la bastilla y mezcla suave en el arranque
    patch *= np.linspace(1.0, 0.85, len(rows))[:,None,None]**np.where(pm > .5, 1, 0)
    w = np.clip((rows - yt) / max(int(H*.02),1), 0, 1)[:,None,None]
    region = out[yt:yh+1, xa:xb+1].astype(np.float32)
    out[yt:yh+1, xa:xb+1] = (region*(1-w) + patch*w).clip(0,255).astype(np.uint8)
    return out
if sys.argv[1] == '--frame':
    cv2.imwrite(sys.argv[3], fix(cv2.imread(sys.argv[2]))); sys.exit()
FF = os.path.expanduser('~/arkamia-reels/bin/ffmpeg'); src, dst = sys.argv[1], sys.argv[2]
cap = cv2.VideoCapture(src); fps = cap.get(5); W, H = int(cap.get(3)), int(cap.get(4))
p = subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-i',src,
    '-map','0:v','-map','1:a','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-c:a','copy',dst], stdin=subprocess.PIPE)
while True:
    ok, f = cap.read()
    if not ok: break
    p.stdin.write(fix(f).tobytes())
p.stdin.close(); p.wait()
