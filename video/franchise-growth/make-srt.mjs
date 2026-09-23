// Writes voiceover.srt and voiceover-script.md from timeline.js.  Usage: node make-srt.mjs
import { readFileSync, writeFileSync } from "fs";
const src = readFileSync(new URL("./timeline.js", import.meta.url), "utf8");
const T = JSON.parse(src.slice(src.indexOf("window.TIMELINE =") + 17).trim().replace(/;$/, ""));
const ts = s => { const ms = Math.round(s * 1000), h = Math.floor(ms / 3600000), m = Math.floor(ms / 60000) % 60, sec = Math.floor(ms / 1000) % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")},${String(ms % 1000).padStart(3, "0")}`; };
writeFileSync(new URL("./voiceover.srt", import.meta.url), T.cues.map(([a, b, s], i) => `${i + 1}\n${ts(a)} --> ${ts(b)}\n${s}\n`).join("\n"));
const mmss = s => `${Math.floor(s / 60)}:${(s % 60).toFixed(1).padStart(4, "0")}`;
const names = ["Scale your framework", "Corporate vision ≠ local reality", "Alkimia builds the bridge", "01. The Initial Assessment",
  "02. The Enablement", "Aligned execution", "Assess. Enable. Scale.", "End card"];
let md = `# Voiceover script: Alkimia Franchise Growth Systems\n\nTotal runtime ${mmss(T.duration)}. Read each line inside its window; the subtitles in the review video show exactly when.\n`;
T.scenes.forEach(([a, b], i) => {
  const cues = T.cues.filter(([s]) => s >= a && s < b), words = cues.reduce((n, c) => n + c[2].split(/\s+/).length, 0);
  md += `\n## ${i + 1}. ${names[i]} (${mmss(a)} to ${mmss(b)})\n\n` + cues.map(([s, e, x]) => `- \`${mmss(s)}–${mmss(e)}\` ${x}`).join("\n") + `\n\n_${words} words_\n`;
});
writeFileSync(new URL("./voiceover-script.md", import.meta.url), md);
console.log("wrote voiceover.srt and voiceover-script.md,", T.cues.length, "cues");
