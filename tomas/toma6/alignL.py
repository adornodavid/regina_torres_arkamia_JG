import cv2, numpy as np
ref = cv2.imread('refL.png'); Hh, Ww = ref.shape[:2]
sift = cv2.SIFT_create(8000); bf = cv2.BFMatcher(); gr = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
park = np.zeros_like(gr); park[int(Hh*.30):int(Hh*.75), :] = 255
kr, dr = sift.detectAndCompute(gr, park)
def align(path, out):
    im = cv2.resize(cv2.imread(path), (Ww, Hh), interpolation=cv2.INTER_LANCZOS4); g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    k, d = sift.detectAndCompute(g, None); m = [a for a, b in bf.knnMatch(d, dr, k=2) if a.distance < .7*b.distance]
    H, inl = cv2.findHomography(np.float32([k[a.queryIdx].pt for a in m]), np.float32([kr[a.trainIdx].pt for a in m]), cv2.RANSAC, 3.0)
    print(path, len(m), int(inl.sum())); w = cv2.warpPerspective(im, H, (Ww, Hh), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    cv2.imwrite(out, w); return w
fin = align('casas_finL.png', 'finL_al.png'); obra = align('casas_obraL.png', 'obraL_al.png')
for n, a in (('refL', ref), ('finL', fin)):
    a = a.copy()
    for x in range(0, Ww, 200): cv2.line(a, (x, 0), (x, Hh), (0, 255, 255), 2); cv2.putText(a, str(x), (x+4, 40), 0, 1.4, (0, 255, 255), 3)
    for y in range(0, Hh, 100): cv2.line(a, (0, y), (Ww, y), (0, 255, 255), 2); cv2.putText(a, str(y), (4, y-6), 0, 1.4, (0, 255, 255), 3)
    cv2.imwrite(n + '_grid.jpg', cv2.resize(a, None, fx=.3, fy=.3))
