const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const path = require("path");
const SKILL = "/root/.claude/skills/synced/afe6026f-afaf-4062-bcc0-ac09e63b0e5d_fb953aa4-26a2-4657-96d9-139179910856/pptx";
const { applyTheme } = require(SKILL + "/scripts/apply_theme.js");

const THEME = {
  name: "BDRR Ranch",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "2B1A10", lt1: "FFFFFF", dk2: "5A2E14", lt2: "F4EBE0",
    accent1: "B5651D", accent2: "3E7C59", accent3: "2F5D8A",
    accent4: "7B4B94", accent5: "8A6D3B", accent6: "6B6B6B",
    hlink: "2F5D8A", folHlink: "7B4B94",
  },
};
// hex copies for icons / hex-only options
const HEX = { brown: "5A2E14", amber: "B5651D", green: "3E7C59", blue: "2F5D8A", purple: "7B4B94", tint: "F4EBE0", ink: "2B1A10", grey: "6B6B6B", white: "FFFFFF" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.title = "Big Dog Ranch Rescue – Media & Keyword Strategy";
pres.author = "Alkimia";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const LOGO = path.join(__dirname, "bdrr-logo.png");

pres.defineSlideMaster({
  title: "TITLE", background: { color: HEX.brown },
  objects: [
    { image: { path: LOGO, x: 8.3, y: 1.55, w: 4.4, h: 2.28, objectName: "BDRR logo" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.7, w: 7.1, h: 1.7, fontSize: 40, bold: true, color: C.background1, align: "left", valign: "bottom", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.6, w: 7.1, h: 1.4, fontSize: 20, color: C.background2, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "SECTION", background: { color: HEX.brown },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.5, w: 9, h: 1.3, fontSize: 44, bold: true, color: C.background1, align: "left", valign: "bottom", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.95, w: 8.2, h: 1.4, fontSize: 20, color: C.background2, align: "left", valign: "top", margin: 0 }, text: "" } },
    { image: { path: LOGO, x: 11.2, y: 6.45, w: 1.5, h: 0.78, objectName: "BDRR logo" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT", background: { color: HEX.white },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.7, w: 12.1, h: 0.85, fontSize: 32, bold: true, color: C.text2, align: "left", valign: "middle", margin: 0 }, text: "" } },
    { image: { path: LOGO, x: 11.4, y: 6.58, w: 1.3, h: 0.67, objectName: "BDRR logo" } },
    { text: { text: "Big Dog Ranch Rescue  |  bdrr.org  |  Media & Keyword Strategy", options: { x: 0.6, y: 6.9, w: 8, h: 0.3, fontSize: 10, color: C.text2, margin: 0, isTextBox: true, objectName: "Footer" } } },
  ],
  slideNumber: { x: 10.6, y: 6.9, w: 0.6, h: 0.3, fontSize: 10, color: HEX.grey, align: "right" },
});

async function icon(Comp, color = "#FFFFFF") {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color, size: 256 }));
  const buf = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

const SEC = {
  paid: { name: "Google Search Ads", color: C.accent1, hex: HEX.amber },
  seo: { name: "SEO", color: C.accent3, hex: HEX.blue },
  geo: { name: "GEO", color: C.accent2, hex: HEX.green },
  aeo: { name: "AEO", color: C.accent4, hex: HEX.purple },
};

