# Toma 3 v3 (mezcla Kelssie + estilo regio): pin de ubicación con tracking, subtítulo palabra por palabra, palabra clave en neón, flashes.
# Toma 3 v2: rampa + lote con luz + "desde / 127 m²" (Light+Bold) + casas levantándose en "sigue creciendo" + "Monterrey".
import cv2, numpy as np, subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FF = os.path.expanduser('~/arkamia-reels/bin/ffmpeg'); W, H, FPS, DUR = 1080, 1920, 30, 7.03
FD = os.path.expanduser('~/Library/Fonts/')
BOLD = lambda s: ImageFont.truetype(FD+'Gotham-Bold.otf', s); LIGHT = lambda s: ImageFont.truetype(FD+'Gotham-Light.otf', s)
MED = lambda s: ImageFont.truetype(FD+'Gotham-Medium.otf', s)
ease = lambda x: 0 if x <= 0 else 1 if x >= 1 else 1-(1-x)**3
inout = lambda x: 0 if x <= 0 else 1 if x >= 1 else 0.5-0.5*np.cos(np.pi*x)
T_AB, T_BC = 1.45, 4.70

def reader(path):
    cap = cv2.VideoCapture(path); fr = []
    while True:
        ok, f = cap.read()
        if not ok: break
        fr.append(f)
    return fr, cap.get(5)
A, fa = reader('segA60.mp4');
GA = [cv2.cvtColor(cv2.resize(f, (540,960)), cv2.COLOR_BGR2GRAY) for f in A]; AREF = 323; PIN_REF = np.float32([[[460, 780]]])
def ahom(a, b):
    p_ = cv2.goodFeaturesToTrack(GA[a], 800, 0.01, 6)
    q_, st_, _ = cv2.calcOpticalFlowPyrLK(GA[a], GA[b], p_, None, winSize=(21,21), maxLevel=4)
    k_ = st_.ravel() == 1; Hm_, _ = cv2.findHomography(p_[k_]*2, q_[k_]*2, cv2.RANSAC, 3.0); return Hm_
HA = {AREF: np.eye(3)}
for i in range(AREF, 0, -1): HA[i-1] = ahom(i, i-1) @ HA[i]
for i in range(AREF, len(A)-1): HA[i+1] = ahom(i, i+1) @ HA[i]
PINA = {i: cv2.perspectiveTransform(PIN_REF, HA[i])[0,0] for i in HA}

BV, _ = reader('drone_v.mp4'); BG_ = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in BV]; BREF = int(round(1.66*30))
bm_ = np.zeros((1920,1080), np.uint8); bm_[int(1920*.28):int(1920*.93)] = 255
def bhom(a, b):
    p_ = cv2.goodFeaturesToTrack(BG_[a], 1500, 0.01, 8, mask=bm_)
    q_, st_, _ = cv2.calcOpticalFlowPyrLK(BG_[a], BG_[b], p_, None, winSize=(31,31), maxLevel=4)
    k_ = st_.ravel() == 1; Hm_, _ = cv2.findHomography(p_[k_], q_[k_], cv2.RANSAC, 2.0); return Hm_
HB = {i: (np.eye(3) if i == BREF else bhom(BREF, i)) for i in range(0, len(BV))}
_c = np.float32([[0,0],[1080,0],[1080,1920],[0,1920]]); _ks = sorted(HB); _P = np.array([cv2.perspectiveTransform(_c[None], HB[i])[0] for i in _ks])
for _j, _i in enumerate(_ks): HB[_i] = cv2.getPerspectiveTransform(_c, np.float32(_P[max(0,_j-3):_j+4].mean(0)))
C, fc = reader('segC60.mp4'); B, fb = reader('drone_lote_sin-etiqueta.mp4'); Q = np.load('lote_quads.npy')

# --- casas: imagen "después" + máscara, seguidas al suelo de C
AFTER = cv2.imread('c_casas_al.png').astype(np.float32); HM = cv2.imread('c_casas_mask.png', 0)
REF = 60; g = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in C]
gm = np.zeros((H,W), np.uint8); gm[int(H*.22):] = 255
def hom(a, b):
    p = cv2.goodFeaturesToTrack(g[a], 1500, 0.01, 8, mask=gm)
    q, st, _ = cv2.calcOpticalFlowPyrLK(g[a], g[b], p, None, winSize=(31,31), maxLevel=4)
    k = st.ravel() == 1; Hm, _ = cv2.findHomography(p[k], q[k], cv2.RANSAC, 2.0); return Hm
