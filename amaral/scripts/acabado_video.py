# Acabado de cámara real por cuadro (versión video de toma8/acabado_foto.py): escala lanczos a 1080x1920,
# curva fílmica, halación, aberración cromática, viñeta y grano distinto en cada cuadro. Uso: acabado_video.py in.mp4 out.mp4
import cv2, numpy as np, subprocess, sys, os
src, dst = sys.argv[1], sys.argv[2]; FF = os.path.expanduser('~/arkamia-reels/bin/ffmpeg')
cap = cv2.VideoCapture(src); fps = cap.get(5); W, H = 1080, 1920
p = subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-i',src,
    '-map','0:v','-map','1:a','-c:v','libx264','-crf','15','-preset','slow','-pix_fmt','yuv420p','-c:a','copy',dst], stdin=subprocess.PIPE)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); cx, cy = W/2, H/2
def radial(ch, k): return cv2.remap(ch, (cx+(xx-cx)*(1+k)).astype(np.float32), (cy+(yy-cy)*(1+k)).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
r = np.sqrt(((xx-cx)/cx)**2 + ((yy-cy)/cy)**2); vig = (1 - .22*np.clip(r-.45, 0, 1)**1.6)[..., None]
n = 0
while True:
    ok, f = cap.read()
    if not ok: break
    im = cv2.resize(f, (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)/255
    im = .012 + im*.988; k = .78
    im = np.where(im > k, k + (1-k)*(1-np.exp(-(im-k)/(1-k)*1.3))/(1-np.exp(-1.3)), im)
    lum = im.mean(2, keepdims=True); hi = np.clip((lum-.78)/.22, 0, 1)*im
    bloom = cv2.GaussianBlur(hi, (0,0), 14)*.16 + cv2.GaussianBlur(hi, (0,0), 50)*.10; bloom[...,2] *= 1.15; bloom[...,0] *= .85
    im = 1 - (1-im)*(1-bloom)
    im[...,2] = radial(im[...,2], -.0012); im[...,0] = radial(im[...,0], .0012)
    im *= vig
    hsv = cv2.cvtColor(np.clip(im,0,1).astype(np.float32), cv2.COLOR_BGR2HSV); hsv[...,1] *= .92; im = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    rng = np.random.default_rng(n); g = cv2.GaussianBlur(rng.normal(0,1,(H,W)).astype(np.float32), (0,0), .7); g /= g.std()
    im = im + (g*.022*(1.2-im.mean(2)))[...,None] + rng.normal(0,.004,im.shape).astype(np.float32)
    p.stdin.write(np.clip(im*255,0,255).astype(np.uint8).tobytes()); n += 1
p.stdin.close(); p.wait(); print('cuadros', n)
