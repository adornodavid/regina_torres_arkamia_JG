# Toma 1: punch-in en "construir" e "invertir" + la palabra en Gotham Bold sobre la palma que la presenta.
import cv2, numpy as np, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FF = os.path.expanduser('~/arkamia-reels/bin/ffmpeg'); src, dst = sys.argv[1], sys.argv[2]
FONT = ImageFont.truetype(os.path.expanduser('~/Library/Fonts/Gotham-Bold.otf'), 78)
cap = cv2.VideoCapture(src); fps = cap.get(5); W, H = int(cap.get(3)), int(cap.get(4)); s = W/480
ease = lambda x: 0 if x<=0 else 1 if x>=1 else 1-(1-x)**3
def zoom(t): return 1 + .12*ease((t-2.40)/.45) + .12*ease((t-3.40)/.45)
CX, CY = 240*s, 400*s                       # centro del zoom: torso
# palma (coords 480p) por tiempo, medida en cuadros
PALM = {'Construir': [(2.5,(142,372)),(2.9,(122,395)),(3.3,(120,420))],
        'Invertir':  [(3.5,(345,380)),(3.9,(340,383)),(4.5,(340,385))]}
SHOW = {}  # sin palabras: solo el zoom
def palm(w, t):
    k = PALM[w]; ts = [a for a,_ in k]
    x = np.interp(t, ts, [p[0] for _,p in k]); y = np.interp(t, ts, [p[1] for _,p in k]); return x*s, y*s
def label(w):
    bb = FONT.getbbox(w); tw, th = bb[2]-bb[0], bb[3]-bb[1]; pad = 30
    im = Image.new('RGBA', (tw+2*pad, th+2*pad), (0,0,0,0)); d = ImageDraw.Draw(im)
    sh = Image.new('RGBA', im.size, (0,0,0,0)); ImageDraw.Draw(sh).text((pad-bb[0], pad-bb[1]+4), w, font=FONT, fill=(0,0,0,150))
    sh = sh.filter(ImageFilter.GaussianBlur(9)); im = Image.alpha_composite(sh, im)
    ImageDraw.Draw(im).text((pad-bb[0], pad-bb[1]), w, font=FONT, fill=(255,255,255,255)); return im
LBL = {w: label(w) for w in SHOW}
p = subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-i',src,
    '-map','0:v','-map','1:a','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','copy',dst], stdin=subprocess.PIPE)
n = 0
while True:
    ok, f = cap.read()
    if not ok: break
    t = n/fps; z = zoom(t)
    M = np.float32([[z,0,CX-z*CX],[0,z,CY-z*CY]])
    f = cv2.warpAffine(f, M, (W,H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    im = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert('RGBA')
    for w,(a,b) in SHOW.items():
        if not a <= t <= b+.2: continue
        u = ease((t-a)/.22); o = u * (1-ease((t-b)/.2)) if t > b else u
        px, py = palm(w, t); px, py = z*px+CX-z*CX, z*py+CY-z*CY
        L = LBL[w]; sc = .8+.2*u; L2 = L.resize((int(L.width*sc), int(L.height*sc)), Image.LANCZOS)
        al = L2.getchannel('A').point(lambda v: int(v*o)); L2.putalpha(al)
        im.alpha_composite(L2, (int(px-L2.width/2), int(py-L2.height-40*s/2.25-20*(1-u))))
    p.stdin.write(cv2.cvtColor(np.array(im.convert('RGB')), cv2.COLOR_RGB2BGR).tobytes()); n += 1
p.stdin.close(); p.wait()
