WHIP = 4      # cuadros de whip a cada lado del corte
# ---------------- fuentes ----------------
def load_face(n):
    a = np.array([[float(x) for x in l.split()] for l in open(f'face{n}.txt') if l[0].isdigit()])
    ok = a[:, 1] >= 0
    for c in (1, 2, 3): a[~ok, c] = np.interp(np.flatnonzero(~ok), np.flatnonzero(ok), a[ok, c])
    k = np.ones(15)/15
    return np.stack([np.convolve(np.pad(a[:, c], 7, mode='edge'), k, 'valid') for c in (1, 2, 3)], 1)
class LazyFrames:
    """Lee los cuadros bajo demanda (la versión original los cargaba todos: ~9 GB a 1080p, no cabe en 8 GB de RAM)."""
    def __init__(self, path):
        self.path = path; c = cv2.VideoCapture(path); self.n = int(c.get(cv2.CAP_PROP_FRAME_COUNT)); c.release()
        self.cap = None; self.pos = -1; self.cache = {}
    def __len__(self): return self.n
    def __getitem__(self, i):
        i = min(max(i, 0), self.n - 1)
        if i in self.cache: return self.cache[i]
        if self.cap is None or i < self.pos:
            if self.cap is not None: self.cap.release()
            self.cap = cv2.VideoCapture(self.path); self.pos = -1
        f = None
        while self.pos < i:
            r, f = self.cap.read(); self.pos += 1
            if not r: self.n = self.pos; return self.__getitem__(self.n - 1)
        self.cache = {i: f}; return f
for s in SEG:
    s['frames'] = LazyFrames(f"s{s['n']}.mp4")
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
            if s.get('ink') == 'dark': L = [(w, tw, {'s': 'sd', 'b': 'bd', 'g': 'gd'}.get(k, k)) for w, tw, k in L]
            sp = [sprite(w, k) for w, _, k in L]; gap = font(L[0][2]).getlength(' ')*.75
            width = sum(x[3] for x in sp) + gap*(len(sp) - 1); rows.append((L, sp, gap, width))
        bases = []; y = 0
        for i, (L, sp, gap, wd) in enumerate(rows):
            asc = font(L[0][2]).getmetrics()[0]
            if i: y += asc*(.80 if L[0][2] != 's' else .95)*s.get('lead', 1)   # lead: más aire entre renglones (toma 6, Liz)
            bases.append(y)
        top = bases[0] - font(rows[0][0][0][2]).getmetrics()[0]*.7; mid = (top + bases[-1])/2
        for (L, sp, gap, wd), by in zip(rows, bases):
            x = ax - wd/2
            for (w, tw, k), spr in zip(L, sp):
                e = ease((tl - tw)/.16)
                if k == 'y' and tl >= tw - .001:          # autocompletar letra por letra (toma 8: terraregia.com con el gesto)
                    nch = max(1, int(round(len(w)*min(1, (tl - tw)/.9))))
                    blit(img, sprite(w[:nch], 'y'), 0, ay + by - mid, alpha=fade, left=x, shadow=.5)
                elif tl >= tw - .001:
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
        else:                                # David 8-oct: el acento va DEBAJO del subtítulo, entre las piernas, no en la cabeza
            sc = min(165/cap, 900/spr[3])
            tw = spr[3]*sc; cx = np.clip(fx, 50 + tw/2, W - 50 - tw/2)
            by = s.get('title_y', .745)*H + 34*(1 - e)
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
    if s.get('fix'):                     # texto quieto al centro aunque la modelo se mueva (toma 2, Liz)
        fx = W/2; fy, fh = np.median(s['face'][:, 1])*H, np.median(s['face'][:, 2])*H
    if z != 1:
        M = cv2.getRotationMatrix2D((fx, fy), 0, z)
        base = cv2.warpAffine(base, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if m is not None: m = cv2.warpAffine(m, M, (W, H), flags=cv2.INTER_LINEAR)
        fh *= z
    img = base.copy()
    # 1) títulos detrás de la cabeza
    if s['titles']:
        draw_titles(img, s, lt, fx, fy - fh/2, fh)   # por delante: ya no se recorta con la silueta
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