function kicker(slide, text, sec) {
  slide.addText(text.toUpperCase(), { x: 0.6, y: 0.4, w: 9, h: 0.3, fontSize: 12, bold: true, charSpacing: 2, color: sec.color, margin: 0, isTextBox: true, objectName: "Kicker" });
}
function newContent(section, secKey, kick, title) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  kicker(s, kick, SEC[secKey]);
  s.addText(title, { placeholder: "title" });
  return s;
}
function sectionSlide(section, title, sub) {
  const s = pres.addSlide({ masterName: "SECTION", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  s.addText(sub, { placeholder: "body" });
  return s;
}

// Keyword group slide: two-column keyword list + side card
function keywordSlide(secKey, section, kick, title, kws, meta) {
  const s = newContent(section, secKey, kick, title);
  const sec = SEC[secKey];
  s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 1.8, w: 8.0, h: 4.6, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: "none" }, objectName: "Keyword card" });
  const half = Math.ceil(kws.length / 2);
  [kws.slice(0, half), kws.slice(half)].forEach((col, i) => {
    s.addText(col.map((k, j) => ({ text: k, options: { bullet: true, breakLine: j < col.length - 1 } })), {
      x: 0.85 + i * 3.9, y: 2.0, w: 3.7, h: 4.2, fontSize: 16, color: C.text1, valign: "top", paraSpaceAfter: 6, margin: 0, isTextBox: true, objectName: "Keywords " + (i + 1),
    });
  });
  s.addShape(pres.ShapeType.roundRect, { x: 8.95, y: 1.8, w: 3.78, h: 4.6, rectRadius: 0.12, fill: { color: sec.color }, line: { type: "none" }, objectName: "Intent card" });
  const runs = [];
  meta.forEach(([label, val], i) => {
    runs.push({ text: label.toUpperCase(), options: { fontSize: 12, bold: true, color: C.background2, breakLine: true, charSpacing: 1 } });
    runs.push({ text: val, options: { fontSize: 15, color: C.background1, breakLine: i < meta.length - 1, paraSpaceAfter: 12 } });
  });
  s.addText(runs, { x: 9.2, y: 2.0, w: 3.3, h: 4.2, valign: "top", margin: 0, isTextBox: true, objectName: "Intent details" });
  return s;
}

// Simple card grid (n columns)
function cards(s, items, { x = 0.6, y = 1.8, w = 12.13, h = 4.5, cols = 2, gap = 0.3, secKey, headSize = 18, bodySize = 14 }) {
  const rows = Math.ceil(items.length / cols);
  const cw = (w - gap * (cols - 1)) / cols, ch = (h - gap * (rows - 1)) / rows;
  items.forEach((it, i) => {
    const cx = x + (i % cols) * (cw + gap), cy = y + Math.floor(i / cols) * (ch + gap);
    s.addShape(pres.ShapeType.roundRect, { x: cx, y: cy, w: cw, h: ch, rectRadius: 0.1, fill: { color: C.background2 }, line: { type: "none" }, objectName: "Card " + (i + 1) });
    s.addShape(pres.ShapeType.ellipse, { x: cx + 0.25, y: cy + 0.25, w: 0.5, h: 0.5, fill: { color: SEC[secKey].color }, line: { type: "none" }, objectName: "Badge " + (i + 1) });
    s.addText(String(i + 1), { x: cx + 0.25, y: cy + 0.25, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(it[0], { x: cx + 0.95, y: cy + 0.2, w: cw - 1.15, h: 0.6, fontSize: headSize, bold: true, color: C.text2, valign: "middle", margin: 0, isTextBox: true, objectName: "Card title " + (i + 1) });
    s.addText(it[1], { x: cx + 0.25, y: cy + 0.9, w: cw - 0.5, h: ch - 1.05, fontSize: bodySize, color: C.text1, valign: "top", margin: 0, isTextBox: true, objectName: "Card body " + (i + 1) });
  });
}

function table(s, head, rows, colW, secKey, y = 1.8, rowH = 0.7) {
  const hdr = head.map((t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: SEC[secKey].color }, fontSize: 14, valign: "middle" } }));
  const body = rows.map((r, ri) => r.map((t, ci) => ({ text: t, options: { fontSize: 14, color: C.text1, bold: ci === 0, fill: { color: ri % 2 ? C.background1 : C.background2 }, valign: "middle" } })));
  s.addTable([hdr, ...body], { x: 0.6, y, w: 12.13, colW, rowH: [0.45, ...rows.map(() => rowH)], border: { type: "solid", pt: 0.5, color: "E2D5C5" }, margin: [0.05, 0.12, 0.05, 0.12], fontFace: "Calibri", objectName: "Table" });
}

