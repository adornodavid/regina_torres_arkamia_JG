# Homografías cuadro → referencia (cuadro 150) sobre el drone horizontal 3414x1920
import cv2, numpy as np
cap = cv2.VideoCapture('droneL.mp4'); fr = []
while True:
    r, f = cap.read()
    if not r: break
    fr.append(cv2.resize(f, (1707, 960)))
N = len(fr); R = 150; s = 1.
sift = cv2.SIFT_create(5000); bf = cv2.BFMatcher()
def kd(f): return sift.detectAndCompute(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), None)
kr, dr = kd(fr[R]); Hs = []
for j, f in enumerate(fr):
    k, d = kd(f); m = [a for a, b in bf.knnMatch(d, dr, k=2) if a.distance < .7*b.distance]
    H, inl = cv2.findHomography(np.float32([k[a.queryIdx].pt for a in m]), np.float32([kr[a.trainIdx].pt for a in m]), cv2.RANSAC, 2.5)
    Hs.append(np.diag([2, 2, 1.]) @ H @ np.diag([.5, .5, 1.]))       # a escala 3414x1920
    if j % 50 == 0: print(j, len(m), int(inl.sum()), flush=True)
np.save('HL_to_ref.npy', np.array(Hs)); print('N', N)
cap = cv2.VideoCapture('droneL.mp4'); cap.set(cv2.CAP_PROP_POS_FRAMES, R); _, ref = cap.read(); cv2.imwrite('refL.png', ref)
corn = np.float32([[0, 0], [3414, 0], [3414, 1920], [0, 1920]])
P = np.array([cv2.perspectiveTransform(corn[None], h)[0] for h in Hs]).reshape(-1, 2); print('bbox', P.min(0).round(), P.max(0).round())
