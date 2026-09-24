# Voiceover with Google AI

There are three ways to make the voiceover. Pick one. Whichever you use, send the audio back and it gets mixed into the video on the subtitle timings.

## Option A: Google AI Studio in the browser (easiest, free, no code)

1. Go to <https://aistudio.google.com> and sign in with your Google account.
2. In the left menu, open **Generate media**, then choose **Generate speech** (Gemini text-to-speech).
3. Choose **Single-speaker audio**.
4. Open `ai-studio-script.txt`:
   - Paste the **style instructions** into the "Style instructions" box.
   - Paste the **text** into the main box.
5. Model and voice:
   - Model: *Gemini 2.5 Pro TTS* (best quality). *Flash TTS* is faster.
   - Voice: start with **Charon** (calm and informative), **Orus** (firm) or **Kore** (firm, female). Click the play icon to preview each one.
6. Click **Run**. Listen, change the voice or style if you want, then **download** the audio. It comes out as a WAV file.
7. Send the WAV back. It gets cut into lines and each line placed on its subtitle.

Tip: if one line sounds wrong, generate only that line again and send it as its own file.

## Option B: Gemini API script (one file per line, free AI Studio key)

This option saves a separate file for each line, which is easier to line up with the subtitles.

1. Get a free API key at <https://aistudio.google.com/apikey>.
2. Install Python 3 if you don't have it (it comes with macOS/Linux; on Windows get it from python.org).
3. Open a terminal in this folder and run:
   ```
   GEMINI_API_KEY=your-key python3 gemini_tts.py Charon
   ```
   On Windows PowerShell, run this instead:
   ```
   $env:GEMINI_API_KEY="your-key"; python gemini_tts.py Charon
   ```
4. This creates `clips/01.wav` to `clips/20.wav`, one file for each subtitle line. The script also warns you about any line that runs longer than its time on screen.
5. Send back the `clips` folder.

## Option C: Google Cloud Text-to-Speech (classic Cloud service)

This needs a Google Cloud account with billing turned on. The free monthly allowance is large enough for this video, so it should cost $0.

1. Go to <https://console.cloud.google.com>, create a project and turn on billing.
2. Search for **Cloud Text-to-Speech API** and click **Enable**.
3. Go to **APIs & Services → Credentials → Create credentials → API key**. Then restrict the key to the Cloud Text-to-Speech API.
4. Run:
   ```
   GCLOUD_TTS_KEY=your-key python3 gcloud_tts.py en-US-Chirp3-HD-Charon
   ```
   - To change the speed, add `RATE=0.9` in front of the command (1.0 is normal speed).
   - For other voices, see the [voice list](https://cloud.google.com/text-to-speech/docs/list-voices-and-types). The *Chirp3-HD* voices sound the most natural.
5. Send back the `clips` folder.

## Notes

- **Commercial use:** Google's terms let you use the generated audio in your own marketing. On the AI Studio free tier, Google may use what you send to improve its products. The script is public marketing copy, so that's fine here.
- **Wording:** the text comes from `../timeline.js`. If the wording changes there, run the script again so the audio matches the subtitles.
- **Pronunciation:** the scripts say "myalkimia.com" as "my alkimia dot com". If "Alkimia" still sounds wrong, spell it the way it should sound, for example "Al-KEE-mee-ah".
