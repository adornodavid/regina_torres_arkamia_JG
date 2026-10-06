# Edición estilo @kelssie3 sobre las 5 tomas de Regina (Terra Regia).
# Par tipográfico Light chico + Bold grande encimados, palabra por palabra a la altura del pecho, título enorme DETRÁS
# de la cabeza (matte de Vision), palabra clave en degradado pastel, píldoras de vidrio que hacen pop, punch-ins en
# palabras clave y whips con speed ramp entre tomas.
# Uso: python3 render.py [salida.mp4] [t_ini t_fin]   (desde edicion_kelssie/work)
import sys, os, numpy as np, cv2, subprocess
from PIL import Image, ImageDraw, ImageFont
FF = os.path.expanduser('~/arkamia-reels/bin/ffmpeg'); W, H, FPS = 1080, 1920, 30
OUT = sys.argv[1] if len(sys.argv) > 1 else 'video_sin_audio.mp4'
RANGE = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else None
FD = '/Library/Fonts/' if os.path.exists('/Library/Fonts/SF-Pro-Display-Bold.otf') else os.path.expanduser('~/Library/Fonts/')
FONTS = {'s': ('Light', 62, -0.02), 'b': ('Bold', 112, -0.06), 'g': ('Bold', 112, -0.06), 'T': ('Bold', 280, -0.06),
         'TG': ('Bold', 280, -0.06), 'TD': ('Bold', 280, -0.06), 'p': ('Medium', 52, -0.02)}
_fc = {}
def font(k):
    w, sz, _ = FONTS[k]
    if k not in _fc: _fc[k] = ImageFont.truetype(f'{FD}SF-Pro-Display-{w}.otf', sz)
    return _fc[k]
GRAD = [(214, 196, 255), (184, 201, 255), (243, 198, 232)]   # lila → periwinkle → rosa (Kelssie)
_sc = {}
def sprite(text, k):
    """RGBA float (0-1) con el texto y la posición de su línea base."""
    if (text, k) in _sc: return _sc[(text, k)]
    f = font(k); tr = FONTS[k][2]*FONTS[k][1]; asc, desc = f.getmetrics(); pad = 40
    adv = [f.getlength(c) + tr for c in text]; w = int(sum(adv) - tr) + 2*pad; h = asc + desc + 2*pad
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m); x = pad
    for c, a in zip(text, adv): d.text((x, pad), c, font=f, fill=255); x += a
    a = np.asarray(m, np.float32)/255
    if k in ('g', 'TG'):
        u = np.linspace(0, 1, w)[None, :, None]; c0, c1, c2 = (np.array(g, np.float32)/255 for g in GRAD)
        col = np.where(u < .5, c0 + (c1-c0)*u*2, c1 + (c2-c1)*(u-.5)*2) * np.ones((h, 1, 1))
    elif k == 'TD': col = np.ones((h, w, 3), np.float32)*np.array([60, 58, 58], np.float32)/255   # gris oscuro sobre fondos claros (como 'FIRST' de Kelssie)
    else: col = np.ones((h, w, 3), np.float32)
    s = (np.dstack([col, a]), pad + asc, pad, int(sum(adv) - tr)); _sc[(text, k)] = s; return s
