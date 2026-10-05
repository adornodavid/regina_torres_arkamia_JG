# Zoom suave por código. Uso: python3 zoom_punch.py in.mp4 out.mp4 "t0:dur:zoom,t0:dur:zoom" cx cy   (cx, cy en fracción del cuadro)
import cv2, numpy as np, subprocess, sys, os
FF = os.path.expanduser('~/arkamia-reels/bin/ffmpeg'); src, dst = sys.argv[1], sys.argv[2]
steps = [tuple(map(float, k.split(':'))) for k in sys.argv[3].split(',')]; cxf, cyf = float(sys.argv[4]), float(sys.argv[5])
ease = lambda x: 0 if x <= 0 else 1 if x >= 1 else 0.5 - 0.5*np.cos(np.pi*x)   # ease in-out, sin golpe
cap = cv2.VideoCapture(src); fps = cap.get(5); W, H = int(cap.get(3)), int(cap.get(4)); CX, CY = cxf*W, cyf*H
p = subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-i',src,
    '-map','0:v','-map','1:a?','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-c:a','copy',dst], stdin=subprocess.PIPE)
n = 0
while True:
    ok, f = cap.read()
    if not ok: break
    t = n/fps; z = 1 + sum((zz-1)*ease((t-t0)/d) for t0, d, zz in steps)
    M = np.float32([[z,0,CX-z*CX],[0,z,CY-z*CY]])
    p.stdin.write(cv2.warpAffine(f, M, (W,H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT).tobytes()); n += 1
p.stdin.close(); p.wait()
