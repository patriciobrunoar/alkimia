"""Generate one voiceover clip per subtitle line with Google Cloud Text-to-Speech.

Setup:  Google Cloud project with "Cloud Text-to-Speech API" enabled + an API key restricted to that API.
Run:    GCLOUD_TTS_KEY=your-key python3 gcloud_tts.py                       (default: en-US-Chirp3-HD-Charon)
        GCLOUD_TTS_KEY=your-key python3 gcloud_tts.py en-US-Studio-Q        (any voice from the Cloud voice list)
Output: clips/01.wav, clips/02.wav, ... one per cue in ../timeline.js (no extra packages needed).
"""
import base64, json, os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = sys.argv[1] if len(sys.argv) > 1 else "en-US-Chirp3-HD-Charon"
RATE = float(os.environ.get("RATE", "0.95"))  # 1.0 = normal speed
KEY = os.environ.get("GCLOUD_TTS_KEY") or sys.exit("Set GCLOUD_TTS_KEY first")

src = open(os.path.join(HERE, "..", "timeline.js")).read()
cues = json.loads(src[src.index("window.TIMELINE =") + 17:].strip().rstrip(";"))["cues"]
os.makedirs(os.path.join(HERE, "clips"), exist_ok=True)

for i, (start, end, text) in enumerate(cues, 1):
    body = {"input": {"text": text.replace("myalkimia.com", "my alkimia dot com")},
            "voice": {"languageCode": "-".join(VOICE.split("-")[:2]), "name": VOICE},
            "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 48000, "speakingRate": RATE}}
    req = urllib.request.Request(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={KEY}",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    try:
        audio = base64.b64decode(json.load(urllib.request.urlopen(req, timeout=60))["audioContent"])
    except urllib.error.HTTPError as e:
        sys.exit(f"Line {i} failed: {e.code} {e.read().decode()[:300]}")
    out = os.path.join(HERE, "clips", f"{i:02d}.wav")
    open(out, "wb").write(audio)  # LINEAR16 comes back as a complete WAV file
    secs = (len(audio) - 44) / 96000
    flag = "  <-- longer than its subtitle window" if secs > end - start + 0.3 else ""
    print(f"{i:02d}.wav  {secs:4.1f}s (window {end - start:.1f}s)  {text}{flag}")