def blit(img, spr, cx, by, alpha=1., scale=1., blur=0., shadow=.32, left=None):
    """Pega el sprite centrado en cx (o desde left) con su línea base en by."""
    rgba, base, pad, tw = spr
    if alpha <= 0.003: return
    if scale != 1: rgba = cv2.resize(rgba, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    if blur > .3: rgba = cv2.GaussianBlur(rgba, (0, 0), blur)
    h, w = rgba.shape[:2]; x0 = int(round((cx - w/2) if left is None else (left - pad*scale))); y0 = int(round(by - base*scale))
    a = rgba[..., 3:]*alpha
    if shadow:
        sh = cv2.GaussianBlur(rgba[..., 3], (0, 0), 7)[..., None]*shadow*alpha
        _over(img, np.zeros_like(rgba[..., :3]), sh, x0, y0 + 4)
    _over(img, rgba[..., :3], a, x0, y0)
def _over(img, col, a, x0, y0):
    h, w = a.shape[:2]; X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if X1 <= X0 or Y1 <= Y0: return
    c = col[Y0-y0:Y1-y0, X0-x0:X1-x0]; aa = a[Y0-y0:Y1-y0, X0-x0:X1-x0]
    img[Y0:Y1, X0:X1] = img[Y0:Y1, X0:X1]*(1-aa) + c*aa
ease = lambda p: 1 - (1 - min(max(p, 0), 1))**3
def back(p):
    p = min(max(p, 0), 1); c = 1.9; return 1 + (c + 1)*(p - 1)**3 + c*(p - 1)**2

# ---------------- guion (tiempos locales de cada toma, medidos con faster-whisper) ----------------
# chunk: (fin, [[(palabra, t, estilo), ...], ...])  estilo s=Light chico, b=Bold grande, g=Bold degradado
# title: (t_ini, t_fin, texto, estilo)  → detrás de la cabeza
SEG = [
 dict(n=1, a=0.20, b=4.35, punch=[], chunks=[
   (1.62, [[('¿Quieres', .29, 's'), ('comprar', .70, 's')], [('tu', .96, 'b'), ('terreno?', 1.10, 'b')]]),
   (2.70, [[('pero', 1.64, 's'), ('todavía', 1.72, 's'), ('no', 1.98, 's'), ('sabes', 2.20, 's'), ('si', 2.42, 's')]]),
   (3.66, [[('o', 3.18, 's')]])],
   titles=[(2.72, 3.66, 'construir', 'T'), (3.68, 9, 'invertir?', 'TG')]),
 dict(n=2, a=0.00, b=3.22, punch=[.68], chunks=[
   (1.06, [[('Conoce', .05, 's')]]),
   (9, [[('Residencial', 1.08, 's'), ('en', 1.76, 's')], [('Dominio', 2.28, 'g'), ('Cumbres', 2.60, 'g')]])],
   titles=[(.68, 9, 'Montessa', 'T')]),
 dict(n=3, a=0.05, b=6.92, punch=[], center=(.5, .53), chunks=[
   (1.50, [[('Aquí', .05, 's'), ('encuentras', .52, 's')], [('terrenos', .98, 'b')]]),
   (5.62, [[('una', 4.24, 's'), ('zona', 4.36, 's'), ('que', 4.66, 's')], [('sigue', 4.90, 'b'), ('creciendo', 5.12, 'g')]])],
   titles=[]),
 dict(n=4, a=0.05, b=7.55, punch=[2.34], chunks=[
   (2.32, [[('tienes', 1.10, 's'), ('acceso', 1.22, 's')], [('controlado', 1.54, 'b')]])],
   titles=[(.08, 1.08, 'Además,', 'T')],
   pills=[(2.34, '3 parques', .20, .40), (3.80, 'Casa club', .77, .44), (4.72, 'Canchas', .19, .50),
          (5.50, 'Pet parks', .79, .54), (6.10, 'Asadores', .20, .60), (6.82, 'Áreas verdes', .76, .64)]),
 dict(n=5, a=0.05, b=3.45, punch=[2.72], chunks=[
   (1.15, [[('Puedes', .15, 's'), ('comprar', .46, 's')], [('tu', .68, 'b'), ('terreno', .86, 'b')]]),
   (1.76, [[('para', 1.16, 's')], [('construir', 1.42, 'b')]]),
   (9, [[('más', 2.30, 's')], [('adelante.', 2.72, 'g')]])],
   titles=[(1.78, 9, 'tu casa', 'T')]),
 dict(n=6, a=0.10, b=4.55, punch=[], center=(.5, .62), chunks=[
   (1.02, [[('O,', .17, 's')], [('consérvalo', .54, 'b')]]),
   (2.38, [[('como', 1.04, 's'), ('parte', 1.22, 's'), ('de', 1.44, 's')], [('tu', 1.54, 'g'), ('patrimonio', 1.66, 'g')]]),
   (9, [[('mientras', 2.40, 's'), ('la', 2.82, 's'), ('zona', 3.02, 's')], [('continúa', 3.18, 'b')], [('desarrollándose.', 3.70, 'g')]])],
   titles=[]),
 dict(n=7, a=0.05, b=3.62, punch=[1.80], center=(.5, .80), tpos=(.5, .445, 170), chunks=[
   (1.78, [[('Pregunta', .15, 's'), ('también', .56, 's'), ('por', .88, 's'), ('las', 1.06, 's')], [('opciones', 1.20, 'b'), ('de', 1.54, 'b')]]),
   (9, [[('directo', 2.26, 'b')], [('con', 2.62, 's')], [('terra regia', 2.86, 'g')]])],
   titles=[(1.80, 9, 'financiamiento', 'TD')]),
 dict(n=8, a=0.38, b=3.90, hold=.45, punch=[1.10, 3.24], center=(.5, .62), chunks=[
   (1.08, [[('Ven', .42, 's'), ('a', .70, 's'), ('conocer', .86, 's')]]),
   (2.92, [[('y', 1.66, 's'), ('encuentra', 1.96, 's'), ('el', 2.18, 's')], [('terreno', 2.34, 'b'), ('ideal', 2.60, 'g')]]),
   (9, [[('para', 2.94, 's')]])],
   titles=[(1.10, 1.94, 'Montessa', 'T'), (3.24, 9, 'tus planes', 'TG')]),
]
WHIP = 4      # cuadros de whip a cada lado del corte
# ---------------- fuentes ----------------
def load_face(n):
    a = np.array([[float(x) for x in l.split()] for l in open(f'face{n}.txt') if l[0].isdigit()])
    ok = a[:, 1] >= 0
    for c in (1, 2, 3): a[~ok, c] = np.interp(np.flatnonzero(~ok), np.flatnonzero(ok), a[ok, c])
    k = np.ones(15)/15
    return np.stack([np.convolve(np.pad(a[:, c], 7, mode='edge'), k, 'valid') for c in (1, 2, 3)], 1)
for s in SEG:
    cap = cv2.VideoCapture(f"s{s['n']}.mp4"); fr = []
    while True:
        r, f = cap.read()
        if not r: break
        fr.append(f)
    s['frames'] = fr
    s['face'] = load_face(s['n']) if os.path.exists(f"face{s['n']}.txt") else None
    s['matte'] = f"matte{s['n']}" if os.path.isdir(f"matte{s['n']}") else None
    s['len'] = (s['b'] - s['a']) + s.get('hold', 0)
t0 = 0
for s in SEG: s['T0'] = t0; t0 += s['len']
TOTAL = t0; NF = int(round(TOTAL*FPS))
print(f'duración {TOTAL:.2f} s, {NF} cuadros', flush=True)
open('timeline.txt', 'w').write('\n'.join(f"{s['n']} {s['T0']:.4f} {s['a']} {s['b']} {s.get('hold', 0)}" for s in SEG))

def src_index(s, lt, nf_left):
    """Índice de cuadro fuente; en los últimos cuadros de la toma acelera (speed ramp hacia el whip)."""
    t = s['a'] + min(lt, s['b'] - s['a'])
    if nf_left < 6 and s is not SEG[-1]:
        t += sum(.5*k/FPS for k in range(6 - nf_left))   # 1x → 3.5x
    return min(int(round(t*FPS)), len(s['frames']) - 1)
def zoom_at(s, lt):
    z = 1.
    for tp in s['punch']: z += .065*ease((lt + s['a'] - tp)/.14)
    return z
def matte(s, i):
    if not s['matte']: return None
    p = f"{s['matte']}/m_{min(i, len(os.listdir(s['matte'])) - 1):05d}.png"
    m = cv2.imread(p, 0); m = cv2.resize(m, (W, H)) if m.shape != (H, W) else m
    return m.astype(np.float32)/255

def draw_chunks(img, s, lt, ax, ay):
    tl = lt + s['a']; prev_end = -1
    for end, lines in s['chunks']:
        t_start = min(w[1] for L in lines for w in L)
        if not (t_start - .01 <= tl < end): continue
        fade = ease((end - tl)/.07)
        # layout: líneas encimadas, centradas en (ax, ay)
        rows = []
        for L in lines:
            sp = [sprite(w, k) for w, _, k in L]; gap = font(L[0][2]).getlength(' ')*.75
            width = sum(x[3] for x in sp) + gap*(len(sp) - 1); rows.append((L, sp, gap, width))
        bases = []; y = 0
        for i, (L, sp, gap, wd) in enumerate(rows):
            asc = font(L[0][2]).getmetrics()[0]
            if i: y += asc*(.80 if L[0][2] != 's' else .95)
            bases.append(y)
        top = bases[0] - font(rows[0][0][0][2]).getmetrics()[0]*.7; mid = (top + bases[-1])/2
        for (L, sp, gap, wd), by in zip(rows, bases):
            x = ax - wd/2
            for (w, tw, k), spr in zip(L, sp):
                e = ease((tl - tw)/.16)
                if tl >= tw - .001:
                    blit(img, spr, 0, ay + by - mid + 16*(1 - e), alpha=e*fade, scale=1, blur=5*(1 - e), left=x, shadow=.5)
                x += spr[3] + gap
def draw_titles(img, s, lt, fx, fy, fh):
    tl = lt + s['a']
    for a, b, txt, k in s['titles']:
        if not (a <= tl < b): continue
        spr = sprite(txt, k); cap = .72*FONTS[k][1]; e = ease((tl - a)/.28); fade = ease((b - tl)/.1)
        if 'tpos' in s:                      # varias personas: posición fija (x, línea base, alto de mayúscula en px)
            tx, tb, tcap = s['tpos']; sc = min(tcap/cap, 980/spr[3]); tw = spr[3]*sc
            cx = np.clip(tx*W, 50 + tw/2, W - 50 - tw/2); by = tb*H + 34*(1 - e)
        else:
            sc = min(np.clip(1.25*fh, 150, 250)/cap, 980/spr[3])
            tw = spr[3]*sc; cx = np.clip(fx, 50 + tw/2, W - 50 - tw/2)
            by = fy + fh*.42 + 34*(1 - e)    # línea base a la altura de los ojos: la cabeza tapa la parte baja del título
        blit(img, spr, cx, by, alpha=e*fade*.96, scale=sc*(1.06 - .06*e), blur=9*(1 - e), shadow=.22)
def draw_pills(img, s, lt, src_img):
    tl = lt + s['a']
    for tp, txt, px, py in s.get('pills', []):
        if tl < tp: continue
        p = (tl - tp)/.30; sc = back(p) if p < 1 else 1.; al = min(1, p*3)
        spr = sprite(txt, 'p'); pw, ph = int((spr[3] + 76)*sc), int(108*sc)
        if pw < 8: continue
        cx, cy = px*W, py*H; x0, y0 = int(cx - pw/2), int(cy - ph/2)
        X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(x0 + pw, W), min(y0 + ph, H)
        if X1 <= X0 or Y1 <= Y0: continue
        reg = cv2.GaussianBlur(src_img[max(Y0-40, 0):min(Y1+40, H), max(X0-40, 0):min(X1+40, W)], (0, 0), 16)
        reg = reg[Y0 - max(Y0-40, 0):Y0 - max(Y0-40, 0) + (Y1 - Y0), X0 - max(X0-40, 0):X0 - max(X0-40, 0) + (X1 - X0)]
        glass = reg*.72 + .28                                   # vidrio esmerilado claro
        m = np.zeros((ph, pw), np.uint8); r = ph//2
        cv2.rectangle(m, (r, 0), (pw - r, ph - 1), 255, -1); cv2.circle(m, (r, r), r, 255, -1); cv2.circle(m, (pw - r, r), r, 255, -1)
        m = cv2.GaussianBlur(m, (0, 0), 1.0).astype(np.float32)/255
        edge = np.clip(m - cv2.erode(m, np.ones((5, 5), np.uint8)), 0, 1)
        mm = m[Y0-y0:Y1-y0, X0-x0:X1-x0][..., None]*al; ee = edge[Y0-y0:Y1-y0, X0-x0:X1-x0][..., None]*al*.6
        sh = cv2.GaussianBlur(m, (0, 0), 10)[Y0-y0:Y1-y0, X0-x0:X1-x0][..., None]*al*.18
        img[Y0:Y1, X0:X1] = img[Y0:Y1, X0:X1]*(1 - sh)
        img[Y0:Y1, X0:X1] = img[Y0:Y1, X0:X1]*(1 - mm) + glass*mm
        img[Y0:Y1, X0:X1] = img[Y0:Y1, X0:X1]*(1 - ee) + ee
        blit(img, spr, cx, cy + 18*sc, alpha=al, scale=sc, shadow=.25)

def whip(img, k, direction):
    """k: 0..1 intensidad; desplaza y barre horizontal (whip pan)."""
    if k <= 0: return img
    dx = direction*k*W*.35; M = np.float32([[1, 0, dx], [0, 1, 0]])
    o = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    L = int(8 + 220*k)
    return cv2.blur(o, (L, 1))

p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
fr_range = range(NF) if not RANGE else range(int(RANGE[0]*FPS), int(RANGE[1]*FPS))
for fi in fr_range:
    T = fi/FPS; si = max(i for i, s in enumerate(SEG) if s['T0'] <= T + 1e-6); s = SEG[si]; lt = T - s['T0']
    nf_left = int(round((s['T0'] + s['len'] - T)*FPS)) - 1
    idx = src_index(s, lt, nf_left)
    base = s['frames'][idx].astype(np.float32)/255; m = matte(s, idx)
    z = zoom_at(s, lt)
    if s['face'] is not None:
        f = s['face'][min(idx, len(s['face']) - 1)]; fx, fy, fh = f[0]*W, f[1]*H, f[2]*H
    else: fx, fy, fh = W/2, H*.3, H*.1
    if z != 1:
        M = cv2.getRotationMatrix2D((fx, fy), 0, z)
        base = cv2.warpAffine(base, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if m is not None: m = cv2.warpAffine(m, M, (W, H), flags=cv2.INTER_LINEAR)
        fh *= z
    img = base.copy()
    # 1) títulos detrás de la cabeza
    if s['titles']:
        draw_titles(img, s, lt, fx, fy - fh/2, fh)
        if m is not None: img = img*(1 - m[..., None]) + base*m[..., None]
    # 2) subtítulo a la altura del pecho (o al centro en el drone)
    if 'center' in s: ax, ay = s['center'][0]*W, s['center'][1]*H
    else: ax, ay = fx, fy + fh*(2.6 if fh < .09*H else 2.25)
    draw_chunks(img, s, lt, ax, ay)
    draw_pills(img, s, lt, base)
    # 3) whip + speed ramp en los cortes
    k = 0; d = 1
    if nf_left < WHIP and si < len(SEG) - 1: k = ease((WHIP - nf_left)/WHIP); d = -1 if si % 2 == 0 else 1
    fin = int(round(lt*FPS))
    if fin < WHIP and si > 0: k = ease((WHIP - fin)/WHIP); d = 1 if (si - 1) % 2 == 0 else -1
    out = whip(np.clip(img*255, 0, 255).astype(np.uint8), k, d)
    p.stdin.write(out.tobytes())
    if fi % 60 == 0: print(f'{T:5.1f}s', flush=True)
p.stdin.close(); p.wait()
