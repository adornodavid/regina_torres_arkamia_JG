# Toma 5 Amaral: drone alto con push-in lento; pin rojo cae sobre Amaral, luego la ruta se dibuja hasta Sendero ("5 min")
# y hasta la Universidad Tecnológica ("3 min"), cada destino con su pin y etiqueta. Los textos grandes los pone render.py.
import cv2, numpy as np, subprocess, os
from PIL import Image, ImageDraw, ImageFont
FF=os.path.expanduser('~/arkamia-reels/bin/ffmpeg'); W,H,FPS,DUR=1080,1920,30,7.25
BG=cv2.imread('mapa_fondo.png').astype(np.float32)/255; BH,BW=BG.shape[:2]; k=BW/700          # puntos medidos en la previa de 700 px
P=lambda pts: np.array(pts,np.float32)*k
AMARAL=P([(355,985)]); SENDERO=P([(205,548)]); UT=P([(530,615)])
R1=P([(350,960),(345,845),(340,770),(333,660),(318,610),(268,575),(212,553)])                     # a Sendero por la avenida
R2=P([(350,960),(345,845),(352,770),(372,700),(420,660),(470,640),(525,622)])                     # a la UT
ease=lambda x: 0 if x<=0 else 1 if x>=1 else 1-(1-x)**3
inout=lambda x: 0 if x<=0 else 1 if x>=1 else .5-.5*np.cos(np.pi*x)
def back(p):
    p=min(max(p,0),1); c=1.7; return 1+(c+1)*(p-1)**3+c*(p-1)**2
PIN=np.asarray(Image.open('pin3d.png').convert('RGBA'),np.float32)/255; PIN=PIN[18:336,72:294]       # recorte al pin
FB=ImageFont.truetype(os.path.expanduser('~/Library/Fonts/SF-Pro-Display-Bold.otf') if os.path.exists(os.path.expanduser('~/Library/Fonts/SF-Pro-Display-Bold.otf')) else '/Library/Fonts/SF-Pro-Display-Bold.otf',46)
def label(txt):
    w=int(FB.getlength(txt))+56; h=86; im=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,w-1,h-1),radius=h//2,fill=(255,255,255,235)); d.text((28,14),txt,font=FB,fill=(35,38,48,255))
    return np.asarray(im,np.float32)/255
LAB={'Amaral':label('Amaral'),'Sendero':label('Sendero'),'UT':label('UT Santa Catarina')}
def over(img,rgba,x0,y0,a=1.):
    h,w=rgba.shape[:2]; X0,Y0,X1,Y1=max(int(x0),0),max(int(y0),0),min(int(x0)+w,W),min(int(y0)+h,H)
    if X1<=X0 or Y1<=Y0 or a<=0: return
    s=rgba[Y0-int(y0):Y1-int(y0),X0-int(x0):X1-int(x0)]; al=s[...,3:]*a
    img[Y0:Y1,X0:X1]=img[Y0:Y1,X0:X1]*(1-al)+s[...,:3][...,::-1]*al
def cam(t):   # push-in lento hacia el centro de la acción
    e=inout(t/DUR); z=1.0+0.10*e; hw,hh=BW/(2*z),BH/(2*z)
    cx=np.clip(BW*.5,hw,BW-hw); cy=np.clip(BH*(.56-.04*e),hh,BH-hh); return z,cx,cy   # nunca se sale del borde
def to_screen(pts,z,cx,cy):
    s=W/BW*z; return np.stack([(pts[:,0]-cx)*s+W/2,(pts[:,1]-cy)*s+H/2],1)
def partial(path,p):
    seg=np.linalg.norm(np.diff(path,axis=0),axis=1); L=seg.sum()*p; out=[path[0]]
    for a,b,l in zip(path[:-1],path[1:],seg):
        if L<=0: break
        f=min(L/l,1); out.append(a+(b-a)*f); L-=l
    return np.array(out)
def route(img,path,p,t):
    if p<=0: return
    pts=partial(path,p).astype(np.int32)
    glow=np.zeros((H,W),np.float32); cv2.polylines(glow,[pts],False,1.,26,cv2.LINE_AA); glow=cv2.GaussianBlur(glow,(0,0),10)*.55
    core=np.zeros((H,W),np.float32); cv2.polylines(core,[pts],False,1.,12,cv2.LINE_AA)
    col=np.array([165,251,253],np.float32)/255                                 # amarillo del logo #FDFBA5 (BGR)
    img[:]=img*(1-glow[...,None])+col*glow[...,None]; img[:]=img*(1-core[...,None])+np.array([1,1,1],np.float32)*core[...,None]
    # punto que avanza en la punta
    hx,hy=pts[-1]; cv2.circle(img,(int(hx),int(hy)),13,(1,1,1),-1,cv2.LINE_AA)
def pin(img,xy,t0,t,scale,name,lab_side=1):
    p=(t-t0)/.45
    if p<=0: return
    s=scale; ph=int(PIN.shape[0]*s); pw=int(PIN.shape[1]*s); spr=cv2.resize(PIN,(pw,ph),interpolation=cv2.INTER_AREA)
    drop=(1-ease(min(p,1)))*-260; sq=back(p) if p<1 else 1.
    x,y=xy
    sh=np.zeros((H,W),np.float32); cv2.ellipse(sh,(int(x),int(y)),(int(pw*.32),int(pw*.11)),0,0,360,1,-1); sh=cv2.GaussianBlur(sh,(0,0),6)*.45*min(p*2,1)
    img[:]=img*(1-sh[...,None])
    over(img,spr[...,[2,1,0,3]][...,::-1][...,[1,2,3,0]] if False else spr,x-pw/2,y-ph*sq+drop,min(p*3,1))
    lp=(t-t0-.25)/.3
    if lp>0:
        lb=LAB[name]; sc=back(lp) if lp<1 else 1.; lb=cv2.resize(lb,(max(int(lb.shape[1]*sc),2),max(int(lb.shape[0]*sc),2)))
        lx=x+lab_side*(pw*.55) if lab_side>0 else x-pw*.55-lb.shape[1]
        over(img,lb,lx,y-ph*.85-lb.shape[0]/2,min(lp*3,1))
p=subprocess.Popen([FF,'-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','14','-preset','slow','-pix_fmt','yuv420p','s5_base.mp4'],stdin=subprocess.PIPE)
for f in range(int(round(DUR*FPS))):
    t=f/FPS; z,cx,cy=cam(t); sc=W/BW*z
    M=np.float32([[sc,0,W/2-cx*sc],[0,sc,H/2-cy*sc]]); img=cv2.warpAffine(BG,M,(W,H),flags=cv2.INTER_AREA if sc<1 else cv2.INTER_LINEAR)
    route(img,to_screen(R1,z,cx,cy),inout((t-1.30)/1.10),t)
    route(img,to_screen(R2,z,cx,cy),inout((t-4.05)/1.20),t)
    A=to_screen(AMARAL,z,cx,cy)[0]; S=to_screen(SENDERO,z,cx,cy)[0]; U=to_screen(UT,z,cx,cy)[0]
    pin(img,S,2.40,t,.62,'Sendero',-1); pin(img,U,5.28,t,.62,'UT',-1); pin(img,A,.30,t,.85,'Amaral',1)
    p.stdin.write(np.clip(img*255,0,255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait(); print('ok')
