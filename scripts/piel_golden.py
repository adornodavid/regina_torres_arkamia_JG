# Regina: piel mate (quita el brillo plástico de IA) + luz golden hour solo sobre ella. Uso: piel_golden.py in.mp4 mattedir out.mp4 [--frame N out.png]
import cv2, numpy as np, subprocess, sys, os
FF = os.path.expanduser('~/arkamia-reels/bin/ffmpeg'); src, md, dst = sys.argv[1], sys.argv[2], sys.argv[3]
one = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[4] == '--frame' else None
cap = cv2.VideoCapture(src); fps = cap.get(5); W, H = int(cap.get(3)), int(cap.get(4))
rng = np.random.default_rng(1); NM = len([x for x in os.listdir(md) if x.endswith('.png')])
def grade(f, m):
    x = f.astype(np.float32)/255
    m = cv2.GaussianBlur(m.astype(np.float32)/255, (0,0), 2)[...,None]
    ycc = cv2.cvtColor(f, cv2.COLOR_BGR2YCrCb).astype(np.float32)
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    skin = ((ycc[...,1] > 138) & (ycc[...,1] < 180) & (ycc[...,2] > 85) & (ycc[...,2] < 130) & (hsv[...,1] > 55)).astype(np.uint8)
    skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((7,7),np.uint8)).astype(np.float32)   # sin motitas sueltas
    skin = cv2.GaussianBlur(skin, (0,0), 3)[...,None] * m
    # 1) quitar el "glow": brillo especular suave y difuso -> se resta el halo y se comprimen altas luces de piel
    L = x.mean(2, keepdims=True)
    halo = cv2.GaussianBlur(np.clip(L-0.55, 0, 1), (0,0), 6)[...,None]
    x = x - halo*float(os.environ.get("HALO","0.55"))*skin
    knee = 0.62; Lx = x.max(2, keepdims=True)
    comp = np.where(Lx > knee, knee + (Lx-knee)*0.55, Lx) / np.maximum(Lx, 1e-4)
    x = x*(1 - skin + skin*comp)
    # textura de piel: micro-poro de alta frecuencia (la IA la alisa)
    n = rng.normal(0, 1, (H, W)).astype(np.float32); n = n - cv2.GaussianBlur(n, (0,0), 1.2)
    x = x + (n*float(os.environ.get("PORO","0.022")))[...,None]*skin
    # 2) golden hour solo sobre Regina: balance cálido + key dorada desde el frente-izquierda
    warm = np.array([0.93, 0.995, 1.05], np.float32)              # BGR
    xg = x*warm
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    key = np.clip(1.0 - (xx/W)*0.55 - np.abs(yy/H-0.35)*0.3, 0.35, 1.0)[...,None]   # más luz del lado izq y en la cara
    gold = np.array([0.55, 0.78, 1.0], np.float32)
    lum = xg.mean(2, keepdims=True)
    xg = xg + gold*key*0.06*np.clip(lum*1.4, 0, 1)                 # luz dorada que respeta sombras
    xg = np.clip((xg-0.5)*1.08+0.5, 0, 1)
    if os.environ.get('NOWARM'): xg = x                       # la toma ya trae golden hour: solo piel mate
    out = x*(1-m) + xg*m
    return (np.clip(out, 0, 1)*255).astype(np.uint8)
if one is not None:
    cap.set(1, one); ok, f = cap.read(); m = cv2.imread(f'{md}/m_{one:05d}.png', 0)
    cv2.imwrite(sys.argv[6], grade(f, m)); sys.exit()
p = subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-i',src,
    '-map','0:v','-map','1:a','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-c:a','copy',dst], stdin=subprocess.PIPE)
k = 0
while True:
    ok, f = cap.read()
    if not ok: break
    m = cv2.imread(f'{md}/m_{min(k,NM-1):05d}.png', 0); p.stdin.write(grade(f, m).tobytes()); k += 1
p.stdin.close(); p.wait()
