# Edición estilo @kelssie3 — reel ALBORADAS (adaptado del render.py de Javier, reel Montessa).
# Par tipográfico Light chico + Bold grande encimados, palabra por palabra a la altura del pecho, título enorme DETRÁS
# de la cabeza (matte de Vision), palabra clave en degradado pastel, píldoras de vidrio que hacen pop, punch-ins en
# palabras clave y whips con speed ramp entre tomas.
# Uso: python3 render.py [salida.mp4] [t_ini t_fin]   (desde edicion_kelssie/work)
import sys, os, numpy as np, cv2, subprocess
from PIL import Image, ImageDraw, ImageFont
FF = 'ffmpeg'; W, H, FPS = 1080, 1920, 30
OUT = sys.argv[1] if len(sys.argv) > 1 else 'video_sin_audio.mp4'
RANGE = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else None
HN = '/System/Library/Fonts/HelveticaNeue.ttc'; HN_IDX = {'Light': 7, 'Bold': 1, 'Medium': 10}
FONTS = {'s': ('Light', 62, -0.02), 'b': ('Bold', 112, -0.05), 'g': ('Bold', 112, -0.05), 'y': ('Bold', 96, -0.04), 'sd': ('Light', 62, -0.02), 'bd': ('Bold', 112, -0.05), 'gd': ('Bold', 112, -0.05), 'T': ('Bold', 280, -0.05),
         'TG': ('Bold', 280, -0.06), 'TD': ('Bold', 280, -0.06), 'p': ('Medium', 52, -0.02)}
_fc = {}
def font(k):
    w, sz, _ = FONTS[k]
    if k not in _fc: _fc[k] = ImageFont.truetype(HN, sz, index=HN_IDX[w])
    return _fc[k]
GRAD = [(193, 230, 252), (160, 196, 245), (120, 150, 226)]   # BGR: crema → durazno → terracota (paleta Alboradas)
_sc = {}
def sprite(text, k):
    """RGBA float (0-1) con el texto y la posición de su línea base."""
    if (text, k) in _sc: return _sc[(text, k)]
    f = font(k); tr = FONTS[k][2]*FONTS[k][1]; asc, desc = f.getmetrics(); pad = 40
    adv = [f.getlength(c) + tr for c in text]; w = int(sum(adv) - tr) + 2*pad; h = asc + desc + 2*pad
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m); x = pad
    for c, a in zip(text, adv): d.text((x, pad), c, font=f, fill=255); x += a
    a = np.asarray(m, np.float32)/255
    if k in ('g', 'TG', 'y'):
        u = np.linspace(0, 1, w)[None, :, None]; c0, c1, c2 = (np.array(g, np.float32)/255 for g in GRAD)
        col = np.where(u < .5, c0 + (c1-c0)*u*2, c1 + (c2-c1)*(u-.5)*2) * np.ones((h, 1, 1))
    elif k in ('TD', 'sd', 'bd'): col = np.ones((h, w, 3), np.float32)*np.array([48, 46, 46], np.float32)/255
    elif k == 'gd': col = np.ones((h, w, 3), np.float32)*np.array([49, 53, 118], np.float32)/255   # vino Alboradas (BGR)   # gris oscuro sobre fondos claros (como 'FIRST' de Kelssie)
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

