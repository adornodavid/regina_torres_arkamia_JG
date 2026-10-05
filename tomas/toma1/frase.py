# Pega la frase real de la pared ("Creamos soluciones inmobiliarias integrales.") desde la foto del showroom, detrás de Regina.
import cv2, numpy as np, subprocess, sys, os
FF=os.path.expanduser('~/arkamia-reels/bin/ffmpeg'); src,dst=sys.argv[1],sys.argv[2]
P=cv2.imread('../../fondos/Showroom Terra Regia-Concéntrico + Terra Regia + Urban-MAY24-03.jpg'); H=np.load('H_v2p.npy')
W=cv2.warpPerspective(P,np.linalg.inv(H),(1080,1920),flags=cv2.INTER_AREA).astype(np.float32)
Y0,Y1,X0,X1=540,600,345,830                     # franja del letrero (coords 1080x1920)
band=np.zeros((1920,1080),np.float32); band[Y0:Y1,X0:X1]=1
band=cv2.GaussianBlur(band,(0,0),6)
sig=12
cap=cv2.VideoCapture(src); n=0
p=subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s','1080x1920','-r','30','-i','-','-i',src,
  '-map','0:v','-map','1:a','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-c:a','copy',dst],stdin=subprocess.PIPE)
while True:
    ok,f=cap.read()
    if not ok: break
    m=cv2.imread(f'matte/m_{n:05d}.png',0); n+=1
    per=cv2.GaussianBlur(cv2.dilate(m,np.ones((5,5),np.uint8)).astype(np.float32)/255,(0,0),1.5)
    V=f.astype(np.float32)
    # igualar luz/color de la foto a la pared del video (ganancia local suave, sin contar a Regina)
    wv=(1-per)
    bv=cv2.GaussianBlur(V*wv[...,None],(0,0),sig)/(cv2.GaussianBlur(wv,(0,0),sig)[...,None]+1e-4)
    bw=cv2.GaussianBlur(W,(0,0),sig)
    Wm=W*(bv/(bw+1e-3))
    a=(band*(1-per))[...,None]
    o=V*(1-a)+Wm*a
    p.stdin.write(np.clip(o,0,255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
