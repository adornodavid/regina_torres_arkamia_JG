# Toma 3 (Alboradas): lote de 10 x 20 m dibujado sobre el terreno real del dron, pegado al suelo por homografía.
# Textos planos en pantalla (regla de Javier): «200 m²» + «10 m de frente» + «20 m de fondo», con línea al lote.
# Uso: python lote_t3.py dron46_t3.mp4 voz.wav salida.mp4      (tiempos de palabras de T3a)
import sys, cv2, numpy as np, subprocess
from PIL import Image, ImageDraw, ImageFont

src, voz, out = sys.argv[1:4]
W, H, FPS = 1080, 1920, 30
DUR = 6.95
REF_T = 4.0                                   # cuadro de referencia donde se definió el lote
# lote en el cuadro de referencia (frente abajo, fondo hacia la montaña)
Q = np.float32([[296, 952], [380, 944], [366, 874], [288, 880]])   # FL, FR, BR, BL
T_DRAW, T_200, T_10, T_20 = 2.05, 2.80, 4.58, 5.90                 # «terrenos», «doscientos», «diez», «veinte»
CREMA = (252, 230, 193); VINO = (118, 53, 49)

HN = '/System/Library/Fonts/HelveticaNeue.ttc'
f_big = ImageFont.truetype(HN, 150, index=1); f_sup = ImageFont.truetype(HN, 70, index=1)
f_small = ImageFont.truetype(HN, 62, index=10)
ease = lambda p: 1 - (1 - min(max(p, 0), 1)) ** 3

cap = cv2.VideoCapture(src); sfps = cap.get(5)
frames = []
while len(frames) < int(DUR * sfps) + 2:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
ref = frames[min(int(REF_T * sfps), len(frames) - 1)]
sift = cv2.SIFT_create(4000)
mask = np.zeros((H, W), np.uint8); mask[700:] = 255          # solo suelo (la montaña también es fija, pero el suelo manda)
gref = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY); kr, dr = sift.detectAndCompute(gref, mask)
bf = cv2.BFMatcher()

def homog(f):
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY); k, d = sift.detectAndCompute(g, mask)
    m = [a for a, b in bf.knnMatch(dr, d, k=2) if a.distance < 0.75 * b.distance]
    Hm, _ = cv2.findHomography(np.float32([kr[x.queryIdx].pt for x in m]), np.float32([k[x.trainIdx].pt for x in m]), cv2.RANSAC, 3.0)
    return Hm

Hs = [homog(f) for f in frames]
# suavizado temporal de las esquinas proyectadas (quita el temblor del tracking)
P = np.array([cv2.perspectiveTransform(Q[None], Hm)[0] for Hm in Hs])
k = np.ones(5) / 5
Ps = np.stack([np.stack([np.convolve(np.pad(P[:, i, j], 2, mode='edge'), k, 'valid') for j in range(2)], -1) for i in range(4)], 1)

def text_layer(t, q):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    cx, cy = q.mean(0)
    a = ease((t - T_200) / 0.35)
    if a > 0:
        # bloque de texto arriba a la derecha + línea al lote
        tx, ty = 560, 520
        d.line([(cx, cy - 20), (cx, ty + 230), (tx - 30, ty + 230)], fill=(255, 255, 255, int(220 * a)), width=4)
        d.ellipse([cx - 9, cy - 29, cx + 9, cy - 11], fill=(255, 255, 255, int(255 * a)))
        y = ty + (1 - a) * 30
        d.text((tx, y + 40), '200', font=f_big, fill=(255, 255, 255, int(255 * a)))
        w = d.textlength('200', font=f_big)
        d.text((tx + w + 10, y + 70), 'm²', font=f_sup, fill=CREMA + (int(255 * a),))
    for tt, txt, dy in ((T_10, '10 m de frente', 250), (T_20, '20 m de fondo', 330)):
        b = ease((t - tt) / 0.3)
        if b > 0:
            d.text((560, 520 + dy + (1 - b) * 20), txt, font=f_small, fill=(255, 255, 255, int(240 * b)))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh.putalpha(L.getchannel('A').point(lambda v: int(v * 0.55)))
    from PIL import ImageFilter
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    return Image.alpha_composite(sh, L)

def lote_layer(t, q):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    p = ease((t - T_DRAW) / 0.9)
    if p <= 0: return L
    pts = [tuple(x) for x in q] + [tuple(q[0])]
    seg = [np.hypot(*(np.subtract(pts[i + 1], pts[i]))) for i in range(4)]; tot = sum(seg); run = p * tot
    fill_a = ease((t - T_DRAW - 0.6) / 0.5)
    if fill_a > 0: d.polygon([tuple(x) for x in q], fill=CREMA + (int(110 * fill_a),))
    for i in range(4):
        if run <= 0: break
        f = min(run / seg[i], 1); a, b = np.array(pts[i]), np.array(pts[i + 1])
        d.line([tuple(a), tuple(a + (b - a) * f)], fill=(255, 255, 255, 255), width=5); run -= seg[i]
    # resalta el lado del frente / fondo cuando se nombran
    if t >= T_10: d.line([pts[0], pts[1]], fill=VINO + (255,), width=8)
    if t >= T_20: d.line([pts[1], pts[2]], fill=VINO + (255,), width=8)
    return L

p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-i', voz, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out],
                     stdin=subprocess.PIPE)
for n in range(int(DUR * FPS)):
    t = n / FPS; i = min(int(t * sfps), len(frames) - 1)
    base = Image.fromarray(cv2.cvtColor(frames[i], cv2.COLOR_BGR2RGB)).convert('RGBA')
    q = Ps[i]
    base = Image.alpha_composite(base, lote_layer(t, q))
    base = Image.alpha_composite(base, text_layer(t, q))
    p.stdin.write(np.asarray(base.convert('RGB')).tobytes())
p.stdin.close(); p.wait()
print('ok', out)
