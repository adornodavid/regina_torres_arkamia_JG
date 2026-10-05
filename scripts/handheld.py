# Cámara en mano sutil: deriva suave (ruido de baja frecuencia) en x/y/rotación con overscan para no ver bordes.
import cv2, numpy as np, subprocess, sys, os
FF = os.path.expanduser('~/arkamia-reels/bin/ffmpeg'); src, dst = sys.argv[1], sys.argv[2]; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 7
cap = cv2.VideoCapture(src); fps = cap.get(5); W, H = int(cap.get(3)), int(cap.get(4)); N = int(cap.get(7))
rng = np.random.default_rng(seed)
def drift(amp, smooth):
    x = np.cumsum(rng.normal(0, 1, N + 200)); x = np.convolve(x, np.ones(smooth)/smooth, 'same')[100:100+N]
    x -= np.linspace(x[0], x[-1], N) * 0.6; x = x - x.mean(); return amp * x / (np.abs(x).max() + 1e-6)
dx, dy, rot = drift(W*.010, 25), drift(H*.006, 25), drift(0.35, 30)
dx += drift(W*.0015, 5); dy += drift(H*.0012, 5)            # micro-temblor de mano
S = 1.045                                                    # overscan
p = subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-i',src,
    '-map','0:v','-map','1:a?','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-c:a','copy',dst], stdin=subprocess.PIPE)
for n in range(N):
    ok, f = cap.read()
    if not ok: break
    M = cv2.getRotationMatrix2D((W/2, H/2), rot[n], S); M[0,2] += dx[n]; M[1,2] += dy[n]
    p.stdin.write(cv2.warpAffine(f, M, (W,H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT).tobytes())
p.stdin.close(); p.wait()