HS = {}
for i in range(20, 110): HS[i] = np.eye(3) if i == REF else hom(REF, i)
# suavizado temporal: promedia las esquinas proyectadas y rehace cada homografía (quita el temblor)
corn = np.float32([[0,0],[W,0],[W,H],[0,H]]); ks = sorted(HS)
PJ = np.array([cv2.perspectiveTransform(corn[None], HS[i])[0] for i in ks])
for j, i in enumerate(ks):
    sm = PJ[max(0,j-3):j+4].mean(0); HS[i] = cv2.getPerspectiveTransform(corn, np.float32(sm))
# celdas que se "construyen": de cerca (abajo) hacia lejos (arriba), con algo de azar
CELL = 44; cells = []; rng = np.random.default_rng(3)
for y in range(0, H, CELL):
    for x in range(0, W, CELL):
        if (HM[y:y+CELL, x:x+CELL] > 0).mean() > 0.15: cells.append((x, y))
ys = np.array([c[1] for c in cells]); order = np.argsort(-(ys + rng.normal(0, 70, len(cells))))
T0, T1, DB = 4.82, 5.70, 0.16
start = {cells[k]: T0 + (T1-T0-DB)*r/len(cells) for r, k in enumerate(order)}
def build_mask(t):
    m = np.zeros((H,W), np.float32)
    for (x, y), s in start.items():
        u = ease((t-s)/DB)
        if u <= 0: continue
        h = int(CELL*u); m[y+CELL-h:y+CELL, x:x+CELL] = 1      # sube de la base al techo
    return cv2.GaussianBlur(m * (HM.astype(np.float32)/255), (0,0), 1.5)

