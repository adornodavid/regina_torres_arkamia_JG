# Voz recortada por toma + whoosh/whip en cada corte + pop en cada píldora + música baja.
import subprocess, os
FF = os.path.expanduser('~/arkamia-reels/bin/ffmpeg'); SFX = '../../work/sfx_ocular/'
TL = [l.split() for l in open('timeline.txt')]
inp, flt, labels = [], [], []
for i, (n, T0, a, b, hold) in enumerate(TL):
    inp += ['-i', f'../clips/t{n}.mp4']; T0, a, b = float(T0), float(a), float(b)
    flt.append(f"[{i}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={b-a-0.02}:d=0.02,adelay={int(T0*1000)}|{int(T0*1000)}[v{i}]"); labels.append(f'[v{i}]')
k = len(TL); cuts = [float(t[1]) for t in TL[1:]]
sfx = []
for j, c in enumerate(cuts):                       # pico del whoosh justo en el corte
    f, pk, vol = (SFX + 'whoosh06.wav', 1.284, .45) if j % 2 == 0 else (SFX + 'whip16.wav', .082, .55)
    sfx.append((f, c - pk, vol))
T4 = float(TL[3][1]); a4 = float(TL[3][2])
for tp in (2.34, 3.80, 4.72, 5.50, 6.10, 6.82): sfx.append(('../../work/pop_pin.mp3', T4 + tp - a4 - .118 + .05, .30))
for f, st, vol in sfx:
    inp += ['-i', f]; d = max(int(st*1000), 0)
    flt.append(f"[{k}:a]{'atrim=start=%.3f,asetpts=PTS-STARTPTS,' % (-st) if st < 0 else ''}volume={vol},adelay={d}|{d}[s{k}]"); labels.append(f'[s{k}]'); k += 1
dur = float(TL[-1][1]) + float(TL[-1][3]) - float(TL[-1][2]) + float(TL[-1][4])
inp += ['-i', os.path.expanduser('~/arkamia-reels/music/hotel-lounge-elegante.m4a')]
flt.append(f"[{k}:a]atrim=0:{dur},volume=0.13,afade=t=in:d=0.4,afade=t=out:st={dur-0.8}:d=0.8[m]"); labels.append('[m]')
flt.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,atrim=0:{dur},loudnorm=I=-14:TP=-1.5:LRA=11[out]")
subprocess.run([FF, '-v', 'error', '-y', *inp, '-filter_complex', ';'.join(flt), '-map', '[out]', '-ar', '48000', '-c:a', 'pcm_s16le', 'mezcla.wav'], check=True)
print('ok', dur)
