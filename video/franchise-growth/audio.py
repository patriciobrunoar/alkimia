"""Synthesises the 60s sound bed (music + sound design) for the Franchise Growth Systems video.

Leaves headroom in the 200 Hz–4 kHz range for the voiceover. Event times match index.html.
Usage: python3 audio.py soundtrack.wav
"""
import sys, wave, json, os
import numpy as np

_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "timeline.js")).read()
TL = json.loads(_src[_src.index("window.TIMELINE =") + 17:].strip().rstrip(";"))
SCENES = TL["scenes"]
OLD_STARTS = [0, 5, 10, 20, 30, 40, 50, 55]  # event times below are authored on the original 60s cut


def T(o):
    """Map a time on the original 60s cut to the current timeline (per-scene offset + speed)."""
    k = max(i for i, a in enumerate(OLD_STARTS) if o >= a)
    a, b, speed = SCENES[k]
    return a + (o - OLD_STARTS[k]) / speed


def S(k): return SCENES[k][0]  # scene start (0-based index)


SR, DUR = 48000, float(TL["duration"])
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(4)
L = np.zeros(N); R = np.zeros(N)


def env(n, a, d):  # attack / exponential decay envelope (seconds)
    x = np.arange(n) / SR
    return np.minimum(1, x / max(a, 1e-4)) * np.exp(-x / d)


def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); j = min(N, i + len(sig))
    if i >= N or j <= i: return
    s = sig[: j - i] * gain
    L[i:j] += s * np.sqrt((1 - pan) / 2) * 1.414
    R[i:j] += s * np.sqrt((1 + pan) / 2) * 1.414


def lowpass(x, fc):  # one-pole
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); acc = 0.0
    for k in range(len(x)): acc = (1 - a) * x[k] + a * acc; y[k] = acc
    return y


def noise(sec): return rng.standard_normal(int(sec * SR))


def hz(note): return 440 * 2 ** ((note - 69) / 12)


# ---- pad: warm detuned chords, slow swells -------------------------------------------------
CHORDS = [(S(0), [50, 57, 60, 64, 69]), (S(2), [46, 53, 57, 62, 65]), (S(3), [41, 48, 57, 60, 64]),
          (S(4), [48, 55, 59, 62, 67]), (S(5), [50, 57, 62, 65, 69]), (S(6), [46, 53, 58, 62, 69]), (S(7), [41, 48, 57, 60, 65, 72])]
pad = np.zeros(N)
for idx, (start, notes) in enumerate(CHORDS):
    end = CHORDS[idx + 1][0] if idx + 1 < len(CHORDS) else DUR
    i, j = int(start * SR), int(min(DUR, end + 1.2) * SR)
    tt = t[i:j] - start
    seg = np.zeros(j - i)
    for n in notes:
        f = hz(n)
        for det in (-0.12, 0.11):
            ph = 2 * np.pi * f * (1 + det / 100) * tt
            seg += (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)) / len(notes)
    fade = np.minimum(1, tt / 1.2) * np.clip((end + 1.2 - start - tt) / 1.2, 0, 1)
    pad[i:j] += seg * fade
pad *= 0.55 + 0.45 * np.sin(2 * np.pi * t / 7.5) ** 2
pad = lowpass(pad, 1800)
intens = np.interp(t, [0, T(5), S(2), S(3), S(6), S(7), S(7) + 3, DUR], [0.35, 0.5, 0.7, 0.8, 0.8, 0.6, 0.9, 0.0])
add(pad * intens, 0, 0.16)

# ---- sub pulse (100 bpm) from the bridge to the zoom-out, side-chained pad feel ------------
beat = 60 / 100
kick_t = np.arange(int(0.45 * SR)) / SR
kick = np.sin(2 * np.pi * (45 * kick_t + 60 * (1 - np.exp(-kick_t * 30)) / 30)) * env(len(kick_t), 0.002, 0.16)
for k in range(int((S(6) - S(2)) / beat)):
    at = S(2) + k * beat
    add(kick, at, 0.36 if at < S(3) else 0.42)
    if at >= S(3) and at < S(6):  # soft shaker on the off-beat
        sh = np.diff(noise(0.07), prepend=0) * env(int(0.07 * SR), 0.003, 0.02)
        add(sh, at + beat / 2, 0.035, pan=0.3 if k % 2 else -0.3)

# ---- riser (0–5s) ------------------------------------------------------------------------------
RL = T(5); n = int(RL * SR); rt = np.arange(n) / SR
riser = np.sin(2 * np.pi * np.cumsum(np.interp(rt, [0, RL], [38, 110])) / SR) * (rt / RL) ** 1.5
riser += lowpass(noise(RL), 900)[:n] * 3 * (rt / RL) ** 2
add(riser, 0, 0.22)


