"""Builds "JCS Case for Miami Dade" in the Alkimia look & feel.

All copy comes verbatim from the approved deck. Images that could not be
exported from the source copy are drawn as labelled image slots (SLOTS) and
can be filled by dropping files in build/slots/slide_<n>_<k>.png and re-running.

Run:  python3 -I build_deck.py
"""
import os, glob
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "build", "img")
SLOTS = os.path.join(HERE, "build", "slots")
OUT = os.path.join(HERE, "JCS-Case-Miami-Dade-Alkimia.pptx")

if os.environ.get("SMALL"):  # lighter build for Google Slides import (connector upload limit)
    OUT = os.path.join(HERE, "build", "JCS-Case-Miami-Dade-Alkimia-small.pptx")
    for src, dst, mx in ((IMG, IMG + "_s", 1300), (SLOTS, SLOTS + "_s", 1500)):
        os.makedirs(dst, exist_ok=True)
        for f in glob.glob(os.path.join(src, "*.png")):
            im = Image.open(f)
            im.thumbnail((mx, mx))
            alpha = src == IMG and im.mode == "RGBA" and im.getchannel("A").getextrema()[0] < 250
            if not alpha and im.mode == "RGBA":
                bg = Image.new("RGB", im.size, "white"); bg.paste(im, mask=im.getchannel("A")); im = bg
            out = os.path.join(dst, os.path.basename(f))
            if alpha:
                im.save(out, optimize=True)
            else:
                im.convert("RGB").save(out[:-4] + ".jpg", quality=80, optimize=True)
                im.convert("RGB").save(out[:-4] + ".png") if False else None
    IMG, SLOTS = IMG + "_s", SLOTS + "_s"

# ---- Alkimia palette (styles.css / salamancadeck) -------------------------
BG1, BG2 = "1B1030", "3A265C"
PURPLE, PURPLE_L, PURPLE_D = "6B4FA1", "8B6BB8", "4A3070"
CARD, CARD_LINE = "2C1D49", "5A4287"
LAV, GOLD, WHITE, MUTED = "E9E4F4", "E3B256", "FFFFFF", "C9BFE0"
FONT = "Inter"


def rgb(h): return RGBColor.from_string(h)


prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
W, H = 13.333, 7.5
state = {"n": 0}


def img(name):
    p = os.path.join(IMG, name)
    return p if os.path.exists(p) else p[:-4] + ".jpg"


def new_slide(footer=True, light=False):
    s = prs.slides.add_slide(BLANK)
    state["n"] += 1
    f = s.background.fill
    f.gradient(); f.gradient_angle = 315
    f.gradient_stops[0].color.rgb = rgb(BG1)
    f.gradient_stops[1].color.rgb = rgb(BG2)
    # soft glow, echoes the purple haze of the Alkimia cover
    g = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(8.8), Inches(-3.2), Inches(8), Inches(8))
    g.fill.gradient(); g.fill.gradient_angle = 90
    g.fill.gradient_stops[0].color.rgb = rgb("5B3F94"); g.fill.gradient_stops[1].color.rgb = rgb(BG1)
    g.line.fill.background()
    _alpha(g, 28)
    s.shapes._spTree.remove(g._element); s.shapes._spTree.insert(2, g._element)
    s._num = state["n"]
    if footer:
        add_footer(s)
    return s


def _alpha(shape, pct):
    sf = shape.fill._xPr.find(qn("a:gradFill"))
    for c in sf.iter(qn("a:srgbClr")):
        a = etree.SubElement(c, qn("a:alpha")); a.set("val", str(pct * 1000))


def add_footer(s):
    pic(s, "alk_white.png", 0.6, 6.98, h=0.3)
    t = text(s, W - 1.6, 6.98, 1.0, 0.3, str(s._num), 12, MUTED, align=PP_ALIGN.RIGHT)


def pic(s, name, x, y, w=None, h=None, path=None):
    p = path or img(name)
    im = Image.open(p)
    r = im.width / im.height
    if w and not h: h = w / r
    if h and not w: w = h * r
    return s.shapes.add_picture(p, Inches(x), Inches(y), Inches(w), Inches(h))


