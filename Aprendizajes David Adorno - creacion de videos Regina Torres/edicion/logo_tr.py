# Cierre: logo "terra regia" animado sobre el verde de marca #19815C. Cada letra sube desde su línea base (máscara)
# con un rebote suave y escalonado, luego la "t" y la "g" quedan, y todo hace un push muy lento. 1080x1920, 3 s.
import cv2, numpy as np, subprocess, os
from PIL import Image
FF = 'ffmpeg'; W, H, FPS, L = 1080, 1920, 30, 2.6
GREEN = np.array([92, 129, 25], np.float32)        # BGR de #19815C
lg = Image.open('/Users/davidadorno/Proyectos/terraregia-ads-proyectos/public/logos/TR_white.png').convert('RGBA'); lg = lg.crop(lg.getbbox())
LW = 760; LH = int(lg.height*LW/lg.width); A = np.asarray(lg.resize((LW, LH), Image.LANCZOS))[..., 3].astype(np.float32)/255
X0, Y0 = (W - LW)//2, (H - LH)//2
# letras = componentes conectados por columnas (la "i" tiene punto: se agrupa por solapamiento horizontal)
n, lab, st, _ = cv2.connectedComponentsWithStats((A > .5).astype(np.uint8))
comps = sorted([(st[i, 0], st[i, 0] + st[i, 2], i) for i in range(1, n) if st[i, 4] > 30])
groups = []
for x0, x1, i in comps:
    if groups and x0 < groups[-1][1] - 2: groups[-1][1] = max(groups[-1][1], x1); groups[-1][2].append(i)
    else: groups.append([x0, x1, [i]])
print('letras', len(groups))
masks = []
for x0, x1, ids in groups:
    m = np.zeros_like(A)
    for i in ids: m[lab == i] = 1
    m = cv2.dilate(m, np.ones((3, 3), np.uint8)); masks.append(A*m)
def back(p, c=1.4):
    p = min(max(p, 0), 1); return 1 + (c + 1)*(p - 1)**3 + c*(p - 1)**2
ease = lambda p: 1 - (1 - min(max(p, 0), 1))**3
p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-shortest',
                      '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', '-c:a', 'aac', 's10.mp4'], stdin=subprocess.PIPE)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
for f in range(int(L*FPS)):
    t = f/FPS
    layer = np.zeros((LH + 200, LW), np.float32)
    for k, m in enumerate(masks):
        u = back((t - .15 - .055*k)/.45)
        dy = int(round((1 - u)*LH*1.05))                    # sube desde abajo de la línea base
        sh = np.zeros_like(layer); sh[100 + dy:100 + dy + LH] = m[:min(LH, LH + 200 - 100 - dy)] if dy < LH + 100 else 0
        layer = np.maximum(layer, sh)
    layer[100 + LH:] = 0                                   # máscara: nada por debajo de la línea base
    canvas = np.zeros((H, W), np.float32); canvas[Y0 - 100:Y0 + LH + 100, X0:X0 + LW] = layer
    z = 1 + .035*ease(t/L) + .04*(1 - ease(t/.5))          # push lento
    Mz = cv2.getRotationMatrix2D((W/2, H/2), 0, z); canvas = cv2.warpAffine(canvas, Mz, (W, H))
    bg = np.ones((H, W, 3), np.float32)*GREEN
    vig = 1 - .10*np.clip(np.sqrt(((xx - W/2)/(W/2))**2 + ((yy - H/2)/(H/2))**2) - .3, 0, 1)
    bg *= vig[..., None]
    fade = ease(t/.18)
    img = bg*(1 - canvas[..., None]) + 255*canvas[..., None]
    img = img*fade + bg*(1 - fade)
    p.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