# ---- sound-design one-shots -----------------------------------------------------------------------
def whoosh(sec=0.7, fc=1400):
    x = lowpass(noise(sec), fc) * 4; k = np.arange(len(x)) / len(x)
    return x * np.sin(np.pi * k) ** 2


def blip(f, sec=0.09, a=0.004, d=0.04):
    k = np.arange(int(sec * SR)) / SR
    return np.sin(2 * np.pi * f * k) * env(len(k), a, d)


def glitch():
    x = np.sign(np.sin(2 * np.pi * rng.uniform(300, 900) * np.arange(int(0.06 * SR)) / SR))
    return x * env(len(x), 0.001, 0.02) * 0.6


def impact(sec=2.5):
    k = np.arange(int(sec * SR)) / SR
    sub = np.sin(2 * np.pi * (32 * k + 50 * (1 - np.exp(-k * 6)) / 6)) * env(len(k), 0.003, 0.9)
    return sub + lowpass(noise(sec), 2500) * env(len(k), 0.001, 0.12) * 1.2


for c in (0.55, 1.1, 1.6, 2.1, 2.55, 3.0, 3.3):
    add(whoosh(0.25, 3000), T(c) - 0.08, 0.10, pan=rng.uniform(-.5, .5)); add(blip(1800, .05, .001, .015), T(c), 0.05)
add(whoosh(1.4, 1200), T(3.4), 0.14)
for k in range(14):  # guidelines breaking down across the map
    add(glitch(), T(6.1 + k * 0.23) + rng.uniform(0, .08), 0.06, pan=rng.uniform(-.7, .7))
add(impact(), S(2), 0.5)
add(whoosh(1.1, 2200), T(11.0), 0.10)
for k, f in enumerate((660, 880, 990, 1320)): add(blip(f, .5, .01, .25), T(13.2 + k * 0.22), 0.05)
add(whoosh(1.0, 1800), T(14.4), 0.12); add(blip(1760, .8, .02, .4), T(14.7), 0.04)
add(whoosh(1.2, 1100), T(15.4), 0.12)
for k in range(9): add(blip(1200 + 90 * k, .08), T(16.5 + k * 0.13), 0.035, pan=rng.uniform(-.5, .5))
for sc in (1, 3, 4, 5, 6, 7): add(whoosh(0.8, 1600), S(sc) - 0.55, 0.14)  # scene transitions
for k in range(5): add(blip(990 + 110 * k), T(21.5 + k * 0.55), 0.05)
for k in range(3): add(blip(740 + 260 * k, .3, .005, .12), T(22.2 + k * 3.2), 0.07)
for at in (30.5, 31.0, 31.6):
    add(whoosh(0.45, 2600), T(at) - .05, 0.08); add(blip(420, .08, .001, .02), T(at + .6), 0.10); add(blip(2400, .05, .001, .01), T(at + .6), 0.04)
for k in range(5): add(blip(1320, .12, .002, .05), T(31.75 + k * 0.45), 0.05)
for k in range(3): add(blip(520, .1, .001, .03), T(32.4 + k * 0.4), 0.08)
add(blip(1560, .15, .002, .06), T(33.7), 0.05)
for k in range(3): add(blip(330 * (k + 2), .4, .005, .2), T(44.4 + k * 0.25), 0.07)
add(whoosh(1.2, 1500), T(45.2), 0.09); add(blip(880, 1.0, .01, .5), T(46.3), 0.06); add(blip(1320, .6, .01, .3), T(47.5), 0.06)
for k, lt in enumerate((0.35, 2.1, 3.85)):  # "Assess. Enable. Scale." word hits
    add(impact(1.0) * .5, S(6) + lt, 0.3); add(blip(440 * (k + 2), .6, .005, .25), S(6) + lt, 0.09)
add(blip(2640, 1.2, .01, .6), T(53.0), 0.03)
add(impact(3.5), S(7), 0.45)
for k, f in enumerate((1047, 1319, 1568)): add(blip(f, 1.8, .02, .9), T(56.4 + k * 0.12), 0.03)

# ---- master ---------------------------------------------------------------------------------------
fade = np.clip((DUR - t) / 1.2, 0, 1) * np.clip(t / 0.08, 0, 1)
st = np.stack([L * fade, R * fade], 1)
st = np.tanh(st * 1.4) / 1.4  # soft clip
st *= 0.89 / np.max(np.abs(st))
out = (st * 32767).astype("<i2")
with wave.open(sys.argv[1] if len(sys.argv) > 1 else "soundtrack.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print("wrote", len(out) / SR, "s")