def ramp(fr, fps, s, v):
    i = s*fps; n = max(1, int(round(v*fps/FPS)))
    idx = np.clip(np.arange(int(i)-n//2, int(i)-n//2+n), 0, len(fr)-1)
    return np.mean([fr[k].astype(np.float32) for k in idx], 0), int(np.clip(i, 0, len(fr)-1))
def zoomrot(img, z, ang, cx=W/2, cy=H/2):
    M = cv2.getRotationMatrix2D((cx, cy), ang, z)
    return cv2.warpAffine(img, M, (W,H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT), M
def radial_blur(img, amt):
    if amt <= 0.01: return img
    acc = img.copy()
    for j in range(1, 7): acc += zoomrot(img, 1 + amt*0.06*j/6, 0)[0]
    return acc/7

def draw_text(L, S, G, txt, f, cx, cy, a, sup=False, col=(255,255,255), glow=None):
    bb = f.getbbox(txt); tw, th = bb[2]-bb[0], bb[3]-bb[1]; ex = 0
    if sup: fs = BOLD(int(f.size*0.48)); ex = fs.getbbox('2')[2] + 4
    x, y = cx - (tw+ex)/2 - bb[0], cy - th/2 - bb[1]
    layers = [(S, (0,0,0,int(165*a)), 6), (L, col+(int(255*a),), 0)]
    if glow: layers.insert(1, (G, glow+(int(255*a),), 0))
    for D, c, off in layers:
        d = ImageDraw.Draw(D); d.text((x, y+off), txt, font=f, fill=c)
        if sup: d.text((x+bb[2]+4, y+off+bb[1]-fs.getbbox('2')[1]-4), '2', font=fs, fill=c)
    return x, y, tw, th
def layer(items):
    L = Image.new('RGBA', (W,H), (0,0,0,0)); S = Image.new('RGBA', (W,H), (0,0,0,0)); G = Image.new('RGBA', (W,H), (0,0,0,0))
    for it in items:
        if it[4] > 0.01: draw_text(L, S, G, *it)
    out = S.filter(ImageFilter.GaussianBlur(11))
    if G.getbbox():
        g1 = G.filter(ImageFilter.GaussianBlur(26)); g2 = G.filter(ImageFilter.GaussianBlur(9))
        out = Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(out, g1), g1), g2)
    return Image.alpha_composite(out, L)
def pop(t, t0, size, fn):   # entrada con escala 1.15 -> 1
    u = ease((t-t0)/0.25); return fn(max(8, int(size*(1.15-0.15*u)))), u
def word(t, a, b, txt, fn, size, cx, cy, sup=False, fade_out=True, col=(255,255,255), glow=None):
    if t < a-0.02 or (fade_out and t > b+0.15): return []
    f, u = pop(t, a, size, fn); o = u*(1-ease((t-b)/0.15)) if (fade_out and t > b) else u
    return [(txt, f, cx, cy - 14*(1-u), o, sup, col, glow)]
# subtítulo palabra por palabra (máquina de escribir con cursor), tiempos de la voz de la toma 3
WORDS = [(0.00,'Aquí'),(0.44,'encuentras'),(0.88,'terrenos'),(1.38,'desde'),(1.66,'127'),(2.22,'metros'),(2.76,'cuadrados'),
         (3.38,'dentro'),(3.94,'de'),(4.14,'una'),(4.24,'zona'),(4.48,'que'),(4.76,'sigue'),(5.02,'creciendo'),(5.50,'al'),
         (5.74,'poniente'),(6.10,'de'),(6.20,'Monterrey')]
SUBF = MED(60); SUBY = 1530
def subtitle(lay, t):
    cur = [w for w in WORDS if w[0] <= t]
    if not cur: return
    t0, w = cur[-1]
    if w in ('Aquí', 'terrenos', '127', 'creciendo', 'Monterrey'): return       # ya está en grande
    n = len(w); k = min(n, int((t-t0)/0.09*n)+1); txt = w[:k] + ('|' if k < n else '')
    S = Image.new('RGBA', (W,H), (0,0,0,0)); bb = SUBF.getbbox(w); x = W/2 - (bb[2]-bb[0])/2 - bb[0]
    ImageDraw.Draw(S).text((x, SUBY+3), txt, font=SUBF, fill=(0,0,0,190)); S = S.filter(ImageFilter.GaussianBlur(6))
    lay.alpha_composite(S); ImageDraw.Draw(lay).text((x, SUBY), txt, font=SUBF, fill=(255,255,255,255))
# pin de ubicación rojo
def pin_img(h):
    S = 4; w = int(h*0.72); im = Image.new('RGBA', (w*S, h*S), (0,0,0,0)); d = ImageDraw.Draw(im); r = w*S/2
    d.polygon([(r*0.22, r*1.25), (r*1.78, r*1.25), (r, h*S)], fill=(214,40,40,255))
    d.ellipse([0, 0, w*S, w*S], fill=(229,57,53,255))
    d.ellipse([r*0.15, r*0.12, r*1.2, r*1.0], fill=(255,120,110,90))          # brillo
    d.ellipse([r*0.58, r*0.58, r*1.42, r*1.42], fill=(255,255,255,255))
    return im.resize((w, h), Image.LANCZOS)
PIN = pin_img(150); PIN_S = pin_img(60)
_p3 = Image.open('pin3d.png').convert('RGBA'); _p3 = _p3.crop(_p3.getbbox())
PIN3D = _p3.resize((int(_p3.width*112/_p3.height), 112), Image.LANCZOS)      # ícono 3D de Liz, chico
MW = BOLD(162).getbbox('Monterrey'); MTW = MW[2]-MW[0]; GAP = 18
MCX = W/2 + (PIN3D.width + GAP)/2                                             # grupo [pin + Monterrey] centrado
def put_pin(lay, x, y, t0, t, P=PIN):
    u = (t-t0)/0.45
    if u <= 0: return
    b = 1 + 2.70158*(min(u,1)-1)**3 + 1.70158*(min(u,1)-1)**2      # ease-out-back (rebote)
    yy = y - P.height - 260*(1-b); o = min(1, u*3)
    sh = Image.new('RGBA', (W,H), (0,0,0,0)); ImageDraw.Draw(sh).ellipse([x-30, y-9, x+30, y+9], fill=(0,0,0,int(120*o)))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    Pm = P.copy(); Pm.putalpha(Pm.getchannel('A').point(lambda v: int(v*o)))
    lay.alpha_composite(Pm, (int(x - P.width/2), int(yy)))
def persp(lay, _unused, PT, CM):
    # texto "pegado" al plano: perspectiva fija del plano (PT) + la cámara digital (CM)
    arr = cv2.warpPerspective(np.array(lay), PT, (W,H), flags=cv2.INTER_LINEAR)
    return Image.fromarray(cv2.warpAffine(arr, CM, (W,H), flags=cv2.INTER_LINEAR))
def plane(src_c, tilt, rot, scale_top):
    # homografía que acuesta el texto: arriba más angosto (perspectiva) y girado a la dirección de las calles
    cx, cy = src_c; w, h = 520, 260
    s = np.float32([[cx-w,cy-h],[cx+w,cy-h],[cx+w,cy+h],[cx-w,cy+h]])
    d = np.float32([[cx-w*scale_top,cy-h*tilt],[cx+w*scale_top,cy-h*tilt],[cx+w,cy+h],[cx-w,cy+h]])
    R = np.vstack([cv2.getRotationMatrix2D((cx,cy), rot, 1.0), [0,0,1]])
    return R @ cv2.getPerspectiveTransform(s, d)
PERS_GROUND = plane((W/2, 900), 0.62, 9, 0.78)    # sobre las casas
PERS_FAR = plane((W/2, 630), 0.75, 4, 0.86)       # hacia la sierra
def comp(base, lay, M=None):
    if M is not None: lay = Image.fromarray(cv2.warpAffine(np.array(lay), M, (W,H), flags=cv2.INTER_LINEAR))
    im = Image.fromarray(cv2.cvtColor(np.clip(base,0,255).astype(np.uint8), cv2.COLOR_BGR2RGB)).convert('RGBA')
    return cv2.cvtColor(np.array(Image.alpha_composite(im, lay).convert('RGB')), cv2.COLOR_RGB2BGR).astype(np.float32)

p = subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
    '-c:v','libx264','-crf','16','-pix_fmt','yuv420p','reel3d_v.mp4'], stdin=subprocess.PIPE)
