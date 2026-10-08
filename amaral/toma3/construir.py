# Toma 3 Amaral: drone aéreo, las casas se construyen en oleada desde el pórtico (tierra → obra negra → terminada)
# mientras la cámara (ventana 9:16 sobre la foto 16:9 4K) hace paneo a la derecha y frena sobre el pórtico.
import cv2, numpy as np, subprocess, os, sys
FF=os.path.expanduser('~/arkamia-reels/bin/ffmpeg'); FPS=30; DUR=float(sys.argv[1]) if len(sys.argv)>1 else 7.2
V=cv2.imread("aereo_vacio.png").astype(np.float32); C=cv2.imread("al_casas.png").astype(np.float32); O=cv2.imread("al_obra.png").astype(np.float32)
H,W=V.shape[:2]; s=W/1600
m=cv2.imread("mask_casas_raw.png",0)
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((61,61),np.uint8))
cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); m=cv2.drawContours(np.zeros_like(m),cs,-1,255,-1)   # sin huecos
P=lambda pts: (np.array(pts,np.float32)*s).astype(np.int32)
cv2.fillPoly(m,[P([(330,270),(560,215),(700,230),(1035,405),(1000,470),(760,560),(620,550),(470,450),(320,330)])],0)   # parque central
cv2.fillPoly(m,[P([(740,625),(815,470),(1215,458),(1350,520),(1360,893),(740,893)])],0)                                # pórtico
m=cv2.GaussianBlur(m.astype(np.float32)/255,(0,0),6)
cv2.imwrite("mask_final.png",(m*255).astype(np.uint8))
# retraso: distancia al pórtico + ruido por celdas (Voronoi) para que no sea una onda perfecta
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
px,py=1050*s,560*s; d=np.sqrt((xx-px)**2+((yy-py)*1.6)**2); d=(d-d[m>.5].min())/(np.percentile(d[m>.5],99)-d[m>.5].min())
rng=np.random.default_rng(7); seeds=rng.uniform([0,0],[W,H],(900,2)).astype(np.float32); jit=rng.uniform(-.28,.28,900).astype(np.float32)
small=(W//8,H//8); sy,sx=np.mgrid[0:small[1],0:small[0]].astype(np.float32)*8
best=np.full(sy.shape,1e18,np.float32); cell=np.zeros(sy.shape,np.float32)
for (cx,cy),j in zip(seeds,jit):
    dd=(sx-cx)**2+(sy-cy)**2; k=dd<best; best[k]=dd[k]; cell[k]=j
cell=cv2.resize(cell,(W,H),interpolation=cv2.INTER_NEAREST); cell=cv2.GaussianBlur(cell,(0,0),9)
# encuadre casi fijo sobre la manzana del fondo + pórtico; la obra avanza desde el pórtico hacia el fondo durante toda la frase
C0,C1,KD=1000*s,1060*s,.9
WW=int(H*9/16); vis=np.zeros((H,W),bool); vis[:,int(C0-WW/2):int(C1+WW/2)]=True
dv=d[(m>.5)&vis]; dn=(d-np.percentile(dv,1))/(np.percentile(dv,97)-np.percentile(dv,1))
delay=(0.4+4.6*np.clip(dn,0,1.08)+cell*.8).astype(np.float32); delay=np.clip(delay,0.3,5.4)
# --- construcción por PIEZAS (Liz: "no fade, que se vea por bloques") ---
# cada casa (componente de la diferencia obra-vs-vacío) se levanta por bloques de abajo hacia arriba;
# luego los acabados entran por piezas en orden salteado. Cada pieza cambia de golpe, sin fundido.
TS=26                                                  # tamaño de pieza en px (foto 4K)
dO=np.abs(cv2.GaussianBlur(O,(0,0),2)-cv2.GaussianBlur(V,(0,0),2)).max(2)
hm=((dO>30)&(m>.5)).astype(np.uint8)*255; hm=cv2.morphologyEx(hm,cv2.MORPH_OPEN,np.ones((7,7),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(hm)
gh,gw=H//TS+1,W//TS+1
cyc=(np.arange(gh)*TS+TS//2).clip(0,H-1); cxc=(np.arange(gw)*TS+TS//2).clip(0,W-1)
L=lab[cyc][:,cxc]                                      # casa de cada pieza
# partir cada hilera en casas: celdas Voronoi de ~170 px dentro de cada componente
r=np.random.default_rng(11)
sd=r.uniform([0,0],[W,H],(int(W*H/170**2),2)).astype(np.float32)
ty=(cyc[:,None]*np.ones((1,gw))).astype(np.float32); tx=(np.ones((gh,1))*cxc[None,:]).astype(np.float32)
cell_id=np.zeros((gh,gw),np.int32); bd=np.full((gh,gw),1e18,np.float32)
for k,(sx_,sy_) in enumerate(sd):
    dd=(tx-sx_)**2+(ty-sy_)**2; q=dd<bd; bd[q]=dd[q]; cell_id[q]=k
uid=np.where(L>0,L*len(sd)+cell_id,-1)
ids,inv=np.unique(uid,return_inverse=True); inv=inv.reshape(gh,gw)
ymn=np.full(len(ids),1e9,np.float32); ymx=np.full(len(ids),-1e9,np.float32)
np.minimum.at(ymn,inv.ravel(),ty.ravel()); np.maximum.at(ymx,inv.ravel(),ty.ravel())
off=r.uniform(-.25,.25,len(ids)).astype(np.float32)                 # cada casa arranca a su ritmo
dur=r.uniform(.45,.8,len(ids)).astype(np.float32)                   # y tarda distinto en levantarse
# cada COLUMNA de bloques crece desde su propio piso (nada flota): base y azotea por (casa, columna)
colid=np.where(L>0,L*gw+np.arange(gw)[None,:],-1); cids,cinv=np.unique(colid,return_inverse=True); cinv=cinv.reshape(gh,gw)
cmn=np.full(len(cids),1e9,np.float32); cmx=np.full(len(cids),-1e9,np.float32)
np.minimum.at(cmn,cinv.ravel(),ty.ravel()); np.maximum.at(cmx,cinv.ravel(),ty.ravel())
rise=np.where(uid>=0,(cmx[cinv]-ty)/np.maximum(cmx[cinv]-cmn[cinv],TS),.5)
dg=cv2.resize(delay,(gw,gh),interpolation=cv2.INTER_AREA)+np.where(uid>=0,off[inv],0)
t1=dg+dur[inv]*np.clip(rise,0,1)+r.uniform(0,.07,(gh,gw))            # hiladas de abajo hacia arriba, orilla irregular
t2=dg+dur[inv]+0.25+r.uniform(0,.55,(gh,gw))+0.12*np.clip(rise,0,1)  # acabados por piezas salteadas
t1=t1.astype(np.float32); t2=t2.astype(np.float32)
def grid(g): return cv2.resize(g,(gw*TS,gh*TS),interpolation=cv2.INTER_NEAREST)[:H,:W]
T1,T2=grid(t1),grid(t2)
sm=lambda x: np.clip(x,0,1)**2*(3-2*np.clip(x,0,1))
# cámara: ventana 9:16 (alto completo) con paneo a la derecha que frena sobre el pórtico + leve push-in
def cam(t):
    u=min(t/(DUR*KD),1); e=1-(1-u)**3                  # ease-out: frena en seco al final
    return C0+(C1-C0)*e-WW/2, 1.0+0.07*e
out=subprocess.Popen([FF,'-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1080x1920','-r',str(FPS),'-i','-','-c:v','libx264','-crf','14','-preset','slow','-pix_fmt','yuv420p','s3_base.mp4'],stdin=subprocess.PIPE)
N=int(round(DUR*FPS))
for f in range(N):
    t=f/FPS; x0,z=cam(t); w=WW/z; h=H/z; cx=x0+WW/2; cy=H/2+ (H-h)*0.08
    X0=int(max(cx-w/2,0)); X1=int(min(cx+w/2,W)); Y0=int(max(cy-h/2,0)); Y1=int(min(cy+h/2,H))
    sl=(slice(Y0,Y1),slice(X0,X1)); mm=m[sl][...,None]
    p1=(t>=T1[sl]).astype(np.float32)[...,None]; p2=(t>=T2[sl]).astype(np.float32)[...,None]   # cada pieza aparece de golpe
    house=V[sl]*(1-p1)+O[sl]*p1; house=house*(1-p2)+C[sl]*p2
    fr=V[sl]*(1-mm)+house*mm
    fr=cv2.resize(fr,(1080,1920),interpolation=cv2.INTER_AREA)
    out.stdin.write(np.clip(fr,0,255).astype(np.uint8).tobytes())
out.stdin.close(); out.wait(); print("ok",N)
