// Renders index.html frame-by-frame with headless Chromium and pipes PNGs to ffmpeg.
//   node render.mjs                     -> frames.mp4 (silent, 1920x1080 @ 30fps)
//   node render.mjs --subs              -> frames-subs.mp4 (voiceover subtitles burned in)
//   node render.mjs --stills 2,7,15     -> still-2.png, still-7.png, ... for review
// Needs: playwright (npm), an ffmpeg binary (FFMPEG env var or on PATH), and the repo served over HTTP
// (the page loads ../../assets). Default URL assumes `python3 -m http.server 8123` from the repo root.
import { createRequire } from "module";
import { spawn } from "child_process";
import { writeFileSync } from "fs";
const require = createRequire(import.meta.url);
let playwright;
try { playwright = require("playwright"); } catch { playwright = require("/opt/node22/lib/node_modules/playwright"); }

const SUBS = process.argv.includes("--subs");
const OUT = process.env.OUT || (SUBS ? "frames-subs.mp4" : "frames.mp4");
const URL_ = process.env.URL || `http://127.0.0.1:8123/video/franchise-growth/index.html#capture${SUBS ? "-subs" : ""}`;
const FPS = 30;
const args = process.argv.slice(2);
const si = args.indexOf("--stills"), stills = si >= 0 ? args[si + 1].split(",").map(Number) : null;

const browser = await playwright.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await page.goto(URL_);
await page.evaluate(() => window.ready);
const DUR = await page.evaluate(() => window.DUR);
const grab = async t => {
  const b64 = await page.evaluate(t => { window.render(t); return document.getElementById("c").toDataURL("image/png").split(",")[1]; }, t);
  return Buffer.from(b64, "base64");
};

if (stills) {
  for (const t of stills) writeFileSync(`still-${t}.png`, await grab(t));
} else {
  const ff = spawn(process.env.FFMPEG || "ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(FPS), "-i", "-",
    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], { stdio: ["pipe", "inherit", "inherit"] });
  const total = Math.round(FPS * DUR);
  for (let f = 0; f < total; f++) {
    const buf = await grab(f / FPS);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    if (f % 150 === 0) console.log(`frame ${f}/${total}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
}
await browser.close();