def rect(s, x, y, w, h, fill=CARD, line=CARD_LINE, radius=0.08, shape=None):
    sh = s.shapes.add_shape(shape or MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape is None:
        sh.adjustments[0] = radius
    if fill: sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
    else: sh.fill.background()
    if line: sh.line.color.rgb = rgb(line); sh.line.width = Pt(1)
    else: sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def text(s, x, y, w, h, content, size=20, color=WHITE, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=0, line=1.15, space_after=0, italic=False):
    """content: str or list of paragraphs; paragraph = str | dict(t, size, color, bold, bullet)"""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    paras = content if isinstance(content, list) else [content]
    for i, pr in enumerate(paras):
        d = pr if isinstance(pr, dict) else {"t": pr}
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = d.get("align", align)
        p.line_spacing = line
        p.space_after = Pt(d.get("after", space_after))
        for rt, rb in (d["runs"] if "runs" in d else [(d["t"], d.get("bold", bold))]):
            r = p.add_run(); r.text = rt
            f = r.font; f.name = FONT; f.size = Pt(d.get("size", size)); f.bold = rb
            f.italic = italic; f.color.rgb = rgb(d.get("color", color))
            sp = d.get("spacing", spacing)
            if sp: r._r.get_or_add_rPr().set("spc", str(int(sp * 100)))
        if d.get("bullet"):
            pPr = p._p.get_or_add_pPr()
            ind = int(Pt(d.get("size", size)).emu * 1.1)
            pPr.set("marL", str(ind)); pPr.set("indent", str(-ind))
            bc = etree.SubElement(pPr, qn("a:buClr")); c = etree.SubElement(bc, qn("a:srgbClr")); c.set("val", GOLD)
            bu = etree.SubElement(pPr, qn("a:buChar")); bu.set("char", "•")
    return tb


def eyebrow(s, label, y=0.6):
    rect(s, 0.6, y + 0.04, 0.35, 0.05, fill=GOLD, line=None, shape=MSO_SHAPE.RECTANGLE)
    text(s, 1.1, y - 0.02, 11, 0.3, label, 13, GOLD, bold=True, spacing=2)


def title(s, t, y=1.05, size=36, w=11.6, h=1.4):
    return text(s, 0.6, y, w, h, t, size, WHITE, bold=True, line=1.1)


def chip_logo(s, name, x, y, h):
    im = Image.open(img(name)); w = h * im.width / im.height
    rect(s, x, y, w + 0.3, h + 0.2, fill=WHITE, line=None, radius=0.12)
    pic(s, name, x + 0.15, y + 0.1, h=h)
    return w + 0.3


def partner_strip(s, y=6.55, names=("mdc.png", "jcs.png", "l988.png"), h=0.42, right=True):
    widths = [Image.open(img(n)).width / Image.open(img(n)).height * h + 0.3 for n in names]
    x = W - 0.6 - sum(widths) - 0.15 * (len(names) - 1) if right else 0.6
    for n, w in zip(names, widths):
        chip_logo(s, n, x, y, h); x += w + 0.15


def card_header(s, x, y, w, label, fill=PURPLE):
    r = rect(s, x, y, w, 0.62, fill=fill, line=None, radius=0.2)
    text(s, x + 0.3, y, w - 0.6, 0.62, label, 15, WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.5)


def slot(s, n, k, x, y, w, h, label, crop=None):
    """Image slot: fills from build/slots/slide_<n>_<k>.* when present, otherwise draws a marked frame."""
    f = glob.glob(os.path.join(SLOTS, "slide_%s_%s.*" % (n, k)))
    if f:
        im = Image.open(f[0]); r = im.width / im.height
        ww, hh = (w, w / r) if w / h < r else (h * r, h)
        s.shapes.add_picture(f[0], Inches(x + (w - ww) / 2), Inches(y + (h - hh) / 2), Inches(ww), Inches(hh))
        return
    b = rect(s, x, y, w, h, fill="241640", line=PURPLE_L, radius=0.04)
    b.line.dash_style = 4; b.line.width = Pt(1.5)
    text(s, x, y, w, h, [{"t": "IMAGE FROM ORIGINAL SLIDE %s" % n, "size": 14, "bold": True, "color": GOLD, "spacing": 2},
                         {"t": label, "size": 14, "color": MUTED}],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, space_after=4)


def place_slots(s, n, x, y, w, h, label, gap=0.3):
    """Places every extracted image of original slide n side by side, scaled to a common height."""
    fs = sorted(glob.glob(os.path.join(SLOTS, "slide_%s_*.*" % n)), key=lambda f: int(os.path.splitext(f)[0].rsplit("_", 1)[1]))
    if not fs:
        return slot(s, n, 1, x, y, w, h, label)
    ims = [Image.open(f) for f in fs]
    ratios = [i.width / i.height for i in ims]
    hh = min(h, (w - gap * (len(ims) - 1)) / sum(ratios))
    tot = sum(r_ * hh for r_ in ratios) + gap * (len(ims) - 1)
    cx = x + (w - tot) / 2
    cy = y + (h - hh) / 2
    for f, r_ in zip(fs, ratios):
        s.shapes.add_picture(f, Inches(cx), Inches(cy), Inches(r_ * hh), Inches(hh)); cx += r_ * hh + gap


def section(label, big, sub=None, sub2=None, logos=("jcs.png",), left_logos=()):
    s = new_slide(footer=False)
    rect(s, 0.9, 2.55, 1.0, 0.07, fill=GOLD, line=None, shape=MSO_SHAPE.RECTANGLE)
    text(s, 0.9, 2.0, 10, 0.4, label, 18, GOLD, bold=True, spacing=2)
    text(s, 0.9, 3.0, 10.8, 1.6, big, 54, WHITE, bold=True, line=1.05)
    if sub: text(s, 0.9, 4.7, 10.8, 1.3, sub, 24, LAV, line=1.3, space_after=6)
    pic(s, "alk_white.png", 0.9, 0.7, h=0.5)
    x = 11.3 if len(logos) == 1 else 9.3
    cx = W - 0.6
    for n in reversed(logos):
        im = Image.open(img(n)); w = 0.55 * im.width / im.height + 0.3
        chip_logo(s, n, cx - w, 0.55, 0.55); cx -= w + 0.15
    return s


# ======================================================================
# 1 — Cover
s = new_slide(footer=False)
pic(s, "alk_white.png", 0.9, 0.7, h=0.8)
rect(s, 4.0, 0.75, 0.02, 0.7, fill=CARD_LINE, line=None, shape=MSO_SHAPE.RECTANGLE)
pic(s, "cm_white.png", 4.3, 0.85, h=0.5)
rect(s, 0.9, 2.95, 1.0, 0.07, fill=GOLD, line=None, shape=MSO_SHAPE.RECTANGLE)
text(s, 0.9, 3.15, 10.5, 0.5, "ALKIMIA + Civil Mafia ", 20, GOLD, bold=True, spacing=3)
text(s, 0.9, 3.7, 11.5, 1.6, "Capabilities, partners and 988 Case", 50, WHITE, bold=True, line=1.05)
text(s, 0.9, 5.9, 9.5, 1.0, [{"t": "Prepared for: Amanda Dominguez", "size": 22, "bold": True},
                              {"t": "Mental Health Program Manager @ Miami-Dade County | LMHC, NCC", "size": 17, "color": MUTED}],
     space_after=4)
chip_logo(s, "mdc.png", 11.0, 6.2, 0.7)

# 2 — Public Impact Communications
s = new_slide()
eyebrow(s, "01 / Social Impact Unit")
title(s, "Public Impact Communications™", y=1.2, size=48)
text(s, 0.6, 2.7, 10.6, 3, "In collaboration with public institutions and organizations like JCS, we develop and execute "
     "measurable communication strategies, creativity and execution while increasing awareness, engagement and participation.",
     28, LAV, line=1.35)

# 3 — Capabilities of both partners
s = new_slide()
eyebrow(s, "01 / Social Impact Unit")
title(s, "Public Impact Communications™", y=1.0, size=34, h=0.8)
for x, logo, lh, items in [
    (0.6, "alk_white.png", 0.85, ["Public Sector Strategic Communication", "Multicultural Community Outreach",
                                  "Storytelling Creative Development", "Core Elements"]),
    (6.85, "cm_white.png", 0.6, ["Paid Media Strategy", "Impact Awareness Campaigns",
                                 "Performance Measurement", "Community Impact"])]:
    rect(s, x, 2.0, 5.9, 4.6)
    pic(s, logo, x + 0.5, 2.4 + (0.85 - lh) / 2 if logo != "alk_white.png" else 2.4, h=lh)
    text(s, x + 0.5, 3.55, 5.0, 2.9, [{"t": i, "bullet": True, "after": 6} for i in items], 19, WHITE, line=1.15)

# 4 — Back to the community
s = new_slide()
eyebrow(s, "01 / Social Impact Unit")
text(s, 0.6, 1.5, 12, 2.0, "PAID MEDIA CAMPAIGN DEVELOPMENT = BACK TO THE COMMUNITY", 44, WHITE, bold=True, line=1.1)
rect(s, 0.6, 3.75, 12.1, 2.6)
pic(s, "cmf_white.png", 1.0, 4.35, h=1.35)
for i, t in enumerate(["BOARD DIRECTOR", "COMMUNITY IMPACT ", "KIDS SOCCER CLINICS"]):
    text(s, 5.3, 4.1 + i * 0.7, 6.8, 0.5, t, 24, GOLD if i == 0 else WHITE, bold=True, spacing=2,
         anchor=MSO_ANCHOR.MIDDLE)

# 5-6 — Core Elements (website content, rebuilt as editable shapes)
def element_card(s, x, y, w, h, head, items, badge=None):
    rect(s, x, y, w, h)
    rect(s, x, y, 0.09, h, fill=GOLD, line=None, shape=MSO_SHAPE.RECTANGLE)
    text(s, x + 0.4, y + 0.3, w - 0.8, 0.8, head, 22, WHITE, bold=True, line=1.1)
    if badge:
        b = rect(s, x + w - 1.3, y + 0.32, 0.9, 0.34, fill=GOLD, line=None, radius=0.5)
        text(s, x + w - 1.3, y + 0.32, 0.9, 0.34, badge, 13, BG1, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 0.4, y + 1.15, w - 0.8, h - 1.3, [{"t": i, "bullet": True, "after": 5} for i in items], 16, LAV, line=1.15)

s = new_slide()
title(s, "Our Core Elements", y=0.6, size=40, h=0.8)
text(s, 0.6, 1.45, 12, 0.5, "The capabilities we combine to move your brand from strategy to execution.", 20, MUTED)
for i, (h_, it) in enumerate([
        ("Business Intelligence", ["Digital Marketing Strategy", "Strategic Planning", "Social Listening", "Consumer Insights",
                                   "Research & Benchmarking", "Competitive Review"]),
        ("Creative & Content", ["Digital Art Direction & Design", "Copywriting", "Content Creation & Digital Audiovisual Production"]),
        ("Media & Activation", ["Paid Media Management", "Mix Media Analysis", "Campaign Production and Execution"])]):
    element_card(s, 0.6 + i * 4.1, 2.3, 3.9, 4.35, h_, it)

s = new_slide()
title(s, "Our Core Elements", y=0.6, size=40, h=0.8)
element_card(s, 0.6, 1.9, 5.9, 4.5, "Technology & Innovation", ["UX/UI Design", "Frontend & Backend Development", "E-commerce Platforms Implementation"])
element_card(s, 6.8, 1.9, 5.9, 4.5, "AI & Automation ", ["AI Strategy", "Workflow & Marketing Automation", "Custom AI Agents & Copilots",
                                                         "AI-Powered Content Tools", "Predictive Analytics"], badge="2026")

# 7 — Core Capabilities
s = new_slide()
title(s, "Core Capabilities", y=0.6, size=40, h=0.8)
text(s, 0.6, 1.4, 11.5, 1.0, "We provide senior expertise, creative leadership, and execution that help you deliver exceptional work while growing your business.",
     20, MUTED, line=1.3)
text(s, 0.6, 2.55, 11, 0.4, "Our Business Transformation Units:", 15, GOLD, bold=True, spacing=2)
for i, (n, tag, d) in enumerate([
        ("Franchise Growth Systems™", "Scale your franchise with confidence.", "Grow your franchise network while maintaining brand consistency, operational excellence, and local relevance."),
        ("Public Impact Communications™", "Build trust through strategic communication.", "Communicate public initiatives clearly while increasing awareness, engagement and participation."),
        ("Growth Studio™", "Senior strategy, seamlessly integrated with your team.", "Senior strategic and creative expertise without increasing permanent overhead.")]):
    x = 0.6 + i * 4.1
    rect(s, x, 3.1, 3.9, 3.5, fill=PURPLE if i == 1 else CARD, line=None if i == 1 else CARD_LINE)
    text(s, x + 0.35, 3.4, 3.2, 0.9, n, 22, WHITE, bold=True, line=1.1)
    text(s, x + 0.35, 4.35, 3.2, 0.8, tag, 16, GOLD if i != 1 else "FFE9B8", bold=True, line=1.2)
    text(s, x + 0.35, 5.15, 3.2, 1.4, d, 15, LAV, line=1.3)

# 8-9 — original slides 5 & 6 (image only in source)
def runs(txt):
    """'plain **bold** plain' -> [(text, bold)]"""
    out = []
    for i, part in enumerate(txt.split("**")):
        if part: out.append((part, i % 2 == 1))
    return out


def feature(s, icon, x, y, w, head, body=None, hs=22, bs=16, iw=0.8):
    pic(s, icon, x, y, w=iw)
    tx = x + iw + 0.3
    text(s, tx, y - 0.05, w - iw - 0.3, 1.0, head, hs, WHITE, bold=True, line=1.1)
    if body:
        text(s, tx, y + 0.85, w - iw - 0.3, 2.2, [{"runs": runs(body)}], bs, LAV, line=1.25)


# 8 - Wellness for Everyone (original slide 5, rebuilt as editable)
s = new_slide(footer=False)
pic(s, "wellness_art.png", 7.6, 0.0, h=H)
rect(s, 0.0, 1.25, 7.0, 1.05, fill=WHITE, line=None, shape=MSO_SHAPE.RECTANGLE)
text(s, 0.6, 1.25, 6.4, 1.05, "Wellness for Everyone", 38, PURPLE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.6, 2.75, 6.5, 3.8, [{"runs": runs("We believe health is a **journey of simplicity, clarity, and accessibility**. Our content is designed to fit seamlessly into any lifestyle, empowering our readers with **practical, expert-backed guidance** on mental health, physical fitness, nutrition, relationships, sleep, cognitive health, and more.")}],
     21, WHITE, line=1.3)

# 9 - original slide 6, rebuilt as editable (split over two slides)
s = new_slide()
feature(s, "ic_bilingual.png", 0.6, 1.0, 5.9, "Bilingual & Culturally Relevant Content",
        "Available in **English and Spanish**, our content is crafted to address the specific needs and priorities of **Hispanic and Latinx communities in the U.S.**, with an open approach that can both include the general U.S. market and Latin American audiences.", bs=14)
feature(s, "ic_board.png", 6.9, 1.0, 5.9, "A Board of Specialists Ensuring Accuracy",
        "Our **multidisciplinary team**—including doctors, nutritionists, mental health professionals, and fitness experts—**reviews and validates every piece of content**, aligning with the highest medical and scientific standards.", bs=14)
feature(s, "ic_expert.png", 0.6, 4.05, 5.9, "Expert-Vetted, Evidence-Based Information",
        "Every article is **crafted by qualified writers and reviewed by specialists**, ensuring content is **accurate, up-to-date, and backed by scientific research**. No fads, no misinformation—just **trustworthy, actionable insights.**", bs=14)
feature(s, "ic_conscious.png", 6.9, 4.05, 5.9, "Conscious Language for Inclusive Communication",
        "Our **Compassion-First Approach** ensures clarity, inclusivity, and respect. We avoid jargon, reduce stigma, and prioritize **language that empowers and represents everyone**, making health and wellness **accessible to all.**", bs=14)

s = new_slide()
feature(s, "ic_integrity.png", 0.6, 1.0, 6.2, "Integrity & Transparency at Our Core",
        "We uphold **strict editorial independence and source only from credible, primary research**. Our commitment to **honesty and trustworthiness** means that every recommendation is grounded in **fact, not influence.**", bs=15)
feature(s, "ic_ethical.png", 0.6, 4.2, 6.2, "Ethical & Responsible Use of AI",
        "We integrate **AI technology responsibly** to enhance quality while maintaining **strict human oversight.** Our editorial process ensures AI-assisted content meets the highest standards of accuracy, empathy, and reliability.", bs=15)
feature(s, "ic_gdpr.png", 7.4, 1.0, 5.3, "General Data Protection Regulation (GDPR) Compliance", None, hs=20)
rect(s, 7.4, 2.5, 5.3, 4.1, fill=WHITE, line=None, radius=0.04)
pic(s, "devices.png", 7.4 + (5.3 - 4.1 * 458 / 630) / 2, 2.5, h=4.1)

# 10 — The Case (section)
s = section("The Case", "Jewish Community Services",
            [{"t": "988 Florida Lifeline — Mental Health Awareness Campaign", "size": 26, "bold": True, "color": WHITE},
             {"t": "Campaign period July - October 2025", "size": 20, "color": LAV},
             {"t": "Miami-Dade & Monroe Counties", "size": 20, "color": LAV}],
            logos=("mdc.png", "jcs.png"))

# 11-13 — digital strategy / methodology (image-only in source)
for n, label in [(8, "JCS - 988 DIGITAL STRATEGY PROPOSAL"), (9, "JCS - METHODOLOGY & APPROACH"), (10, "JCS - METHODOLOGY & APPROACH")]:
    s = new_slide(); eyebrow(s, label)
    place_slots(s, n, 0.6, 1.2, 12.1, 5.4, "Re-insert the original slide image here")
    partner_strip(s, 6.9 - 0.05, h=0.3) if False else None

# 14-17 — research
for n, t in [(11, "How the conversation around suicide breaksdown in Miami Dade and Monroe county"),
             (12, "Men are more vocal about suicide on social media than women"),
             (13, "Depression is the common ground between cultures"),
             (14, "Across social media, the cultures similarities outgrow the differences around suicide")]:
    s = new_slide(); eyebrow(s, "RESEARCH")
    title(s, t, y=1.05, size=30, h=1.0)
    place_slots(s, n, 0.6, 2.2, 12.1, 4.45, "Re-insert the original chart / image here")

# 18 — strategy statement
s = new_slide()
eyebrow(s, "STRATEGY")
text(s, 1.0, 1.7, 11.3, 2.2, "WE BUILT A COMPREHENSIVE STRATEGY TO REACH THE CORRECT AUDIENCE, RAISE AWARENESS AND PROVIDE CRUCIAL SUPPORT WHEN THEY MAY NEED IT",
     34, WHITE, bold=True, line=1.2, align=PP_ALIGN.CENTER)
for i, t in enumerate(["Identify 988 Target", "Reach 988 Target", "Generate Awareness"]):
    x = 1.2 + i * 3.9
    o = rect(s, x, 4.9, 0.95, 0.95, fill=PURPLE, line=PURPLE_L, shape=MSO_SHAPE.OVAL)
    text(s, x, 4.9, 0.95, 0.95, str(i + 1), 28, WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 1.15, 4.9, 2.7, 0.95, t, 19, WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)

# 19 — target statement
s = new_slide()
eyebrow(s, "STRATEGY - IDENTIFY TARGET")
text(s, 0.9, 2.2, 11.5, 3, "Given the sensitivity of the subject, we understand the importance of tailoring creatives to engage with each age group. ",
     38, WHITE, bold=True, line=1.25)

# 20 — three audiences
s = new_slide()
eyebrow(s, "STRATEGY - IDENTIFY TARGET")
text(s, 0.6, 1.05, 12, 0.5, "INTERESTS AND NEEDS FOR EACH TARGET AUDIENCE AND THEIR AGES: ", 20, GOLD, bold=True, spacing=1)
cards = [("13-17 YO", ["Requires legally enabled platforms for underage audiences. ",
                       "We can reach them with specific content suitable for their level of understanding and developmental stage."]),
         ("18-24 YO", ["Individuals who may be experiencing crises themselves or seeking help for friends/family. ",
                       "Their needs and concerns may differ from younger audiences and we can deliver content and resources that address their unique challenges."]),
         ("25-45 YO", ["Comprises individuals facing crises and seeking support for themselves or their loved ones. ",
                       "They may have different experiences, responsibilities, and communication preferences compared to younger age groups."])]
for i, (a, ps) in enumerate(cards):
    x = 0.6 + i * 4.1
    rect(s, x, 1.8, 3.9, 4.95)
    rect(s, x + 0.3, 2.05, 1.05, 0.9, fill=WHITE, line=None, radius=0.12)
    pic(s, "", x + 0.45, 2.12, h=0.76, path=img("age%d.png" % (i + 1)))
    text(s, x + 1.6, 2.05, 2.2, 0.9, a, 26, WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 0.3, 3.2, 3.35, 3.4, [{"t": p, "after": 10, "bold": j == 0} for j, p in enumerate(ps)], 16, LAV, line=1.2)

# 21-22 — implementation phases
phases = [("1.", "BRANDING", "Through a holistic social media campaign we will announce the re-number 988. With visually impactful and shareable content, such as videos and images, we will communicate the purpose and benefits of the Lifeline.",
           ["Reddit & Twitter", "Meta", "SEM", "YouTube and CTV", "Tiktok"]),
          ("2.", "AWARENESS", "Now that users know about the new number, we will focus our efforts on increasing the line's visibility and JCS by expanding the reach to more platforms.",
           ["Phase 1 Tactics", "Display Banners & Video", "Gaming & Spotify", "CTV", "DOOH"])]
for num, head, para, items in phases:
    s = new_slide(); eyebrow(s, "STRATEGY - IMPLEMENTATION PHASES")
    o = rect(s, 0.6, 1.2, 1.0, 1.0, fill=PURPLE, line=PURPLE_L, shape=MSO_SHAPE.OVAL)
    text(s, 0.6, 1.2, 1.0, 1.0, num, 26, WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 1.9, 1.2, 8, 1.0, head, 44, WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 0.6, 2.7, 6.4, 3.5, para, 22, LAV, line=1.35)
    rect(s, 7.6, 2.5, 5.1, 3.9)
    text(s, 8.0, 2.85, 4.4, 3.4, [{"t": i, "bullet": True, "after": 12} for i in items], 24, WHITE, line=1.15)
    partner_strip(s, 6.45, names=("mdc.png", "jcs.png", "l988.png"), h=0.4)

# 23 — the case video frame + partners
s = new_slide(footer=False)
eyebrow(s, "JCS - THE CASE")
_v = Image.open(img("still.png")); vid = _v.crop((0, 0, _v.width, int(_v.height * 0.95))); vid.save(img("still_c.png"))
pic(s, "", 2.3, 1.1, h=4.8, path=img("still_c.png"))
x = 0.6
for n in ["cm_white.png"]:
    pic(s, n, x, 6.55, h=0.4); x += 2.2
cx = 3.3
for n in ["tm.png", "dcf.png", "mdc.png", "jcs.png", "l988.png"]:
    w = chip_logo(s, n, cx, 6.42, 0.45); cx += w + 0.2
pic(s, "alk_white.png", 11.2, 6.52, h=0.42)

# 24-25 — results
s = new_slide(); eyebrow(s, "CAMPAIGN RESULTS")
text(s, 0.6, 1.2, 12, 1.2, "Across all platforms, the 988 campaign achieved meaningful visibility and awareness throughout Miami-Dade and Monroe counties. ",
     26, LAV, line=1.3)
text(s, 0.6, 2.9, 6, 0.4, "OVERALL PERFORMANCE", 15, GOLD, bold=True, spacing=2)
for i, (lab, val) in enumerate([("Impressions:", "16,444,043 "), ("Clicks:", "55,027"), ("CTR:", "0.34%"), ("Unique Users:", "5,147,887 ")]):
    x = 0.6 + i * 3.08
    rect(s, x, 3.5, 2.9, 2.6)
    text(s, x + 0.3, 3.9, 2.4, 0.4, lab, 17, MUTED, bold=True)
    text(s, x + 0.3, 4.5, 2.4, 1.2, val.strip(), 30 if len(val) > 8 else 40, WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)

s = new_slide(); eyebrow(s, "CAMPAIGN RESULTS")
text(s, 0.6, 1.1, 12, 0.5, "AWARENESS THAT DROVE ACTION", 20, GOLD, bold=True, spacing=2)
for i, (h_, a, b) in enumerate([("REACH", "67K active users | 66K new users", "Visibility built sustained engagement across 10s avg. time."),
                                ("BEHAVIOR", "Behavior | 45K sessions from Organic Social", "Social content drove discovery and intent to learn more."),
                                ("IMPACT", "63K users in the U.S.", "Message expanded globally, proving digital empathy travels.")]):
    x = 0.6 + i * 4.1
    rect(s, x, 1.9, 3.9, 4.6)
    card_header(s, x, 1.9, 3.9, h_)
    text(s, x + 0.35, 2.85, 3.2, 1.5, a, 22, WHITE, bold=True, line=1.2)
    text(s, x + 0.35, 4.45, 3.2, 1.8, "↳ " + b, 17, LAV, line=1.3)

# 26-27 — platform impact
s = new_slide(); eyebrow(s, "CAMPAIGN RESULTS")
text(s, 0.6, 1.05, 12, 0.5, "WHERE EACH PLATFORM MADE ITS IMPACT  ", 20, GOLD, bold=True, spacing=2)
text(s, 0.6, 1.9, 11.5, 0.9, "Despite challenges by sensitivity policies on Google platforms:", 28, WHITE, bold=True, line=1.2)
text(s, 0.6, 3.1, 11.5, 3, [{"t": t, "bullet": True, "after": 16} for t in [
    "Message reached diverse audiences with empathy and consistency. ",
    "Meta and TikTok drove strong engagement and connection, especially among younger audiences.",
    "Basis delivered broad visibility at scale."]], 26, LAV, line=1.25)
s = new_slide(); eyebrow(s, "CAMPAIGN RESULTS")
text(s, 0.6, 1.05, 12, 0.5, "WHERE EACH PLATFORM MADE ITS IMPACT  ", 20, GOLD, bold=True, spacing=2)
Image.open(img("plat_c.png")).save(img("plat_c.png"))
rect(s, 1.6, 1.75, 10.1, 4.9, fill="EFEBEB", line=None, radius=0.03)
pic(s, "", 1.7, 1.85, h=4.7, path=img("plat_c.png"))

# 28 — statement
s = new_slide(); eyebrow(s, "CAMPAIGN RESULTS")
text(s, 0.9, 1.9, 11.5, 3.5, "OVERALL, THE CAMPAIGN DEMONSTRATED THAT EVEN WITHIN STRICT CONTENT FRAMEWORKS, AUTHENTIC AND COMPASSIONATE COMMUNICATION ABOUT MENTAL HEALTH CAN BREAK THROUGH AND INSPIRE AWARENESS",
     34, WHITE, bold=True, line=1.25, align=PP_ALIGN.CENTER)

# 29 — Donate campaign (section)
section("JSC - Donate Campaign", "Jewish Community Services", [{"t": "Multicultural Creative Proposal", "size": 28, "bold": True, "color": WHITE}], logos=("jcs.png",))

# 30-32 — multicultural outreach (image-only in source)
for n in (23, 24, 25):
    s = new_slide(); eyebrow(s, "MULTICULTURAL COMMUNITY OUTREACH")
    place_slots(s, n, 0.6, 1.2, 12.1, 5.4, "Re-insert the original creative image here")
    chip_logo(s, "jcs.png", W / 2 - 1.0, 6.55, 0.38) if False else None

# 33 — Food Security (section)
section("JSC - Food Security ", "Food Security Campaign", [{"t": "Creative Rationale", "size": 28, "bold": True, "color": WHITE}], logos=("jcs.png",))

# 34-35 — campaign overview
s = new_slide(); eyebrow(s, "CAMPAIGN OVERVIEW")
rect(s, 0.6, 1.4, 12.1, 5.1, fill=PURPLE_D, line=None)
text(s, 1.2, 1.9, 10, 0.4, "CORE CAMPAIGN ", 15, GOLD, bold=True, spacing=3)
text(s, 1.2, 2.6, 10.5, 2.2, "Food insecurity isn’t always visible.", 64, WHITE, bold=True, line=1.05)
rect(s, 1.2, 5.0, 0.9, 0.06, fill=GOLD, line=None, shape=MSO_SHAPE.RECTANGLE)
text(s, 1.2, 5.3, 10, 0.4, "TRAFFIC TO DONATE AND FIND HELP", 16, WHITE, bold=True, spacing=2)

s = new_slide(); eyebrow(s, "CAMPAIGN OVERVIEW")
rect(s, 0.6, 1.2, 12.1, 5.45)
rect(s, 0.6, 1.2, 0.18, 5.45, fill=GOLD, line=None, shape=MSO_SHAPE.RECTANGLE)
text(s, 1.2, 1.5, 11, 5, [
    {"t": "GOAL", "size": 15, "bold": True, "color": GOLD, "spacing": 2, "after": 4},
    {"t": "Increase awareness of JCS services across the food security pillar.", "bullet": True, "after": 3},
    {"t": "Enhance donor engagement and retention.", "bullet": True, "after": 14},
    {"t": "TARGET", "size": 15, "bold": True, "color": GOLD, "spacing": 2, "after": 4},
    {"t": "Families and individuals experiencing food insecurity or living near the poverty line, including Jewish and non-Jewish residents of Miami-Dade County. ", "bullet": True, "after": 14},
    {"t": "CREATIVE CONCEPT - “Food insecurity isn’t always visible.”", "size": 15, "bold": True, "color": GOLD, "spacing": 1, "after": 4},
    {"t": "A broad awareness and donor-education concept that challenges stereotypes around hunger, normalizes the need for food support, and highlights how quickly life circumstances can change for individuals and families.", "bullet": True}],
     19, WHITE, line=1.2)

# 36-38 — food security creatives (image-only in source)
for n in (28, 29, 30):
    s = new_slide(); eyebrow(s, "FOOD SECURITY CAMPAIGN")
    place_slots(s, n, 0.6, 1.2, 12.1, 5.4, "Re-insert the original creative image here")

# 39-40 — food security results
s = new_slide(); eyebrow(s, "CAMPAIGN RESULTS")
text(s, 0.6, 1.2, 12, 1.2, "The campaign outperformed the industry benchmark by +28% in CTR. By running two parallel audiences and objectives, we achieved efficiency both in awareness and direct action.",
     25, LAV, line=1.3)
text(s, 0.6, 3.25, 6, 0.4, "OVERALL PERFORMANCE", 15, GOLD, bold=True, spacing=2)
for i, (lab, val) in enumerate([("Impressions:", "1,953,648 "), ("Clicks:", "15,850"), ("CTR:", "1,67%")]):
    x = 0.6 + i * 4.1
    rect(s, x, 3.8, 3.9, 2.6)
    text(s, x + 0.4, 4.2, 3.2, 0.4, lab, 18, MUTED, bold=True)
    text(s, x + 0.4, 4.8, 3.2, 1.2, val.strip(), 46, WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)

s = new_slide(); eyebrow(s, "CAMPAIGN RESULTS")
text(s, 0.6, 1.1, 12, 0.5, "AWARENESS THAT DROVE PERFORMANCE", 20, GOLD, bold=True, spacing=2)
for i, (h_, rows) in enumerate([("GET HELP", [("Impressions:", "696,942"), ("Clicks:", "4,991"), ("CTR:", "1,64%"), ("Reach:", "152,968")]),
                                ("DONATE", [("Impressions:", "1,256,506"), ("Clicks:", "12,898"), ("CTR:", "1,69%"), ("Reach:", "590,295")])]):
    x = 0.6 + i * 6.15
    rect(s, x, 1.8, 5.95, 4.8)
    card_header(s, x, 1.8, 5.95, h_)
    for j, (a, b) in enumerate(rows):
        y = 2.7 + j * 0.95
        text(s, x + 0.4, y, 2.6, 0.7, a, 20, MUTED, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, x + 2.9, y, 2.8, 0.7, b, 30, WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)

# 41 — best creatives (two slides would split image/insight; keep paired)
for k, (pc, ins) in enumerate([("c1.png", "The creative that humanized the invisibility of hunger (overdue bills, debt, financial stress) resonated far more than direct visuals. Challenging the stereotypes around hunger was key to connecting with audiences who may not immediately identify with the idea of “homelessness” or food insecurity."),
                               ("c2.png", "The strongest-performing creative focused on empathy and action through a simple, human-centered message. Showing the direct impact of a donation generated a stronger emotional response and encouraged audiences to take immediate action.")]):
    s = new_slide(); eyebrow(s, "CAMPAIGN RESULTS")
    text(s, 0.6, 1.05, 12, 0.5, "BEST PERFORMING CREATIVES", 20, GOLD, bold=True, spacing=2)
    im = Image.open(img(pc)); hh = 5.0; ww = hh * im.width / im.height
    rect(s, 0.9, 1.7, ww + 0.2, hh + 0.2, fill=WHITE, line=None, radius=0.03)
    pic(s, "", 1.0, 1.8, h=hh, path=img(pc))
    rect(s, 5.2, 1.7, 7.5, 5.2)
    text(s, 5.6, 2.1, 6.7, 0.4, "INSIGHT", 15, GOLD, bold=True, spacing=3)
    text(s, 5.6, 2.8, 6.7, 4.0, ins, 21, WHITE, line=1.35)

# 42 — thank you
s = new_slide(footer=False)
rect(s, 0.9, 3.0, 1.0, 0.07, fill=GOLD, line=None, shape=MSO_SHAPE.RECTANGLE)
text(s, 0.9, 3.4, 11, 1.4, "Thank you! Gracias!", 72, WHITE, bold=True)
pic(s, "alk_white.png", 0.9, 0.7, h=0.8)
pic(s, "cm_white.png", 9.3, 6.4, h=0.55)
chip_logo(s, "jcs.png", 11.2, 6.28, 0.55) if False else None

# 43-44 — posting status (appendix)
for k in ("post1.png", "post2.png"):
    s = new_slide(footer=False)
    im = Image.open(img(k)); hh = 7.0; ww = hh * im.width / im.height
    rect(s, (W - ww) / 2 - 0.05, 0.2, ww + 0.1, hh + 0.1, fill=WHITE, line=None, radius=0.01)
    pic(s, "", (W - ww) / 2, 0.25, h=hh, path=img(k))

prs.save(OUT)
print("saved", OUT, len(prs.slides._sldIdLst), "slides")
