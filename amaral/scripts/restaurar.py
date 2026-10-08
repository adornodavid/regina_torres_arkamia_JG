# Restauración de voz local (resemble-enhance): dereverb + denoise + timbre de estudio. Uso: restaurar.py in.wav out.wav [lambd]
import sys, torch, torchaudio
from pathlib import Path
from resemble_enhance.enhancer.inference import enhance
src, dst = sys.argv[1], sys.argv[2]; lambd = float(sys.argv[3]) if len(sys.argv) > 3 else 0.9
wav, sr = torchaudio.load(src); wav = wav.mean(0)
dev = "mps" if torch.backends.mps.is_available() else "cpu"
try: out, osr = enhance(wav, sr, dev, nfe=64, solver="midpoint", lambd=lambd, tau=0.5, run_dir=Path("modelo/enhancer_stage2"))
except Exception as e:
    print("mps falló, uso cpu:", str(e)[:120]); out, osr = enhance(wav, sr, "cpu", nfe=64, solver="midpoint", lambd=lambd, tau=0.5, run_dir=Path("modelo/enhancer_stage2"))
torchaudio.save(dst, out[None].cpu(), osr); print("ok", osr, out.shape[0]/osr)
