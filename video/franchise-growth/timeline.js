// Single source of truth for scene timing and voiceover subtitles.
// Used by index.html (animation + burned-in subtitles), audio.py (sound design) and make-srt.mjs (voiceover.srt).
// Keep the object below strict JSON so Python and Node can parse it.
// scenes: [start, end, speed] in seconds — speed < 1 plays that scene's animation slower.
// cues:   [start, end, "text"] in seconds — edit the voiceover here, then re-render.
window.TIMELINE = {
  "duration": 69.54,
  "scenes": [
    [0.0, 9.84, 0.61],
    [9.84, 16.23, 1.017],
    [16.23, 24.35, 1.108],
    [24.35, 36.03, 0.899],
    [36.03, 46.7, 0.984],
    [46.7, 55.4, 1.092],
    [55.4, 63.48, 0.743],
    [63.48, 69.54, 0.99]
  ],
  "cues": [
    [0.28, 3.7, "Scaling a franchise isn't just about adding locations."],
    [3.7, 6.81, "It's building a scalable model that drives growth,"],
    [6.81, 9.54, "brand consistency and team efficiency."],
    [10.07, 12.78, "As networks expand, real friction appears"],
    [12.78, 15.88, "between corporate vision and local execution."],
    [16.46, 18.48, "Alkimia builds the bridge:"],
    [18.48, 21.65, "a framework that turns high-level strategy and marketing"],
    [21.65, 24.0, "into repeatable local performance."],
    [24.58, 27.0, "We start with an end-to-end Assessment,"],
    [27.0, 31.8, "auditing your GTM, processes, tools and franchisee support,"],
    [31.8, 35.68, "to uncover blind spots and map your strategic roadmap."],
    [36.26, 38.51, "Then, we activate that roadmap:"],
    [38.51, 42.33, "turnkey grand openings, plug-and-play marketing playbooks,"],
    [42.33, 46.35, "always-on media and continuous franchisee enablement."],
    [46.93, 50.96, "We work alongside your leadership, agencies and franchisees"],
    [50.96, 55.05, "to execute accurately, without disrupting your operations."],
    [55.63, 58.38, "One unified marketing ecosystem."],
    [58.38, 60.0, "Built for consistency."],
    [60.0, 63.13, "Engineered for enterprise and local growth."],
    [63.71, 67.79, "Start with your Growth Assessment at myalkimia.com."]
  ]
};
