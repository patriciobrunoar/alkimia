"""Fit the video timeline to a recorded voiceover take.

Takes one continuous read of the script (paragraphs separated by pauses), speeds it up slightly
without changing pitch, finds the paragraph and line breaks from its pauses, and then:
  - rewrites ../timeline.js: scene lengths/speeds built around each paragraph, subtitle cues on the spoken words
  - writes voice-aligned.wav: the voice placed on the new timeline (48 kHz stereo), mixed in by ../audio.py

Usage: python3 align.py [take.wav] [tempo]      (defaults: charon-full.wav, 1.06)
Needs ffmpeg (FFMPEG env var, imageio-ffmpeg, or on PATH).
"""
import json, os, re, subprocess, sys, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TAKE = os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else "charon-full.wav")
TEMPO = float(sys.argv[2]) if len(sys.argv) > 2 else 1.06
SR = 48000
LEAD, TAIL, END_HOLD = 0.35, 0.6, 2.0          # seconds before each paragraph, after it, and after the last one
CONTENT = [6, 6.5, 9, 10.5, 10.5, 9.5, 6, 6]    # animation length each scene was authored for (scene-local seconds)
# which subtitle cues belong to which paragraph/scene (cue indexes, 0-based)
GROUPS = [[0, 1, 2], [3, 4], [5, 6, 7], [8, 9, 10], [11, 12, 13], [14, 15], [16, 17, 18], [19]]


def ffmpeg():
    if os.environ.get("FFMPEG"): return os.environ["FFMPEG"]
    try:
        import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def load(path):
    with wave.open(path) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(float) / 32768
        return x.reshape(-1, w.getnchannels()).mean(1)


# 1) speed up (pitch preserved) and resample to 48 kHz mono
tmp = os.path.join(HERE, ".tempo.wav")
subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", TAKE, "-af", f"atempo={TEMPO}", "-ar", str(SR), "-ac", "1", tmp], check=True)
v = load(tmp); os.remove(tmp)

# 2) speech/silence map (10 ms frames)
hop = SR // 100
db = 20 * np.log10(np.sqrt(np.convolve(v ** 2, np.ones(hop) / hop, "same")[::hop]) + 1e-9)
speech = db > db.max() - 38
on = np.where(speech)[0]; t0, t1 = on[0] / 100, on[-1] / 100 + 0.01
pauses, i = [], 0
while i < len(speech):
    if not speech[i]:
        j = i
        while j < len(speech) and not speech[j]: j += 1
        if (j - i) >= 20 and i / 100 > t0 and j / 100 < t1: pauses.append((i / 100, j / 100))
        i = j
    else: i += 1

# 3) paragraph breaks = the 7 longest pauses
breaks = sorted(sorted(pauses, key=lambda p: p[1] - p[0], reverse=True)[:len(GROUPS) - 1])
paras = [(t0 if k == 0 else breaks[k - 1][1], t1 if k == len(GROUPS) - 1 else breaks[k][0]) for k in range(len(GROUPS))]

src = open(os.path.join(HERE, "..", "timeline.js")).read()
head, body = src[:src.index("window.TIMELINE =")], src[src.index("window.TIMELINE =") + 17:].strip().rstrip(";")
TL = json.loads(body)
texts = [c[2] for c in TL["cues"]]

# 4) new scenes, subtitle cues, and the placed voice track
scenes, cues, out, cursor = [], [], np.zeros(0), 0.0
for k, ((a, b), group) in enumerate(zip(paras, GROUPS)):
    start = cursor
    vstart = start + LEAD + (0.05 if k == 0 else 0)
    dur = LEAD + (b - a) + (END_HOLD if k == len(GROUPS) - 1 else TAIL)
    end = round(start + dur, 2)
    scenes.append([round(start, 2), end, round(float(np.clip(CONTENT[k] / dur, 0.55, 1.3)), 3)])
    # line breaks inside the paragraph: split by text length, snapped to a nearby pause
    inner = [p for p in pauses if a < p[0] and p[1] < b]
    chars = [len(texts[c]) for c in group]; bounds = [a]
    for n in range(1, len(group)):
        guess = a + (b - a) * sum(chars[:n]) / sum(chars)
        near = min(inner, key=lambda p: abs((p[0] + p[1]) / 2 - guess), default=None)
        bounds.append(((near[0] + near[1]) / 2) if near and abs((near[0] + near[1]) / 2 - guess) < 0.8 else guess)
    bounds.append(b)
    for n, c in enumerate(group):
        cs = vstart + bounds[n] - a - (0.12 if n == 0 else 0)
        ce = vstart + bounds[n + 1] - a + (0.25 if n == len(group) - 1 else 0)
        cues.append([round(cs, 2), round(ce, 2), texts[c]])
    seg = v[int(a * SR):int(b * SR)]
    need = int(vstart * SR) - len(out)
    out = np.concatenate([out, np.zeros(max(0, need)), seg])
    cursor = end
    print(f"scene {k + 1}: {start:5.2f}-{end:5.2f}  voice {vstart:5.2f}-{vstart + b - a:5.2f}  speed {scenes[-1][2]}")

TL["duration"] = scenes[-1][1]; TL["scenes"] = scenes; TL["cues"] = cues
fmt = lambda rows: "[\n" + ",\n".join("    " + json.dumps(r, ensure_ascii=False) for r in rows) + "\n  ]"
with open(os.path.join(HERE, "..", "timeline.js"), "w") as f:
    f.write(head + "window.TIMELINE = {\n  \"duration\": %s,\n  \"scenes\": %s,\n  \"cues\": %s\n};\n" % (TL["duration"], fmt(scenes), fmt(cues)))

out = np.concatenate([out, np.zeros(int(TL["duration"] * SR) - len(out))])[:int(TL["duration"] * SR)]
out = np.clip(out * (0.9 / np.max(np.abs(out))), -1, 1)
pcm = (np.repeat(out[:, None], 2, 1) * 32767).astype("<i2")
with wave.open(os.path.join(HERE, "voice-aligned.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f"duration {TL['duration']}s  ->  timeline.js + voice-aligned.wav")
