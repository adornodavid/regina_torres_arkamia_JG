# Toma de drone: delimitación de un lote con luz + "127 m²", seguida al suelo con homografías cuadro a cuadro.
import cv2, numpy as np, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FF = os.path.expanduser('~/arkamia-reels/bin/ffmpeg'); src, dst = sys.argv[1], sys.argv[2]
T_REF, T_DRAW, D_DRAW, T_LBL = 1.66, 1.62, 0.75, 1.95          # sincronía con "127 metros cuadrados"
QUAD = np.float32([[520,905],[565,898],[557,843],[512,850]])     # lote en el cuadro de referencia (1080x1920)
LIGHT = np.array([255, 244, 220], np.float32)                     # blanco cálido (RGB)
cap = cv2.VideoCapture(src); fps = cap.get(5); frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
N = len(frames); H, W = frames[0].shape[:2]; ref = int(round(T_REF*fps))
# --- seguimiento: homografía del suelo entre cuadros consecutivos
mask = np.zeros((H,W), np.uint8); mask[int(H*.28):int(H*.93)] = 255
gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
def hom(a, b):
    p = cv2.goodFeaturesToTrack(gray[a], 1500, 0.01, 8, mask=mask)
    q, st, _ = cv2.calcOpticalFlowPyrLK(gray[a], gray[b], p, None, winSize=(31,31), maxLevel=4)
    g = st.ravel() == 1; Hm, _ = cv2.findHomography(p[g], q[g], cv2.RANSAC, 2.0); return Hm
quads = {ref: QUAD.copy()}
for i in range(ref, N-1):  quads[i+1] = cv2.perspectiveTransform(quads[i][None], hom(i, i+1))[0]
for i in range(ref, 0, -1): quads[i-1] = cv2.perspectiveTransform(quads[i][None], hom(i, i-1))[0]
# suavizado temporal leve para quitar temblor del tracking
Q = np.array([quads[i] for i in range(N)]); K = 5
Qs = np.array([Q[max(0,i-K):i+K+1].mean(0) for i in range(N)]); np.save('lote_quads.npy', Qs)
font = ImageFont.truetype(os.path.expanduser('~/Library/Fonts/Gotham-Bold.otf'), 66); fsup = ImageFont.truetype(os.path.expanduser('~/Library/Fonts/Gotham-Bold.otf'), 38)
ease = lambda x: 0 if x <= 0 else 1 if x >= 1 else 1-(1-x)**3
def perimeter_pts(q, prog):
    pts = list(q) + [q[0]]; seg = [np.linalg.norm(pts[k+1]-pts[k]) for k in range(4)]; L = sum(seg) * prog; out = [pts[0]]
    for k in range(4):
        if L <= 0: break
        t = min(1, L/seg[k]); out.append(pts[k] + (pts[k+1]-pts[k])*t); L -= seg[k]
    return np.array(out)
p = subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-c:v','libx264','-crf','16','-pix_fmt','yuv420p',dst], stdin=subprocess.PIPE)
for i, f in enumerate(frames):
    t = i/fps; out = f.astype(np.float32)
    prog = ease((t-T_DRAW)/D_DRAW)
    if prog > 0:
        q = Qs[i]; S = 2                                            # supersampling para líneas finas limpias
        line = np.zeros((H*S, W*S), np.uint8)
        cv2.polylines(line, [np.int32(perimeter_pts(q, prog)*S)], False, 255, 4*S, cv2.LINE_AA)
        line = cv2.resize(line, (W,H), interpolation=cv2.INTER_AREA).astype(np.float32)/255
        fill = np.zeros((H,W), np.float32)
        if prog >= 1:
            k = ease((t-T_DRAW-D_DRAW)/0.4); pulse = 0.16 + 0.04*np.sin((t-T_DRAW-D_DRAW)*4.0)
            cv2.fillPoly(fill, [np.int32(q)], 1.0); fill = cv2.GaussianBlur(fill, (0,0), 1.2) * pulse * k
        glow = cv2.GaussianBlur(line, (0,0), 5)*1.3 + cv2.GaussianBlur(line, (0,0), 18)*1.0
        a = np.clip(line + glow*0.9 + fill, 0, 1.4)[...,None]
        out = out + (LIGHT[::-1] - out*0.35) * np.clip(a, 0, 1) * 0.95   # luz aditiva cálida
    if t >= T_LBL and not os.environ.get('NOLABEL'):
        u = ease((t-T_LBL)/0.35); q = Qs[i]; c = q.mean(0); top = q[:,1].min()
        im = Image.fromarray(cv2.cvtColor(np.clip(out,0,255).astype(np.uint8), cv2.COLOR_BGR2RGB)).convert('RGBA')
        lay = Image.new('RGBA', im.size, (0,0,0,0)); d = ImageDraw.Draw(lay)
        y1 = top - 18; y2 = top - 18 - 150*u
        d.line([(c[0], y1), (c[0], y2)], fill=(255,244,220,int(235*u)), width=3)
        d.ellipse([c[0]-6, y1-6, c[0]+6, y1+6], fill=(255,244,220,int(255*u)))
        txt = '127 m'; bb = font.getbbox(txt); tw = bb[2]-bb[0] + 26; th = bb[3]-bb[1]   # el ² no existe en Gotham: se dibuja
        tx, ty = c[0]-tw/2, y2-th-26 + 12*(1-u)
        def write(dr, dy, col):
            dr.text((tx, ty+dy), txt, font=font, fill=col); dr.text((tx+bb[2]+3, ty+dy-6), '2', font=fsup, fill=col)
        sh = Image.new('RGBA', im.size, (0,0,0,0)); write(ImageDraw.Draw(sh), 4, (0,0,0,int(170*u)))
        sh = sh.filter(ImageFilter.GaussianBlur(10)); im = Image.alpha_composite(Image.alpha_composite(im, sh), lay)
        write(ImageDraw.Draw(im), 0, (255,255,255,int(255*u)))
        out = cv2.cvtColor(np.array(im.convert('RGB')), cv2.COLOR_RGB2BGR).astype(np.float32)
    p.stdin.write(np.clip(out,0,255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
