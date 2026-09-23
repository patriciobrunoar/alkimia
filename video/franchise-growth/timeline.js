// Single source of truth for scene timing and voiceover subtitles.
// Used by index.html (animation + burned-in subtitles), audio.py (sound design) and make-srt.mjs (voiceover.srt).
// Keep the object below strict JSON so Python and Node can parse it.
// scenes: [start, end, speed] in seconds — speed < 1 plays that scene's animation slower.
// cues:   [start, end, "text"] in seconds — edit the voiceover here, then re-render.
window.TIMELINE = {
  "duration": 66.5,
  "scenes": [
    [0, 7.5, 0.8],
    [7.5, 14, 1],
    [14, 24, 0.9],
    [24, 34.5, 1],
    [34.5, 45, 1],
    [45, 54.5, 1],
    [54.5, 60.5, 1],
    [60.5, 66.5, 1]
  ],
  "cues": [
    [0.4, 3.4, "Scaling a franchise isn't just about adding locations."],
    [3.4, 5.4, "It's building a scalable model that drives growth,"],
    [5.4, 7.3, "brand consistency and team efficiency."],
    [7.9, 10.6, "As networks expand, real friction appears"],
    [10.6, 13.6, "between corporate vision and local execution."],
    [14.3, 16.6, "Alkimia builds the bridge:"],
    [16.6, 19.6, "a framework that turns high-level strategy and marketing"],
    [19.6, 22.6, "into repeatable local performance."],
    [24.4, 27.2, "We start with an end-to-end Assessment,"],
    [27.2, 30.4, "auditing your GTM, processes, tools and franchisee support,"],
    [30.4, 33.9, "to uncover blind spots and map your strategic roadmap."],
    [34.9, 37.4, "Then, we activate that roadmap:"],
    [37.4, 40.6, "turnkey grand openings, plug-and-play marketing playbooks,"],
    [40.6, 44.3, "always-on media and continuous franchisee enablement."],
    [45.4, 48.6, "We work alongside your leadership, agencies and franchisees"],
    [48.6, 52.2, "to execute accurately, without disrupting your operations."],
    [54.8, 56.6, "One unified marketing ecosystem."],
    [56.6, 58.3, "Built for consistency."],
    [58.3, 60.3, "Engineered for enterprise and local growth."],
    [61.0, 65.0, "Start with your Growth Assessment at myalkimia.com."]
  ]
};
