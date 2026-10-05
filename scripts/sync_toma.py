# Retimea la salida de Genjutsu a la voz original midiendo la boca (Vision) y busca K/offset.
# Uso: python3 sync_toma.py gen.mp4 boca_src.txt boca_gen.txt voz.mp4 salida.mp4
import sys, numpy as np, cv2, subprocess, os
gen, fsrc, fgen, voz, out = sys.argv[1:6]
FF = os.path.expanduser('~/arkamia-reels/bin/ffmpeg')
def load(f):
    a = np.array([[float(x) for x in l.split()[:2]] for l in open(f) if l[0].isdigit()]); a[a[:,1] < 0, 1] = np.nan; return a
S, G = load(fsrc), load(fgen)
ts = np.arange(0, S[-1,0], 1/100); s = np.interp(ts, S[:,0], np.nan_to_num(S[:,1], nan=np.nanmean(S[:,1])))
best = (-2, 1, 0)
for K in np.arange(0.95, 1.10, 0.0025):
    for off in np.arange(-0.4, 0.4, 0.01):
        tg = G[:,0]; tsrc = K*tg + off; ok = (tsrc >= 0) & (tsrc <= ts[-1]) & ~np.isnan(G[:,1])
        if ok.sum() < 60: continue
        c = np.corrcoef(np.interp(tsrc[ok], ts, s), G[ok,1])[0,1]
        if c > best[0]: best = (c, K, off)
c, K, off = best; print(f'corr={c:.3f} K={K:.4f} off={off:+.3f}')
cap = cv2.VideoCapture(gen); F = []
while True:
    r, f = cap.read()
    if not r: break
    F.append(cv2.resize(f, (720, 1280), interpolation=cv2.INTER_AREA))
gfps = cap.get(cv2.CAP_PROP_FPS); D = S[-1,0] + 1/30   # duración de la toma original; la cola faltante queda en el último cuadro
p = subprocess.Popen([FF,'-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','720x1280','-r','30','-i','-','-i',voz,
    '-map','0:v','-map','1:a','-c:v','libx264','-crf','16','-preset','slow','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest',out], stdin=subprocess.PIPE)
for n in range(int(round(D*30))):
    x = ((n/30 - off)/K)*gfps; x = min(max(x, 0), len(F)-1); i = int(x); a = x - i; j = min(i+1, len(F)-1)
    fr = F[i] if a < 1e-3 else cv2.addWeighted(F[i], 1-a, F[j], a, 0)
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
