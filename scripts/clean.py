# Regina sobre verde limpio: quita cintas naranjas, tripié y degradado del ciclorama
import cv2, numpy as np, subprocess, sys, os
src, dst = sys.argv[1], sys.argv[2]
FF = __import__('os').path.expanduser('~/arkamia-reels/bin/ffmpeg')
cap = cv2.VideoCapture(src); fps = cap.get(5); W, H = 1080, 1920
p = subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(fps),'-i','-',
    '-i',src,'-map','0:v','-map','1:a','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-c:a','copy',dst], stdin=subprocess.PIPE)
GREEN = np.array([64,177,0], np.uint8)  # BGR de chroma limpio
frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    g = cv2.inRange(hsv, (38,110,90), (85,255,255))            # verde
    o = cv2.inRange(hsv, (5,80,120), (25,255,255)); o[:int(H*.82)] = 0  # cintas naranjas, solo piso
    bgm = cv2.bitwise_or(g, o)
    if not os.environ.get('MEDIO'): bgm[:, :int(W*.12)] = 255; bgm[:, int(W*.88):] = 255      # garbage matte lateral
    fg = cv2.bitwise_not(bgm)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5,5),np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg)       # se queda con la persona
    if n > 1:
        k = 1 + np.argmax(st[1:,4]); fg = np.where(lab==k,255,0).astype(np.uint8)
    cs,_ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); fg = cv2.drawContours(np.zeros_like(fg), cs, -1, 255, -1)  # sin huecos
    a = cv2.GaussianBlur(fg,(5,5),0).astype(np.float32)[...,None]/255
    # despill: limita el verde al máximo de rojo/azul
    b,gg,r = cv2.split(f.astype(np.int16)); gg = np.minimum(gg, np.maximum(r,b)); f2 = cv2.merge([b,gg,r]).astype(np.float32)
    out = f2*a + GREEN.astype(np.float32)*(1-a)
    p.stdin.write(out.astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