(async () => {
  const iSearch = await icon(fa.FaSearch), iGoogle = await icon(fa.FaGoogle), iRobot = await icon(fa.FaRobot), iQ = await icon(fa.FaQuestionCircle), iPin = await icon(fa.FaMapMarkerAlt);

  ["Intro","Google Search Ads","SEO","GEO","AEO","Wrap-up"].forEach((t) => pres.addSection({ title: t }));
  // 1. Title
  let s = pres.addSlide({ masterName: "TITLE", sectionTitle: "Intro" });
  s.addText("BIG DOG RANCH RESCUE", { placeholder: "title" });
  s.addText([
    { text: "Media & Keyword Strategy", options: { breakLine: true, bold: true } },
    { text: "Google Search Ads  |  SEO  |  GEO  |  AEO", options: { breakLine: true } },
    { text: "bdrr.org", options: {} },
  ], { placeholder: "body" });

  // 2. Overview
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Intro" });
  s.addText("bdrr.org: one site, four search jobs", { placeholder: "title" });
  s.addText("Big Dog Ranch Rescue (Loxahatchee, Palm Beach County, FL) is a large cage-free, no-kill dog rescue. People come to bdrr.org to adopt, foster, volunteer, donate and visit.", { x: 0.6, y: 1.65, w: 12.1, h: 0.8, fontSize: 18, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  const jobs = [
    [iGoogle, "Google Search Ads", "Capture people actively searching to adopt, foster, volunteer or give. Fast, measurable, budget-controlled.", C.accent1],
    [iSearch, "SEO", "Build owned, compounding visibility for the same intents across the site and Google Maps.", C.accent3],
    [iRobot, "GEO", "Get Big Dog Ranch Rescue named and cited when ChatGPT, Gemini, Perplexity and AI Overviews recommend rescues.", C.accent2],
    [iQ, "AEO", "Give search engines and assistants short, structured answers to the questions adopters and donors ask.", C.accent4],
  ];
  jobs.forEach((j, i) => {
    const cx = 0.6 + i * 3.08;
    s.addShape(pres.ShapeType.roundRect, { x: cx, y: 2.7, w: 2.89, h: 3.7, rectRadius: 0.1, fill: { color: C.background2 }, line: { type: "none" }, objectName: "Channel card " + (i + 1) });
    s.addShape(pres.ShapeType.ellipse, { x: cx + 0.25, y: 2.95, w: 0.7, h: 0.7, fill: { color: j[3] }, line: { type: "none" }, objectName: "Icon circle " + (i + 1) });
    s.addImage({ data: j[0], x: cx + 0.42, y: 3.12, w: 0.36, h: 0.36, altText: j[1] + " icon" });
    s.addText(j[1], { x: cx + 0.25, y: 3.85, w: 2.4, h: 0.45, fontSize: 20, bold: true, color: C.text2, margin: 0, isTextBox: true });
    s.addText(j[2], { x: cx + 0.25, y: 4.4, w: 2.4, h: 1.9, fontSize: 14, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  });

  // 3. How the pieces work together
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Intro" });
  s.addText("Full-funnel search plan", { placeholder: "title" });
  const steps = [
    ["Be found", "SEO + GEO + AEO make bdrr.org the answer people and AI assistants cite.", C.accent3],
    ["Capture intent", "Google Search Ads show up at the moment of a high-intent search.", C.accent1],
    ["Convert", "Dedicated landing pages: Adopt, Foster, Volunteer, Donate.", C.accent2],
    ["Learn and expand", "Search terms, conversions and AI mentions feed the next quarter.", C.accent4],
  ];
  steps.forEach((st, i) => {
    const cx = 0.6 + i * 3.08;
    s.addShape(pres.ShapeType.roundRect, { x: cx, y: 2.0, w: 2.89, h: 3.3, rectRadius: 0.1, fill: { color: st[2] }, line: { type: "none" }, objectName: "Step " + (i + 1) });
    s.addText(String(i + 1), { x: cx + 0.25, y: 2.15, w: 1, h: 0.9, fontSize: 48, bold: true, color: C.background1, margin: 0, isTextBox: true });
    s.addText(st[0], { x: cx + 0.25, y: 3.1, w: 2.4, h: 0.5, fontSize: 20, bold: true, color: C.background1, margin: 0, isTextBox: true });
    s.addText(st[1], { x: cx + 0.25, y: 3.65, w: 2.4, h: 1.5, fontSize: 14, color: C.background1, margin: 0, valign: "top", isTextBox: true });
  });
  s.addText("Note: keyword sets are intent-based recommendations. Search volumes and CPCs must be validated in Google Keyword Planner or Semrush before launch; no volume data is included here.", { x: 0.6, y: 5.6, w: 10.5, h: 0.7, fontSize: 14, italic: true, color: C.text1, margin: 0, valign: "top", isTextBox: true });

  // ---------- SECTION A: GOOGLE SEARCH ----------
  const A = "Google Search Ads";
  sectionSlide(A, "Google Search: paid keywords", "Keyword groups for adoption, foster, volunteer, donate and visit intent");

  s = newContent(A, "paid", "Google Search Ads", "Campaign structure");
  table(s, ["Campaign", "Goal", "Landing page", "Ad groups"], [
    ["Brand", "Protect brand terms", "Home / About", "Brand, Brand + location"],
    ["Adopt", "Adoption applications", "Adopt a dog", "Adopt, Puppies and breeds, Local"],
    ["Foster", "Foster sign-ups", "Foster", "Foster, Foster-to-adopt"],
    ["Volunteer", "Volunteer applications", "Volunteer", "Volunteer, Groups and students"],
    ["Donate", "Online gifts", "Donate", "Donate, Sponsor, In-kind"],
    ["Programs and visits", "Awareness, events", "Programs / Events", "Veterans, Seniors, Beagles, Visit"],
  ], [2.4, 3.0, 2.6, 4.13], "paid", 1.8, 0.62);

  s = newContent(A, "paid", "Google Search Ads", "Match types, bidding and Ad Grants");
  cards(s, [
    ["Match types", "Start with phrase and exact for the core terms. Use broad match only with smart bidding, once conversion data exists and negatives are in place."],
    ["Bidding", "Begin with Maximize Clicks to learn, then move to Maximize Conversions or target CPA per campaign (adoption app, foster form, donation)."],
    ["Google Ad Grants", "If BDRR is enrolled: up to $10K/month of Search ads. Policy needs at least 5% CTR and no single-word keywords except brand. Verify current rules."],
    ["Targeting", "Palm Beach County first, then Broward, Martin, St. Lucie and Miami-Dade. Schedule heavier weight for adoption events and giving moments."],
  ], { secKey: "paid", cols: 2 });

  const paid = [
    ["Brand", "Brand terms", ["big dog ranch rescue", "big dog ranch rescue loxahatchee", "big dog ranch rescue adoption", "big dog ranch rescue palm beach", "big dog and small ranch rescue", "bdrr", "bdrr.org", "bdrr dog adoption", "big dog ranch rescue donate", "big dog ranch rescue volunteer", "big dog ranch rescue foster", "big dog ranch rescue reviews", "big dog ranch rescue events", "big dog ranch rescue visit"], [["Intent", "Navigational. People who already know us."], ["Landing page", "Home, or the matching section page"], ["Match type", "Exact and phrase"], ["Why", "Defend brand terms against other advertisers."]]],
    ["1", "Adopt a Dog", ["adopt a dog", "dog adoption", "adopt a dog near me", "dog adoption near me", "dogs for adoption near me", "rescue dogs for adoption", "adopt a rescue dog", "no kill dog rescue near me", "dog adoption florida", "dog adoption palm beach county", "dog adoption west palm beach", "how to adopt a dog", "dog rescue near me", "dog adoption application"], [["Intent", "High. Ready to adopt."], ["Landing page", "Adopt a dog / available dogs"], ["Match type", "Phrase and exact"], ["Why", "Core conversion: adoption applications."]]],
    ["2", "Puppies, Seniors and Breeds", ["puppies for adoption", "puppies for adoption near me", "adopt a puppy", "rescue puppies near me", "puppy adoption florida", "senior dog adoption", "adopt a senior dog", "small dogs for adoption", "large dog rescue", "labrador rescue florida", "german shepherd rescue florida", "pit bull rescue florida", "golden retriever rescue florida", "husky rescue florida"], [["Intent", "High. Specific preference."], ["Landing page", "Adopt, filtered by age or size"], ["Match type", "Phrase and exact"], ["Why", "Long-tail terms usually cost less per click."]]],
    ["4", "Foster", ["foster a dog", "dog foster near me", "become a dog foster", "foster dog florida", "dog fostering palm beach county", "foster to adopt dog", "how to foster a dog", "dog rescue foster program", "foster a puppy", "foster dogs near me", "temporary dog foster", "foster a dog for a rescue"], [["Intent", "Medium to high. Ready to help."], ["Landing page", "Foster a dog"], ["Match type", "Phrase and exact"], ["Why", "Fosters free kennel space for more rescues."]]],
    ["5", "Volunteer", ["dog rescue volunteer near me", "volunteer with dogs", "volunteer at animal shelter", "animal shelter volunteer palm beach county", "dog walking volunteer", "animal rescue volunteer opportunities", "volunteer dog rescue florida", "community service hours animal shelter", "student volunteer animal shelter", "corporate volunteering animal shelter"], [["Intent", "Medium. Exploring ways to help."], ["Landing page", "Volunteer"], ["Match type", "Phrase"], ["Why", "Builds volunteers, groups and future donors."]]],
    ["6", "Donate and Sponsor", ["donate to dog rescue", "donate to animal rescue florida", "best dog rescue to donate to", "animal charity donations", "sponsor a dog", "dog rescue donations", "donate dog food to shelter", "in kind donations animal shelter", "donate to no kill shelter", "monthly giving animal rescue", "donate in memory of pet", "charity for dogs near me"], [["Intent", "Medium to high. Giving intent."], ["Landing page", "Donate / Ways to give"], ["Match type", "Phrase and exact"], ["Why", "Direct revenue. Test year-end and giving days."]]],
    ["7", "Visit, Events and Camps", ["dog rescue ranch visit", "animal shelter tours", "things to do in loxahatchee", "dog events palm beach county", "adoption events near me", "dog friendly events west palm beach", "kids animal camp palm beach county", "animal rescue field trip", "pet adoption event west palm beach", "visit animal sanctuary florida"], [["Intent", "Low to medium. Discovery."], ["Landing page", "Visit / Events"], ["Match type", "Phrase"], ["Why", "Confirm which visits and events are currently offered."]]],
    ["8", "Programs and Special Rescues", ["service dogs for veterans", "veteran service dog program florida", "companion dog for seniors", "senior companion dog adoption", "adopt a beagle", "rescued beagles adoption", "beagle rescue florida", "hurricane rescue dogs", "youth animal program palm beach county", "dogs for veterans near me"], [["Intent", "Mixed. Mission and campaign driven."], ["Landing page", "Program or campaign page"], ["Match type", "Phrase"], ["Why", "Tie to news moments such as beagle arrivals."]]],
  ];
  const localSlide = () => {
  // Local keyword slide
  let s = newContent(A, "paid", "Google Search Ads  |  Group 3", "Local and city modifiers");
  const cities = ["Loxahatchee", "Wellington", "West Palm Beach", "Royal Palm Beach", "Palm Beach Gardens", "Jupiter", "Boynton Beach", "Delray Beach", "Boca Raton", "Fort Lauderdale", "Port St. Lucie", "Miami"];
  s.addText("Build each pattern for every city:", { x: 0.6, y: 1.7, w: 8, h: 0.4, fontSize: 16, bold: true, color: C.text2, margin: 0, isTextBox: true });
  const pats = ["dog adoption [city]", "adopt a dog [city]", "dog rescue [city]", "foster a dog [city]", "volunteer with dogs [city]", "animal shelter [city]"];
  pats.forEach((p, i) => {
    const px = 0.6 + (i % 2) * 2.6, py = 2.2 + Math.floor(i / 2) * 0.62;
    s.addShape(pres.ShapeType.roundRect, { x: px, y: py, w: 2.45, h: 0.5, rectRadius: 0.25, fill: { color: C.accent1 }, line: { type: "none" }, objectName: "Pattern " + (i + 1) });
    s.addText(p, { x: px, y: py, w: 2.45, h: 0.5, fontSize: 14, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
  });
  s.addText("Phrase and exact match. Scale to additional Florida counties once the first set performs.", { x: 0.6, y: 4.2, w: 5.2, h: 1.0, fontSize: 14, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  s.addShape(pres.ShapeType.roundRect, { x: 6.2, y: 1.8, w: 6.53, h: 4.6, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: "none" }, objectName: "Cities card" });
  s.addText("Priority cities", { x: 6.5, y: 2.0, w: 5.9, h: 0.4, fontSize: 18, bold: true, color: C.text2, margin: 0, isTextBox: true });
  [cities.slice(0, 6), cities.slice(6)].forEach((col, i) => {
    s.addText(col.map((k, j) => ({ text: k, options: { bullet: true, breakLine: j < col.length - 1 } })), { x: 6.5 + i * 3.0, y: 2.55, w: 2.8, h: 3.6, fontSize: 16, color: C.text1, valign: "top", paraSpaceAfter: 8, margin: 0, isTextBox: true });
  });

  };
  paid.forEach((g) => {
    const label = g[0] === "Brand" ? "Brand" : "Group " + g[0];
    keywordSlide("paid", A, "Google Search Ads  |  " + label, g[1], g[2], g[3]);
    if (g[0] === "2") localSlide();
  });

  // Negatives
  keywordSlide("paid", A, "Google Search Ads  |  Negative keywords", "Negative keywords", ["free dog", "cheap puppies", "puppies for sale", "dogs for sale", "buy a dog", "breeder", "puppy mill", "pet store", "craigslist", "lost dog", "found dog", "stray dog", "jobs / careers", "dog training classes", "vet near me", "dog food coupons"], [["Purpose", "Block shoppers, breeders and unrelated pet services."], ["Apply at", "Account level, then refine per campaign."], ["Review", "Weekly search terms report in month one, then monthly."], ["Watch", "Do not block 'free' for donation or service-dog programs without checking."]]);

  // ---------- SECTION B: SEO ----------
  const B = "SEO";
  sectionSlide(B, "SEO: owned search visibility", "Pillar pages, local search and content that earn traffic without paying per click");

  s = newContent(B, "seo", "SEO", "Pillar pages and target keywords");
  table(s, ["Pillar page", "Primary keywords", "Supporting content"], [
    ["Adopt a dog", "dog adoption palm beach county, adopt a dog near me", "Adoption process, fees, FAQs, adoptable dog profiles"],
    ["Foster a dog", "foster a dog palm beach county, dog foster near me", "How fostering works, supplies list, foster stories"],
    ["Volunteer", "dog rescue volunteer near me, volunteer with dogs", "Roles, age rules, group and student volunteering"],
    ["Donate / Give", "donate to dog rescue florida, sponsor a dog", "Impact page, wish list, giving days, memorial gifts"],
    ["Programs", "service dogs for veterans, companion dogs for seniors", "One page per program, with outcomes and stories"],
    ["Visit and events", "things to do in loxahatchee, dog adoption events", "Event calendar with Event schema, visitor guide"],
  ], [2.3, 4.9, 4.93], "seo", 1.8, 0.66);

  s = newContent(B, "seo", "SEO", "Priority fixes and builds");
  cards(s, [
    ["Make dog profiles indexable", "Each adoptable dog gets a crawlable URL with unique text, photos with alt text and a clear Apply button. Redirect or noindex adopted dogs."],
    ["Structured data", "Organization / NonProfit, LocalBusiness, Event, FAQPage and DonateAction schema. Validate in Rich Results Test."],
    ["Local SEO", "Complete the Google Business Profile, keep name, address and phone identical on Petfinder, Adopt-a-Pet, GuideStar and local directories."],
    ["Authority links", "Earn links from local news, Palm Beach County agencies, schools, corporate partners and veterinary partners."],
    ["Speed and mobile", "Compress heavy photography, fix Core Web Vitals and test the adoption form on mobile."],
    ["Internal linking", "Link every blog post and dog profile back to Adopt, Foster, Volunteer and Donate pages."],
  ], { secKey: "seo", cols: 3, headSize: 16, bodySize: 14, h: 4.6 });

  s = newContent(B, "seo", "SEO", "Content calendar starters");
  [
    ["Adopting a dog in Palm Beach County: step by step", "adoption process"],
    ["First 30 days with a rescue dog", "new adopter guide"],
    ["Foster vs adopt: which is right for you?", "foster funnel"],
    ["What does cage-free, no-kill rescue mean?", "brand explainer"],
    ["Best dog breeds for Florida heat", "breed intent"],
    ["How to volunteer with dogs in South Florida", "volunteer funnel"],
    ["Where your donation goes", "trust and giving"],
    ["Meet the beagles: how rescued lab dogs adjust", "news and story hook"],
  ].forEach((it, i) => {
    const col = i % 2, row = Math.floor(i / 2), cx = 0.6 + col * 6.17, cy = 1.8 + row * 1.15;
    s.addShape(pres.ShapeType.roundRect, { x: cx, y: cy, w: 5.96, h: 0.98, rectRadius: 0.1, fill: { color: C.background2 }, line: { type: "none" }, objectName: "Topic " + (i + 1) });
    s.addText(String(i + 1), { x: cx + 0.2, y: cy + 0.2, w: 0.55, h: 0.55, fontSize: 16, bold: true, color: C.background1, align: "center", valign: "middle", fill: { color: HEX.blue }, shape: pres.ShapeType.ellipse, margin: 0, isTextBox: true });
    s.addText([{ text: it[0], options: { bold: true, fontSize: 16, color: C.text1, breakLine: true } }, { text: it[1], options: { fontSize: 14, color: C.accent6 } }], { x: cx + 0.95, y: cy + 0.08, w: 4.85, h: 0.82, valign: "middle", margin: 0, isTextBox: true });
  });

  // ---------- SECTION C: GEO ----------
  const G = "GEO";
  sectionSlide(G, "GEO: Generative Engine Optimization", "Being named and cited in ChatGPT, Gemini, Perplexity, Copilot and Google AI Overviews");

  s = newContent(G, "geo", "GEO", "Prompts we want Big Dog Ranch Rescue to win");
  const prompts = [
    ["Discovery", ["best dog rescues in Palm Beach County", "where can I adopt a dog in South Florida", "best no-kill dog shelters in Florida", "largest cage-free dog rescue in the US"]],
    ["Action", ["how do I foster a dog in Palm Beach County", "dog rescues near Wellington that need volunteers", "where to donate to help rescue dogs in Florida", "how do I adopt a beagle in Florida"]],
    ["Trust", ["is Big Dog Ranch Rescue legit", "Big Dog Ranch Rescue reviews and rating", "how does Big Dog Ranch Rescue use donations", "what programs does Big Dog Ranch Rescue run"]],
  ];
  prompts.forEach((g, i) => {
    const cx = 0.6 + i * 4.1;
    s.addShape(pres.ShapeType.roundRect, { x: cx, y: 1.8, w: 3.93, h: 4.6, rectRadius: 0.1, fill: { color: C.background2 }, line: { type: "none" }, objectName: "Prompt card " + (i + 1) });
    s.addText(g[0], { x: cx + 0.25, y: 1.95, w: 3.4, h: 0.5, fontSize: 18, bold: true, color: C.accent2, margin: 0, isTextBox: true });
    s.addText(g[1].map((k, j) => ({ text: k, options: { bullet: true, breakLine: j < g[1].length - 1 } })), { x: cx + 0.25, y: 2.55, w: 3.45, h: 3.7, fontSize: 16, color: C.text1, valign: "top", paraSpaceAfter: 10, margin: 0, isTextBox: true });
  });

  s = newContent(G, "geo", "GEO", "How we earn AI citations");
  cards(s, [
    ["Consistent entity", "One clear description of BDRR everywhere: site, Google Business Profile, Wikipedia or Wikidata where eligible, GuideStar, Charity Navigator."],
    ["Citable facts", "Dated, sourced impact numbers, programs and policies on crawlable pages. AI tools quote specific facts, not slogans."],
    ["Third-party mentions", "Local news, PBSO and county partnerships, corporate partners and reviews. Assistants weigh what others say about you."],
    ["Open to AI crawlers", "Check robots.txt and firewall rules for GPTBot, ClaudeBot, PerplexityBot and Google-Extended. Keep key pages as server-rendered HTML."],
    ["Fresh and structured", "Update adoption, event and campaign pages often, with clear headings, tables and schema."],
    ["Measure share of voice", "Run the prompt set monthly across ChatGPT, Gemini, Perplexity, Copilot and AI Overviews. Log mentions, citations and accuracy."],
  ], { secKey: "geo", cols: 3, headSize: 16, bodySize: 14, h: 4.6 });

  // ---------- SECTION D: AEO ----------
  const E = "AEO";
  sectionSlide(E, "AEO: Answer Engine Optimization", "Short, structured answers that win featured snippets, People Also Ask and voice results");

  const aeo = [
    ["Adoption questions", ["how do I adopt a dog from Big Dog Ranch Rescue", "how much does it cost to adopt a dog in Florida", "what do I need to adopt a dog", "can I adopt a dog if I rent", "how long does dog adoption take", "do rescue dogs come vaccinated and spayed", "can I return an adopted dog", "what is a cage-free dog rescue"], [["Format", "40 to 60 word direct answer under a question heading."], ["Schema", "FAQPage on the Adopt page."], ["Target", "Featured snippets and People Also Ask."], ["Confirm", "Fees, policies and requirements with the client first."]]],
    ["Foster and volunteer questions", ["how does dog fostering work", "do foster dogs cost money", "what supplies do I need to foster a dog", "can I foster a dog for a short time", "how old do you have to be to volunteer at an animal shelter", "how do I get community service hours with dogs", "what do dog rescue volunteers do", "can groups volunteer at a dog rescue"], [["Format", "Step lists and short Q&A blocks."], ["Schema", "FAQPage and HowTo."], ["Target", "Voice search and AI summaries."], ["Confirm", "Age limits, group rules and orientation steps."]]],
    ["Donation and trust questions", ["is Big Dog Ranch Rescue a good charity", "is Big Dog Ranch Rescue a nonprofit", "where does my donation go", "are donations to dog rescues tax deductible", "how can I help a dog rescue without adopting", "what dog food can I donate", "who founded Big Dog Ranch Rescue", "where is Big Dog Ranch Rescue located"], [["Format", "Fact-first answers with sources and dates."], ["Schema", "Organization, DonateAction, FAQPage."], ["Target", "AI answers and knowledge panel."], ["Confirm", "Ratings, financial details and founder facts."]]],
  ];
  aeo.forEach((g) => keywordSlide("aeo", E, "AEO  |  Question targets", g[0], g[1], g[2]));

  s = newContent(E, "aeo", "AEO", "Answer-ready page template");
  cards(s, [
    ["Question as heading", "Use the exact wording people search, in an H2 or H3."],
    ["Answer first", "Give a direct 40 to 60 word answer straight after the heading, then add detail."],
    ["Mark it up", "FAQPage, HowTo, Event and Organization schema where the content matches."],
    ["Update and track", "Review Search Console queries and People Also Ask monthly, then add the new questions."],
  ], { secKey: "aeo", cols: 2 });

  // ---------- Measurement ----------
  const M = "Wrap-up";
  s = newContent(M, "paid", "Measurement and next steps", "How we will measure success");
  table(s, ["Channel", "Key metrics", "Cadence"], [
    ["Google Search Ads", "Adoption applications, foster and volunteer forms, donations, CPA, search terms", "Weekly first month, then bi-weekly"],
    ["SEO", "Non-brand organic clicks, rankings for pillar keywords, GBP actions, referring domains", "Monthly"],
    ["GEO", "Mentions, citations and accuracy across ChatGPT, Gemini, Perplexity, Copilot", "Monthly prompt audit"],
    ["AEO", "Featured snippets, People Also Ask wins, FAQ page traffic", "Monthly"],
  ], [2.6, 6.6, 2.93], "paid", 1.8, 0.68);
  s.addText("Next steps: 1) validate keywords and bids, 2) confirm current offers and policies, 3) set up conversion tracking, 4) launch Brand and Adopt campaigns, 5) start pillar pages and the GEO baseline audit.", { x: 0.6, y: 5.45, w: 10.5, h: 0.9, fontSize: 16, color: C.text1, margin: 0, valign: "top", isTextBox: true });

  await pres.writeFile({ fileName: path.join(__dirname, "BDRR_Media_and_Keyword_Strategy.pptx") });
  await applyTheme(path.join(__dirname, "BDRR_Media_and_Keyword_Strategy.pptx"), THEME);
  console.log("done");
})();
