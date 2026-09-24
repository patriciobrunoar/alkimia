"""Generate one voiceover clip per subtitle line with the Gemini API (Google AI Studio key).

Setup:  get a free API key at https://aistudio.google.com/apikey
Run:    GEMINI_API_KEY=your-key python3 gemini_tts.py            (default voice: Charon)
        GEMINI_API_KEY=your-key python3 gemini_tts.py Kore       (any AI Studio voice name)
Output: clips/01.wav, clips/02.wav, ... one per cue in ../timeline.js (no extra packages needed).
"""
import base64, json, os, sys, time, urllib.request, wave

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-2.5-pro-preview-tts")  # or gemini-2.5-flash-preview-tts
VOICE = sys.argv[1] if len(sys.argv) > 1 else "Charon"
STYLE = ("Read as a premium B2B brand video voiceover: calm, confident and warm, like a trusted strategy "
         "advisor, medium-slow pace, not salesy. Say: ")
KEY = os.environ.get("GEMINI_API_KEY") or sys.exit("Set GEMINI_API_KEY first (https://aistudio.google.com/apikey)")

src = open(os.path.join(HERE, "..", "timeline.js")).read()
cues = json.loads(src[src.index("window.TIMELINE =") + 17:].strip().rstrip(";"))["cues"]
os.makedirs(os.path.join(HERE, "clips"), exist_ok=True)

for i, (start, end, text) in enumerate(cues, 1):
    spoken = text.replace("myalkimia.com", "my alkimia dot com")
    body = {"contents": [{"parts": [{"text": STYLE + spoken}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
    for attempt in range(5):
        try:
            res = json.load(urllib.request.urlopen(req, timeout=120)); break
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 4: sys.exit(f"Line {i} failed: {e.code} {e.read().decode()[:300]}")
            time.sleep(20 * (attempt + 1))  # free tier rate limit: wait and retry
    pcm = base64.b64decode(res["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    out = os.path.join(HERE, "clips", f"{i:02d}.wav")
    with wave.open(out, "wb") as w:  # Gemini returns 24 kHz, 16-bit mono PCM
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
    secs = len(pcm) / 48000
    flag = "  <-- longer than its subtitle window" if secs > end - start + 0.3 else ""
    print(f"{i:02d}.wav  {secs:4.1f}s (window {end - start:.1f}s)  {text}{flag}")
