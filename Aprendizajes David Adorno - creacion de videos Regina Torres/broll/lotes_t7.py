# Toma 7 (Alboradas): «Alboradas cuenta con 319 terrenos residenciales».
# Render Máster aéreo (lotificación real) en 9:16 con paneo lento; la superficie de lotes se enciende en ola
# desde el acceso (tinte crema + borde vino) mientras el contador sube a 319. Las líneas blancas del render
# marcan cada lote. Uso: python lotes_t7.py master_aereo_4k.png voz.wav salida.mp4
import sys, cv2, numpy as np, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

src, voz, out = sys.argv[1:4]
OW, OH, FPS, DUR = 1080, 1920, 30, 4.45
T0, T1 = 0.55, 3.25                                # «trescientos diecinueve» llega a 319 al terminar la frase
CREMA = np.array([193, 230, 252], np.float32)      # BGR #FCE6C1
VINO = (118, 53, 49)
im = cv2.imread(src).astype(np.float32); H, W = im.shape[:2]
hsv = cv2.cvtColor(im.astype(np.uint8), cv2.COLOR_BGR2HSV); h, s, v = cv2.split(hsv)
lots = ((h >= 25) & (h <= 72) & (s >= 55) & (v >= 45)).astype(np.uint8) * 255
lots = cv2.morphologyEx(lots, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
# solo la mancha grande del desarrollo (fuera queda la sierra)
n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(lots, np.ones((25, 25), np.uint8)))
big = 1 + np.argmax(st[1:, 4]); dev = (lab == big).astype(np.uint8)
# contorno convexo del desarrollo: incluye bloques centrales de verde más apagado
cs, _ = cv2.findContours(dev, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
hull = np.zeros_like(dev); cv2.fillPoly(hull, [cv2.convexHull(max(cs, key=cv2.contourArea))], 1)
hull = cv2.erode(hull, np.ones((15, 15), np.uint8))
loose = (h >= 22) & (h <= 80) & (s >= 35) & (v >= 40)
lots = loose & (hull > 0)
lots = cv2.morphologyEx(lots.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0
dev = hull
white = (s < 60) & (v > 165) & (dev > 0)
lotsf = cv2.GaussianBlur(lots.astype(np.float32), (0, 0), 1.2)
ENT = np.array([2830, 1690], np.float32)           # acceso principal (abajo a la derecha)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
dist = np.hypot(xx - ENT[0], yy - ENT[1]); dist /= dist[lots].max()

HN = '/System/Library/Fonts/HelveticaNeue.ttc'
f_num = ImageFont.truetype(HN, 230, index=1); f_lbl = ImageFont.truetype(HN, 66, index=10)
ease = lambda p: 1 - (1 - min(max(p, 0), 1)) ** 3

# recorte 9:16 que pasea de derecha (acceso) a izquierda, con acercamiento suave
cw0 = int(H * 9 / 16)
def crop_at(t):
    p = ease(t / DUR); z = 1.0 + 0.10 * p
    cw, ch = int(cw0 / z), int(H / z)
    cx = (W - cw0 / 2 - 120) * (1 - p) + (W * 0.42) * p
    x0 = int(np.clip(cx - cw / 2, 0, W - cw)); y0 = int(np.clip(H * 0.52 - ch / 2, 0, H - ch))
    return x0, y0, cw, ch

proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                         '-i', voz, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out],
                        stdin=subprocess.PIPE)
for n in range(int(DUR * FPS)):
    t = n / FPS; x0, y0, cw, ch = crop_at(t)
    sub = im[y0:y0 + ch, x0:x0 + cw]; d = dist[y0:y0 + ch, x0:x0 + cw]; L = lotsf[y0:y0 + ch, x0:x0 + cw]
    wave = ease((t - T0) / (T1 - T0)) * 1.15 if t > T0 else 0                      # frente de la ola (0 → 1.15)
    on = np.clip((wave - d) / 0.06, 0, 1)                   # encendido detrás del frente
    edge = np.exp(-((wave - d) / 0.025) ** 2) * (wave > 0)  # brillo en el frente
    a = (L * (0.62 * on + 0.35 * edge))[..., None]
    fr = sub * (1 - a) + CREMA * a
    eg = (L * edge)[..., None] * 0.55
    fr = fr * (1 - eg) + np.array([49, 53, 118], np.float32) * eg     # frente de la ola en vino
    wl = white[y0:y0 + ch, x0:x0 + cw] & (on > 0.5)         # líneas de lote más blancas una vez encendidas
    fr[wl] = fr[wl] * 0.5 + 255 * 0.5
    fr = cv2.resize(np.clip(fr, 0, 255).astype(np.uint8), (OW, OH), interpolation=cv2.INTER_AREA)
    # contador
    k = int(round(319 * ease((t - T0) / (T1 - T0)))) if t > T0 else 0
    pil = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert('RGBA')
    lay = Image.new('RGBA', (OW, OH)); dr = ImageDraw.Draw(lay)
    al = ease((t - 0.25) / 0.4)
    if al > 0:
        txt = f'{k}'; tw = dr.textlength('319', font=f_num)
        dr.text(((OW - tw) / 2, 330), txt, font=f_num, fill=(255, 255, 255, int(255 * al)))
        lbl = 'terrenos residenciales'; lw = dr.textlength(lbl, font=f_lbl)
        dr.text(((OW - lw) / 2, 585), lbl, font=f_lbl, fill=(255, 255, 255, int(255 * al)))
        sh = Image.new('RGBA', (OW, OH), (0, 0, 0, 0)); sh.putalpha(lay.getchannel('A').point(lambda q: int(q * 0.7)))
        lay = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), lay)
    pil = Image.alpha_composite(pil, lay)
    proc.stdin.write(cv2.cvtColor(np.asarray(pil.convert('RGB')), cv2.COLOR_RGB2BGR).tobytes())
proc.stdin.close(); proc.wait(); print('ok', out)
