#!/usr/bin/env python3
"""Loop musicale senza stacco per il gioco.

    python3 tools/music.py <ingresso.mp3> <uscita.mp3> [--durata 42] [--strumentale]

Procedimento (collaudato su Warm Memories / Paper Lantern Promise):
 1. decodifica in wav (ffmpeg completo di imageio-ffmpeg: quello di sistema
    può mancare del decoder mp3);
 2. (--strumentale) attenua la voce: mid/side — il canale centrale (dove sta
    la voce) viene ridotto, i bassi centrali reintegrati;
 3. cerca la finestra di N secondi PIÙ UNIFORME del brano (scansione RMS a
    blocchi: minima varianza) → niente attacchi/stacchi dentro il loop;
 4. chiude il loop con crossfade equal-power di 1.5 s (overlap-add numpy:
    la coda sfuma sull'inizio) → giunzione senza discontinuità;
 5. ricodifica mp3 192k.
"""
import os, subprocess, sys, tempfile
import numpy as np

def ffmpeg_bin():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return 'ffmpeg'

SR = 44100

def decodifica(src, strumentale):
    fd, wav = tempfile.mkstemp(suffix='.wav'); os.close(fd)
    filtro = []
    if strumentale:
        # mid/side: voce (centro) a 0.35, bassi centrali (<180Hz) reintegrati
        filtro = ['-filter_complex',
                  'asplit=2[full][x];[full]lowpass=f=180[bass];'
                  '[x]stereotools=mlev=0.35[body];'
                  '[bass][body]amix=inputs=2:normalize=0']
    subprocess.check_call([ffmpeg_bin(), '-y', '-i', src, *filtro,
                           '-ar', str(SR), '-ac', '2', wav],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import wave
    w = wave.open(wav)
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16)\
          .reshape(-1, 2).astype(np.float32) / 32768
    w.close(); os.remove(wav)
    return a

def finestra_uniforme(a, durata):
    """Inizio della finestra di `durata` secondi con RMS più costante."""
    blocco = SR // 2                                  # mezzo secondo
    rms = np.sqrt((a**2).mean(axis=1))
    nb = len(rms) // blocco
    r = np.sqrt((rms[:nb*blocco].reshape(nb, blocco)**2).mean(axis=1))
    L = int(durata * 2)                               # blocchi nella finestra
    if nb <= L: return 0
    var = np.array([r[i:i+L].std() / (r[i:i+L].mean() + 1e-9) for i in range(nb - L)])
    lo = min(4, len(var)-1)                           # evita il fade-in iniziale
    return (lo + int(np.argmin(var[lo:]))) * blocco

def chiudi_loop(seg, fade=1.5):
    n = int(fade * SR)
    testa, corpo, coda = seg[:n], seg[n:-n], seg[-n:]
    t = np.linspace(0, np.pi/2, n, dtype=np.float32)[:, None]
    unione = coda * np.cos(t) + testa * np.sin(t)     # equal-power
    return np.concatenate([unione, corpo])

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 2: sys.exit(__doc__)
    src, dst = args
    durata = 42.0
    if '--durata' in sys.argv: durata = float(sys.argv[sys.argv.index('--durata')+1])
    strumentale = '--strumentale' in sys.argv
    a = decodifica(src, strumentale)
    i0 = finestra_uniforme(a, durata)
    seg = a[i0:i0 + int(durata*SR)]
    loop = chiudi_loop(seg)
    # verifica giunzione: differenza campione a cavallo del punto di loop
    salto = float(np.abs(loop[0] - loop[-1]).max())
    fd, wav = tempfile.mkstemp(suffix='.wav'); os.close(fd)
    import wave
    w = wave.open(wav, 'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(loop, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    subprocess.check_call([ffmpeg_bin(), '-y', '-i', wav, '-b:a', '192k', dst],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(wav)
    print(f'{dst}: loop {durata:.0f}s da t={i0/SR:.1f}s'
          f'{" (strumentale)" if strumentale else ""} · discontinuità {salto:.4f} · '
          f'{os.path.getsize(dst)//1024} KB')

if __name__ == '__main__':
    main()