cA = Q.mean(1)
for n in range(int(DUR*FPS)+1):
    t = n/FPS
    if t < T_AB:
        a, b = 6.449, -1.879; img, ai = ramp(A, fa, a*t + b*t*t, a + 2*b*t)
        img, MA = zoomrot(img, 1.18 - 0.18*ease(t/0.5), 0); img = radial_blur(img, 2.0*(1-ease(t/0.35)))
        img = radial_blur(img, 2.5*ease((t-1.30)/0.15))                      # zoom-blur hacia el lote
        px, py = PINA[ai]; px, py = MA @ np.array([px, py, 1.0])

    elif t < T_BC:
        k = min(len(B)-1, int(round((t - T_AB + 1.40)*fb))); img = B[k].astype(np.float32)
        z = 1 + 0.38*ease((t-1.60)/0.9) + 0.25*inout((t-4.15)/0.55)**2
        img = zoomrot(img, z, 0, cx=cA[k][0], cy=cA[k][1])[0]
        if t > 4.50: img = radial_blur(img, 3.0*ease((t-4.50)/0.2))
        lx = float(np.clip(cA[k][0], 380, W-380)); top = Q[k][:,1].min(); lb = Q[k][:,1].max()
        items = word(t, 1.38, 9, 'desde', LIGHT, 74, lx, 330, fade_out=False) if t < 4.55 else []
        items += word(t, 1.66, 9, '127 m', BOLD, 205, lx, 470, sup=True, fade_out=False) if t < 4.55 else []
        lay = layer(items)
        if 1.85 <= t < 4.55:
            gg = ease((t-1.85)/0.3); d = ImageDraw.Draw(lay); y1 = 575; y2 = y1 + (top - 22 - y1)*gg
            d.line([(lx, y1), (cA[k][0], y2)], fill=(255,244,220,235), width=4)
            if gg >= 1: d.ellipse([cA[k][0]-8, top-30, cA[k][0]+8, top-14], fill=(255,244,220,255))
        img = comp(img, lay)
    else:
        tc = t - T_BC; img, ci = ramp(C, fc, 0.45 + 0.5*tc + 1e-4, 0.5); ci = int(np.clip(ci, 20, 109))
        img = cv2.warpPerspective(img, np.linalg.inv(HS[ci]), (W,H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)   # estabilizado al REF
        bm = build_mask(t)[...,None]
        if bm.max() > 0: img = img*(1-bm) + AFTER*bm                    # casas sin deformar
        u = inout(tc/2.33); camz = 1.16 + 0.10*u; camx = -30 + 45*u; camr = 1.5 - 3.0*u   # cámara digital
        CM = cv2.getRotationMatrix2D((W/2, H*0.55), camr, camz); CM[0,2] += camx
        img = cv2.warpAffine(img, CM, (W,H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        img = radial_blur(img, 3.0*(1-ease(tc/0.3)))
        sc = []
        sc += word(t, 5.50, 9, 'al poniente de', LIGHT, 70, W/2, 360, fade_out=False) + word(t, 6.20, 9, 'Monterrey', BOLD, 162, MCX, 480, fade_out=False)
        lay = layer(sc)
        if t >= 6.26:                                                        # el pin entra con un pop justo después de la palabra
            u = (t-6.26)/0.35; b = 1 + 2.70158*(min(u,1)-1)**3 + 1.70158*(min(u,1)-1)**2
            sc_ = max(0.05, b); P = PIN3D.resize((max(1,int(PIN3D.width*sc_)), max(1,int(PIN3D.height*sc_))), Image.LANCZOS)
            P.putalpha(P.getchannel('A').point(lambda v: int(v*min(1, u*3))))
            px = MCX - MTW/2 - GAP - PIN3D.width/2; py = 480
            sh = Image.new('RGBA', (W,H), (0,0,0,0)); sh.alpha_composite(P, (int(px-P.width/2), int(py-P.height/2)+6))
            sh = Image.fromarray((np.array(sh)*[0,0,0,0.45]).astype(np.uint8)).filter(ImageFilter.GaussianBlur(8))
            lay.alpha_composite(sh); lay.alpha_composite(P, (int(px-P.width/2), int(py-P.height/2)))
        img = comp(img, lay)
    p.stdin.write(np.clip(img,0,255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
