# Mezcla del reel Alboradas: voz original de Barbara por toma + whoosh/whip en cada corte + pop por amenidad
# + tecleo en terraregia.com + música baja que sube en el cierre (regla de David) + loudnorm -14 LUFS.
import subprocess, numpy as np
VOZ = {1: 'T1', 2: 'T2', 3: 'T3a', 4: 'T4a', 5: 'T5', 6: 'T6a', 7: 'T6b', 8: 'T7', 9: 'T8'}
TL = [l.split() for l in open('timeline.txt')]
seg = {int(n): (float(T0), float(a), float(b), float(h)) for n, T0, a, b, h in TL}
dur = max(T0 + b - a + h for T0, a, b, h in seg.values())
MUSIC = '/Users/davidadorno/Proyectos/tr-regina-castelo/broll/music_v4_afrohouse_vocal.mp3'
inp, flt, lab = [], [], []
def add(path, delay, vol, trim=None, extra=''):
    i = len(inp) // 2; inp.extend(['-i', path])
    t = f'atrim={trim[0]}:{trim[1]},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={trim[1]-trim[0]-0.03}:d=0.03,' if trim else ''
    d = max(int(delay * 1000), 0)
    flt.append(f'[{i}:a]{t}aformat=channel_layouts=stereo,volume={vol}{extra},adelay={d}|{d}[x{i}]'); lab.append(f'[x{i}]')
for n, (T0, a, b, h) in seg.items():
    if n in VOZ: add(f'../tomas/{VOZ[n]}.mp4', T0, 1.0, (a, b))
cuts = sorted(T0 for n, (T0, a, b, h) in seg.items() if n > 1)
for j, c in enumerate(cuts):
    if j % 2 == 0: add('sfx/whoosh.mp3', c - 0.45, 0.40)
    else: add('sfx/whip.mp3', c - 0.12, 0.45)
T0, a, b, h = seg[5]
for tp in (1.37, 2.07, 3.01, 3.87, 4.53, 5.57, 6.71): add('sfx/pop.mp3', T0 + tp - a, 0.30)
T0, a, b, h = seg[9]; add('sfx/type.mp3', T0 + 2.21 - a, 0.30)
# música: cama baja (0.11) y sube a 0.45 en el cierre (después de la última palabra de Regina)
t_up = seg[10][0] - 0.3
i = len(inp) // 2; inp.extend(['-i', MUSIC])
flt.append(f"[{i}:a]atrim=0:{dur},asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo,"
           f"volume='if(lt(t,{t_up}),0.11,0.11+0.34*min(1,(t-{t_up})/0.6))':eval=frame,afade=t=in:d=0.5,afade=t=out:st={dur-0.9}:d=0.9[m]"); lab.append('[m]')
flt.append(f"{''.join(lab)}amix=inputs={len(lab)}:normalize=0,atrim=0:{dur},loudnorm=I=-14:TP=-1.5:LRA=11[out]")
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inp, '-filter_complex', ';'.join(flt), '-map', '[out]', '-ar', '48000', '-c:a', 'pcm_s16le', 'mezcla.wav'], check=True)
print('ok', round(dur, 2))
