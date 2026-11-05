#!/usr/bin/env python3
"""Builds the site pages into SITE (default ../site-final) so shared parts stay consistent.
Usage: python3 build_site.py SITE_DIR
"""
import os
import re
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else "site-final"

NAV_ITEMS = [
    ("index.html", "Home"),
    ("early-years.html", "Early years"),
    ("printables.html", "Printables"),
    ("make.html", "Make your own"),
    ("frameworks.html", "Frameworks"),
]


def nav(current):
    out = ['<nav class="sitenav" aria-label="Site">', '    <a class="wordmark" href="index.html">Framework Finder</a>']
    for href, label in NAV_ITEMS:
        cur = ' aria-current="page"' if href == current else ""
        out.append('    <a href="%s"%s>%s</a>' % (href, cur, label))
    out.append("  </nav>")
    return "\n  ".join(out)


NAV_CSS = """
.sitenav { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding-block: 16px 0; }
.sitenav a { font-weight: 600; text-decoration: none; padding: 8px 14px; border: 2px solid var(--ink); }
.sitenav a[aria-current="page"] { background: var(--ink); color: var(--bg); }
.sitenav a.wordmark { border: 0; padding-left: 0; margin-right: auto; font-family: var(--display); font-size: 1.3rem; font-weight: 800; letter-spacing: -0.01em; }
@media (max-width: 640px) { .sitenav a.wordmark { flex: 1 0 100%; } }
"""

AREA_COLOURS = {
    "communication": "#1971c2", "personal-social": "#c2255c", "physical": "#c2410c", "literacy": "#6741d9",
    "mathematics": "#0c8599", "understanding-world": "#237a35", "expressive-arts": "#a16207",
}

SHARED_CSS = """
:root {
  --bg: #f3f6f8; --surface: #ffffff; --ink: #142330; --muted: #4f606c; --line: #d3dce2;
  --accent: #00756f; --accent-soft: #dff1ef; --mark: #ffd84d; --focus: #1c6ed5;
  --display: "Bricolage Grotesque", "Arial Narrow", Arial, sans-serif;
  --body: "Source Sans 3", system-ui, -apple-system, "Segoe UI", sans-serif;
  @@AREAS@@
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0d1a22; --surface: #13242e; --ink: #e7eff4; --muted: #9ab0bd; --line: #26394a;
    --accent: #4fd1c5; --accent-soft: #123a3d; --focus: #6aa8ff; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #0d1a22; --surface: #13242e; --ink: #e7eff4; --muted: #9ab0bd; --line: #26394a;
  --accent: #4fd1c5; --accent-soft: #123a3d; --focus: #6aa8ff; color-scheme: dark;
}
* { box-sizing: border-box; }
html { background: var(--bg); }
body {
  margin: 0; background: var(--bg); color: var(--ink); font: 17px/1.5 var(--body);
  padding-block: 0 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
}
img, svg { max-width: 100%; }
[hidden] { display: none !important; }
.wrap { max-width: 960px; margin-inline: auto; }
h1, h2, h3 { font-family: var(--display); margin: 0; line-height: 1.05; text-wrap: balance; }
p { margin: 0; }
a { color: inherit; }
:focus-visible { outline: 3px solid var(--focus); outline-offset: 2px; }
.btn { display: inline-flex; align-items: center; justify-content: center; min-height: 46px; padding: 0 20px; font: 600 1rem var(--body); text-decoration: none; border: 2px solid var(--ink); background: transparent; color: var(--ink); cursor: pointer; }
.btn.primary { background: var(--accent); border-color: var(--accent); color: var(--bg); }
.btn:hover { filter: brightness(1.08); }
.eyebrow { font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent); }
.sec { padding-block: 52px 0; }
.sec > h2 { font-size: clamp(1.8rem, 5vw, 2.5rem); font-weight: 800; letter-spacing: -0.01em; }
.sec > .intro { margin-top: 10px; color: var(--muted); max-width: 62ch; }
footer { margin-top: 64px; padding-top: 20px; border-top: 2px solid var(--ink); font-size: 0.88rem; color: var(--muted); max-width: 72ch; }
footer p + p { margin-top: 8px; }
.tiles { display: grid; grid-template-columns: minmax(0, 1fr); gap: 10px; margin-top: 20px; }
@media (min-width: 560px) { .tiles { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (min-width: 860px) { .tiles.three { grid-template-columns: repeat(3, minmax(0, 1fr)); } .tiles.four { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
.tile { display: flex; flex-direction: column; justify-content: space-between; gap: 18px; min-height: 120px; padding: 16px; background: var(--c, var(--ink)); color: #fff; text-decoration: none; }
.tile .t-name { font-family: var(--display); font-size: 1.35rem; font-weight: 700; line-height: 1.1; }
.tile .t-n { font-size: 0.92rem; font-weight: 600; opacity: 0.95; }
.tile:hover { filter: brightness(1.1); }
.grouplabel { margin-top: 26px; font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }
.rule-list { list-style: none; margin: 20px 0 0; padding: 0; border-top: 2px solid var(--ink); }
.rule-list li { border-bottom: 1px solid var(--line); }
.rule-list a { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 4px 16px; padding: 16px 0; text-decoration: none; }
.rule-list a:hover .rl-t { text-decoration: underline; }
.rl-t { font-family: var(--display); font-size: 1.3rem; font-weight: 700; }
.rl-d { grid-column: 1; color: var(--muted); max-width: 60ch; }
.rl-n { grid-row: 1 / span 2; grid-column: 2; align-self: center; font-weight: 600; color: var(--accent); white-space: nowrap; }
""".replace("@@AREAS@@", "\n  ".join("--a-%s: %s;" % (k, v) for k, v in AREA_COLOURS.items()))

FOOTER = """<footer>
    <p>Framework Finder is an independent resource. It is not run by, or endorsed by, the Department for Education, Ofsted or any organisation it links to.</p>
    <p>Sheets such as safeguarding, safer sleep, fire drill and risk assessment forms are general templates. Follow your own setting's policies and the current official requirements.</p>
  </footer>"""

FONTS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Andika:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Source+Sans+3:wght@400;500;600&display=swap">"""

COUNTS_JS = """
function fillCounts(json) {
  const items = json.items;
  const byArea = {}, byCat = {};
  items.forEach((i) => {
    byCat[i.cat] = (byCat[i.cat] || 0) + 1;
    (i.areas || []).forEach((a) => { byArea[a] = (byArea[a] || 0) + 1; });
  });
  document.querySelectorAll("[data-area]").forEach((el) => { const n = byArea[el.dataset.area] || 0; el.textContent = n + (n === 1 ? " printable" : " printables"); });
  document.querySelectorAll("[data-cat]").forEach((el) => { const n = byCat[el.dataset.cat] || 0; el.textContent = n + (n === 1 ? " sheet" : " sheets"); });
  const total = items.length, ey = items.filter((i) => i.phases.includes("early")).length;
  document.querySelectorAll("[data-total]").forEach((el) => { el.textContent = total; });
  document.querySelectorAll("[data-ey]").forEach((el) => { el.textContent = ey; });
}
fetch("resources.json").then((r) => r.ok ? r.json() : Promise.reject()).then(fillCounts).catch(() => {});
"""


def page(title, body, css="", script="", current="", extra_head=""):
    return """<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%(title)s</title>
%(fonts)s
%(head)s
<style>
%(shared)s
%(nav_css)s
%(css)s
</style>
</head>
<body>
<div class="wrap">
  %(nav)s
%(body)s
  %(footer)s
</div>
<script>
%(script)s
</script>
</body>
</html>
""" % {"title": title, "fonts": FONTS, "head": extra_head, "shared": SHARED_CSS, "nav_css": NAV_CSS, "css": css,
       "nav": nav(current), "body": body, "footer": FOOTER, "script": script}


AREAS = [
    ("communication", "Communication and Language", "prime",
     "Listening, attention and understanding; speaking."),
    ("personal-social", "Personal, Social and Emotional Development", "prime",
     "Self-regulation; managing self; building relationships."),
    ("physical", "Physical Development", "prime",
     "Gross motor skills; fine motor skills."),
    ("literacy", "Literacy", "specific", "Comprehension; word reading; writing."),
    ("mathematics", "Mathematics", "specific", "Number; numerical patterns."),
    ("understanding-world", "Understanding the World", "specific",
     "Past and present; people, culture and communities; the natural world."),
    ("expressive-arts", "Expressive Arts and Design", "specific",
     "Creating with materials; being imaginative and expressive."),
]


def tile(a):
    return ('<a class="tile" style="--c: var(--a-%s)" href="printables.html#area-%s"><span class="t-name">%s</span>'
            '<span class="t-n" data-area="%s">Printables</span></a>') % (a[0], a[0], a[1], a[0])


def build_home():
    prime = "\n      ".join(tile(a) for a in AREAS if a[2] == "prime")
    spec = "\n      ".join(tile(a) for a in AREAS if a[2] == "specific")
    body = """
  <header class="hero">
    <p class="eyebrow">For nursery, preschool and reception practitioners</p>
    <h1>Early years, <span>ready to print.</span></h1>
    <p class="lead">Observation sheets, planning, records and activity sheets that match the seven areas of learning. There are tools for teachers and student teachers too.</p>
    <div class="cta">
      <a class="btn primary" href="printables.html#early">Browse early years printables</a>
      <a class="btn" href="make.html">Make a sheet with names on</a>
    </div>
    <p class="count"><strong data-total>267</strong> printables, <strong data-ey>200</strong> of them for early years. Every sheet is an original design, free to print.</p>
  </header>

  <section class="sec" aria-labelledby="h-areas">
    <h2 id="h-areas">Find a sheet by area of learning</h2>
    <p class="intro">The EYFS has three prime areas and four specific areas. Open one to see the sheets that support it.</p>
    <p class="grouplabel">Prime areas</p>
    <div class="tiles three">
      %s
    </div>
    <p class="grouplabel">Specific areas</p>
    <div class="tiles four">
      %s
    </div>
  </section>

  <section class="sec" aria-labelledby="h-need">
    <h2 id="h-need">Start with what you need today</h2>
    <ul class="rule-list">
      <li><a href="printables.html#ey-observation"><span class="rl-t">Observe and assess</span><span class="rl-d">Observation sheets, WOW moment slips, a tracker for each area of learning, handover and baseline sheets.</span><span class="rl-n" data-cat="ey-observation"></span></a></li>
      <li><a href="printables.html#ey-planning"><span class="rl-t">Plan and set up provision</span><span class="rl-d">Weekly plans, continuous provision, enhancements, letters to families and risk-benefit sheets.</span><span class="rl-n" data-cat="ey-planning"></span></a></li>
      <li><a href="printables.html#ey-records"><span class="rl-t">Records and checklists</span><span class="rl-d">Registers, safer sleep and nappy charts, hygiene and outdoor checks, staff rota and logs.</span><span class="rl-n" data-cat="ey-records"></span></a></li>
      <li><a href="printables.html#ey-literacy"><span class="rl-t">Letters, sounds and words</span><span class="rl-d">Sound cards, letter formation, word cards, reading records and bookmarks.</span><span class="rl-n" data-cat="ey-literacy"></span></a></li>
      <li><a href="printables.html#ey-maths"><span class="rl-t">Early maths</span><span class="rl-d">Dot patterns, shape, day, month and number word cards, measuring and counting records.</span><span class="rl-n" data-cat="ey-maths"></span></a></li>
      <li><a href="printables.html#ey-roleplay"><span class="rl-t">Role play and provision labels</span><span class="rl-d">Sign sets for a café, shop, vet, surgery, post office, garden centre, builders' yard and space station.</span><span class="rl-n" data-cat="ey-roleplay"></span></a></li>
      <li><a href="printables.html#ey-topics"><span class="rl-t">Topics and seasons</span><span class="rl-d">A topic web, vocabulary cards and nature hunts for ten topics and all four seasons.</span><span class="rl-n" data-cat="ey-topics"></span></a></li>
      <li><a href="printables.html#ey-activities"><span class="rl-t">Child activity sheets</span><span class="rl-d">Pre-writing patterns, tracing, number and letter cards, emotion faces and daily charts.</span><span class="rl-n" data-cat="ey-activities"></span></a></li>
    </ul>
  </section>

  <section class="sec feature" aria-labelledby="h-make">
    <div class="f-text">
      <p class="eyebrow">Make your own</p>
      <h2 id="h-make">Type the names. Print the sheets.</h2>
      <p class="intro">Name tracing sheets, peg and drawer labels and class registers, made with your children's names. Names stay in your browser and are never sent anywhere.</p>
      <p style="margin-top:18px"><a class="btn primary" href="make.html">Open the tools</a></p>
    </div>
    <svg class="f-art" viewBox="0 0 420 210" role="img" aria-label="Sample name tracing sheet with the name Ava in dotted letters">
      <rect x="1" y="1" width="418" height="208" fill="var(--surface)" stroke="var(--ink)" stroke-width="2"/>
      <g stroke="var(--line)" stroke-width="1.2">
        <line x1="20" y1="48" x2="400" y2="48"/><line x1="20" y1="82" x2="400" y2="82" stroke-dasharray="5 4"/><line x1="20" y1="116" x2="400" y2="116"/>
        <line x1="20" y1="118" x2="400" y2="118" stroke="none"/>
        <line x1="20" y1="156" x2="400" y2="156"/><line x1="20" y1="190" x2="400" y2="190"/>
      </g>
      <text x="26" y="112" font-family="Andika, 'Trebuchet MS', sans-serif" font-size="82" font-weight="400" fill="var(--ink)">Ava</text>
      <text x="206" y="112" font-family="Andika, 'Trebuchet MS', sans-serif" font-size="82" font-weight="400" fill="none" stroke="var(--ink)" stroke-width="1.6" stroke-dasharray="2 5" stroke-linecap="round">Ava</text>
    </svg>
  </section>

  <section class="sec" aria-labelledby="h-roles">
    <h2 id="h-roles">Teaching or training?</h2>
    <p class="intro">Lesson plans, organisers and revision tools for the classroom, and a toolkit for placements and early career years.</p>
    <div class="tiles three">
      <a class="tile" href="printables.html#teacher"><span class="t-name">For teachers</span><span class="t-n">Lesson plans, maths tools, organisers</span></a>
      <a class="tile" href="printables.html#student"><span class="t-name">For student teachers</span><span class="t-n">Placement, mentor and evidence tools</span></a>
      <a class="tile" href="frameworks.html"><span class="t-name">Official frameworks</span><span class="t-n">England, Scotland, Wales, Northern Ireland</span></a>
    </div>
  </section>

  <section class="sec" aria-labelledby="h-news">
    <h2 id="h-news">What changed recently</h2>
    <ul class="rule-list">
      <li><a href="early-years.html"><span class="rl-t">1 September 2026</span><span class="rl-d">New EYFS statutory framework versions took effect, with changes on safer sleep, screen use and banned dog breeds.</span><span class="rl-n">Read more</span></a></li>
      <li><a href="frameworks.html"><span class="rl-t">10 November 2025</span><span class="rl-d">Ofsted's new report cards and inspection changes began for early years and state-funded schools.</span><span class="rl-n">Sources</span></a></li>
    </ul>
  </section>
""" % (prime, spec)
    css = """
.hero { padding-block: 44px 8px; }
.hero h1 { margin-top: 14px; font-size: clamp(2.9rem, 10vw, 5.6rem); font-weight: 800; letter-spacing: -0.025em; max-width: 12ch; }
.hero h1 span { background: linear-gradient(transparent 62%, var(--mark) 62%, var(--mark) 92%, transparent 92%); }
.hero .lead { margin-top: 20px; max-width: 54ch; font-size: 1.2rem; color: var(--muted); }
.hero .cta { margin-top: 26px; display: flex; flex-wrap: wrap; gap: 12px; }
.hero .count { margin-top: 20px; color: var(--muted); font-size: 0.95rem; }
.feature { display: grid; grid-template-columns: minmax(0, 1fr); gap: 28px; align-items: center; }
@media (min-width: 820px) { .feature { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 48px; } }
.feature h2 { margin-top: 8px; }
.f-art { width: 100%; height: auto; }
"""
    return page("Framework Finder", body, css, COUNTS_JS, "index.html")


def build_hub():
    cards = []
    for k, name, kind, aspects in AREAS:
        cards.append("""      <article class="area" style="--c: var(--a-%s)">
        <p class="a-kind">%s area</p>
        <h3>%s</h3>
        <p class="a-asp">%s</p>
        <p class="a-link"><a href="printables.html#area-%s">See the sheets</a> <span class="a-n" data-area="%s"></span></p>
      </article>""" % (k, "Prime" if kind == "prime" else "Specific", name, aspects, k, k))
    body = """
  <header class="hubhead">
    <p class="eyebrow">Early years hub</p>
    <h1>The EYFS, and the sheets to go with it</h1>
    <p class="lead">A short guide to the Early Years Foundation Stage for England, with links to the official documents and the printables that support each area of learning.</p>
  </header>

  <section class="sec" aria-labelledby="h-eyfs">
    <h2 id="h-eyfs">The EYFS in brief</h2>
    <p class="intro">The EYFS statutory framework sets the standards for learning, development and care from birth to 5. It has seven areas of learning: three prime areas, which come first and underpin the rest, and four specific areas. Practitioners also think about three characteristics of effective teaching and learning: playing and exploring, active learning, and creating and thinking critically.</p>
    <div class="areas">
%s
    </div>
    <p class="fine">The aspects listed above follow the early learning goal headings. Check the current framework for the exact wording.</p>
  </section>

  <section class="sec" aria-labelledby="h-sets">
    <h2 id="h-sets">Setting essentials</h2>
    <ul class="rule-list">
      <li><a href="printables.html#ey-observation"><span class="rl-t">Observation and assessment</span><span class="rl-d">Capture what you see, then plan the next step.</span><span class="rl-n" data-cat="ey-observation"></span></a></li>
      <li><a href="printables.html#ey-planning"><span class="rl-t">Planning and provision</span><span class="rl-d">Weekly plans, provision, enhancements and letters to families.</span><span class="rl-n" data-cat="ey-planning"></span></a></li>
      <li><a href="printables.html#ey-records"><span class="rl-t">Records and checklists</span><span class="rl-d">Registers, safer sleep, nappy, hygiene and outdoor checks.</span><span class="rl-n" data-cat="ey-records"></span></a></li>
      <li><a href="make.html"><span class="rl-t">Make your own</span><span class="rl-d">Name tracing sheets, labels and registers with your children's names.</span><span class="rl-n">Tools</span></a></li>
    </ul>
  </section>

  <section class="sec" aria-labelledby="h-src">
    <h2 id="h-src">Official sources</h2>
    <p class="intro">These open on the owner's own page.</p>
    <ul class="rule-list">
      <li><a href="https://www.gov.uk/government/publications/early-years-foundation-stage-framework--2" target="_blank" rel="noopener"><span class="rl-t">EYFS statutory framework</span><span class="rl-d">Department for Education. The legal standards for providers in England.</span><span class="rl-n">GOV.UK</span></a></li>
      <li><a href="https://www.gov.uk/government/publications/development-matters--2" target="_blank" rel="noopener"><span class="rl-t">Development Matters</span><span class="rl-d">Non-statutory curriculum guidance that supports the framework.</span><span class="rl-n">GOV.UK</span></a></li>
      <li><a href="https://birthto5matters.org.uk/" target="_blank" rel="noopener"><span class="rl-t">Birth to 5 Matters</span><span class="rl-d">Non-statutory guidance that settings can use alongside the framework.</span><span class="rl-n">Birth to 5 Matters</span></a></li>
      <li><a href="https://www.gov.uk/progress-check-at-age-2-and-eyfs-profile" target="_blank" rel="noopener"><span class="rl-t">Progress check at age 2 and the EYFS profile</span><span class="rl-d">Official guidance on both.</span><span class="rl-n">GOV.UK</span></a></li>
      <li><a href="https://help-for-early-years-providers.education.gov.uk/" target="_blank" rel="noopener"><span class="rl-t">Help for early years providers</span><span class="rl-d">The DfE's support site for providers and childminders.</span><span class="rl-n">DfE</span></a></li>
      <li><a href="https://foundationyears.org.uk/2024/04/about-us/" target="_blank" rel="noopener"><span class="rl-t">Foundation Years</span><span class="rl-d">Free guidance, news and community for early years practitioners.</span><span class="rl-n">Foundation Years</span></a></li>
    </ul>
    <p class="fine">More official links for Scotland, Wales and Northern Ireland are on the <a href="frameworks.html">Frameworks page</a>.</p>
  </section>

  <section class="sec" aria-labelledby="h-upd">
    <h2 id="h-upd">What changed on 1 September 2026</h2>
    <p class="intro">New EYFS statutory framework versions took effect. The changes include safer sleep, a requirement to have regard to screen use, and prohibiting childcare where banned dog breeds are present. Open the framework to read the exact wording for your type of provider.</p>
  </section>
""" % "\n".join(cards)
    css = """
.hubhead { padding-block: 44px 4px; }
.hubhead h1 { margin-top: 12px; font-size: clamp(2.4rem, 8vw, 4.2rem); font-weight: 800; letter-spacing: -0.02em; max-width: 16ch; }
.hubhead .lead { margin-top: 18px; max-width: 58ch; font-size: 1.15rem; color: var(--muted); }
.areas { display: grid; grid-template-columns: minmax(0, 1fr); gap: 10px; margin-top: 22px; }
@media (min-width: 640px) { .areas { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.area { background: var(--c); color: #fff; padding: 18px; display: flex; flex-direction: column; gap: 8px; }
.area h3 { font-size: 1.35rem; font-weight: 700; }
.a-kind { font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.92; }
.a-asp { opacity: 0.97; }
.a-link { margin-top: auto; padding-top: 8px; font-weight: 600; }
.a-link a { text-decoration: underline; }
.a-n { opacity: 0.92; margin-left: 6px; }
.fine { margin-top: 14px; font-size: 0.9rem; color: var(--muted); }
"""
    return page("Early Years Hub", body, css, COUNTS_JS, "early-years.html")


MAKE_BODY = """
  <header class="mkhead">
    <p class="eyebrow">Make your own</p>
    <h1>Sheets with your children's names on</h1>
    <p class="lead">Type the names, check the preview, then print. Names stay in this browser and are never sent anywhere.</p>
  </header>

  <div class="mk">
    <section class="controls" aria-label="Sheet settings">
      <div class="roles" id="tools" role="group" aria-label="Choose a sheet"></div>
      <label class="field"><span>Names, one per line</span>
        <textarea id="names" rows="8" placeholder="Type one child's name on each line"></textarea>
      </label>
      <div class="row">
        <button class="btn" type="button" id="example">Fill with example names</button>
        <button class="btn" type="button" id="clear">Clear names</button>
      </div>
      <label class="field"><span id="setting-label">Setting or class name (optional)</span>
        <input id="setting" type="text" autocomplete="off" placeholder="e.g. Robins class">
      </label>
      <label class="field" id="rows-field"><span>Traced rows on each sheet</span>
        <select id="rows"><option value="1">1</option><option value="2" selected>2</option><option value="3">3</option></select>
      </label>
      <label class="check" id="small-field"><input id="small" type="checkbox"> <span>Show the setting name under each label</span></label>
      <div class="row">
        <button class="btn primary" type="button" id="print">Print</button>
        <span id="count" role="status" class="muted"></span>
      </div>
      <p class="note" id="framed" hidden>Printing may be blocked inside an app preview. If Print does nothing, open the website in your browser. The sheets look the same.</p>
    </section>

    <section class="stage" aria-label="Preview">
      <p class="muted" id="empty">Add at least one name to see the sheets.</p>
      <div id="sheets"></div>
    </section>
  </div>
"""

MAKE_CSS = """
.mkhead { padding-block: 40px 8px; }
.mkhead h1 { margin-top: 12px; font-size: clamp(2.3rem, 8vw, 4rem); font-weight: 800; letter-spacing: -0.02em; max-width: 16ch; }
.mkhead .lead { margin-top: 16px; max-width: 54ch; font-size: 1.12rem; color: var(--muted); }
.mk { display: grid; grid-template-columns: minmax(0, 1fr); gap: 28px; margin-top: 26px; align-items: start; }
@media (min-width: 900px) { .mk { grid-template-columns: 320px minmax(0, 1fr); } .controls { position: sticky; top: 12px; } }
.controls { display: flex; flex-direction: column; gap: 14px; padding: 18px; border: 2px solid var(--ink); background: var(--surface); }
.roles { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { font: 600 0.98rem/1 var(--body); min-height: 42px; padding: 0 14px; cursor: pointer; border: 2px solid var(--ink); background: transparent; color: var(--ink); }
.chip[aria-pressed="true"] { background: var(--ink); color: var(--bg); }
.field { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.field > span { font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); }
.field input, .field select, .field textarea { padding: 10px 12px; border: 2px solid var(--line); border-radius: 0; background: var(--bg); color: var(--ink); font: 400 1rem var(--body); width: 100%; min-width: 0; }
.field textarea { resize: vertical; min-height: 130px; }
.check { display: flex; gap: 8px; align-items: center; }
.row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
.row .btn { min-height: 40px; padding: 0 14px; font-size: 0.95rem; }
.muted { color: var(--muted); font-size: 0.92rem; }
.note { font-size: 0.88rem; padding: 8px 10px; background: var(--accent-soft); }
.stage { min-width: 0; }
.swrap { margin-bottom: 18px; background: #fff; box-shadow: 0 2px 14px rgba(0, 0, 0, 0.18); overflow: hidden; }
.sheet { width: 210mm; height: 297mm; background: #fff; color: #142330; transform-origin: top left; position: relative; font-family: "Source Sans 3", Arial, sans-serif; overflow: hidden; }
.sheet .s-head { position: absolute; left: 14mm; right: 14mm; top: 10mm; display: flex; justify-content: space-between; font-size: 10pt; color: #4f606c; }
.sheet .s-foot { position: absolute; left: 14mm; right: 14mm; bottom: 8mm; font-size: 8pt; color: #8fa3af; display: flex; justify-content: space-between; }
.trace { position: absolute; left: 14mm; right: 14mm; top: 24mm; }
.trace h3 { font-family: "Source Sans 3", Arial, sans-serif; font-size: 11pt; font-weight: 600; color: #4f606c; margin-bottom: 4mm; }
.trace svg { width: 100%; height: auto; display: block; margin-bottom: 6mm; }
.labels { position: absolute; left: 7mm; top: 13mm; display: grid; grid-template-columns: repeat(3, 63.5mm); grid-auto-rows: 33.9mm; gap: 0 2.5mm; }
.lab { border: 0.3mm dashed #c9d6dd; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 2mm; overflow: hidden; }
.lab .nm { font-family: Andika, "Trebuchet MS", sans-serif; font-weight: 700; white-space: nowrap; color: #142330; line-height: 1.1; }
.lab .st { font-size: 8pt; color: #4f606c; margin-top: 1.5mm; white-space: nowrap; }
.reg { position: absolute; left: 10mm; right: 10mm; top: 20mm; }
.reg table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 10pt; }
.reg th, .reg td { border: 0.3mm solid #8fa3af; height: 9.6mm; padding: 0 1.5mm; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.reg th { background: #00756f; color: #fff; font-weight: 600; height: 8mm; font-size: 9pt; }
.reg th.d { font-size: 8.5pt; }
.reg td.nm { font-weight: 600; }
@page { size: A4; margin: 0; }
@media print {
  html, body { background: #fff !important; padding: 0 !important; }
  .sitenav, .mkhead, .controls, footer, #empty { display: none !important; }
  .wrap { max-width: none; }
  .mk { display: block; margin: 0; }
  .swrap { height: auto !important; width: auto !important; margin: 0; box-shadow: none; overflow: visible; break-after: page; }
  .swrap:last-child { break-after: auto; }
  .sheet { transform: none !important; }
}
"""

MAKE_JS = r"""
const $ = (id) => document.getElementById(id);
const SVGNS = "http://www.w3.org/2000/svg";
const TOOLS = [
  { id: "tracing", label: "Name tracing" },
  { id: "labels", label: "Name labels" },
  { id: "register", label: "Class register" }
];
const EXAMPLE = ["Amelia", "Noah", "Fatima", "Oliver", "Zainab", "Leo", "Isla", "Ravi"];
let tool = "tracing";

/* Remember what was typed, in this browser only */
function load(key, fallback) { try { const v = localStorage.getItem(key); return v === null ? fallback : v; } catch (e) { return fallback; } }
function save(key, value) { try { localStorage.setItem(key, value); } catch (e) {} }
$("names").value = load("ff-make-names", "");
$("setting").value = load("ff-make-setting", "");
try { if (window.self !== window.top) $("framed").hidden = false; } catch (e) { $("framed").hidden = false; }

TOOLS.forEach((t) => {
  const b = document.createElement("button");
  b.type = "button"; b.className = "chip"; b.textContent = t.label; b.dataset.tool = t.id;
  b.addEventListener("click", () => { tool = t.id; render(); });
  $("tools").appendChild(b);
});

function getNames() {
  return $("names").value.split(/\r?\n/).map((s) => s.trim()).filter(Boolean).slice(0, 200);
}
function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; }

/* Shrink an SVG text element until it fits the width */
function fitSvgText(textEl, maxW, startSize) {
  let size = startSize;
  textEl.setAttribute("font-size", size);
  let guard = 0;
  while (textEl.getComputedTextLength() > maxW && size > 20 && guard++ < 60) { size -= 4; textEl.setAttribute("font-size", size); }
  return size;
}

function sheetShell(headLeft, headRight) {
  const wrap = el("div", "swrap");
  const sheet = el("div", "sheet");
  const h = el("div", "s-head"); h.append(el("span", "", headLeft), el("span", "", headRight));
  const f = el("div", "s-foot"); f.append(el("span", "", "Framework Finder"), el("span", "", "Free to print and use in your own setting."));
  sheet.append(h, f); wrap.appendChild(sheet);
  return { wrap, sheet };
}

function svgEl(tag, attrs) {
  const e = document.createElementNS(SVGNS, tag);
  Object.keys(attrs).forEach((k) => e.setAttribute(k, attrs[k]));
  return e;
}

function tracingSheet(name, setting, rowsWanted) {
  const { wrap, sheet } = sheetShell(setting || "Name tracing", "Name:");
  const box = el("div", "trace");
  box.appendChild(el("h3", "", "Trace over the letters, then write your name on the line."));
  const W = 700, H = 170;
  const rows = [];
  for (let i = 0; i < rowsWanted; i++) rows.push(i === 0 ? "model" : "dots");
  rows.push("write");
  rows.forEach((kind) => {
    const svg = svgEl("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": kind === "write" ? "Blank writing line" : "Name " + name });
    const g = svgEl("g", { stroke: "#c9d6dd", "stroke-width": "1.5" });
    g.appendChild(svgEl("line", { x1: 0, y1: 30, x2: W, y2: 30 }));
    g.appendChild(svgEl("line", { x1: 0, y1: 80, x2: W, y2: 80, "stroke-dasharray": "6 5" }));
    g.appendChild(svgEl("line", { x1: 0, y1: 130, x2: W, y2: 130, stroke: "#8fa3af" }));
    svg.appendChild(g);
    if (kind !== "write") {
      const attrs = { x: 6, y: 130, "font-family": "Andika, 'Trebuchet MS', 'Comic Sans MS', sans-serif", "font-weight": "400" };
      if (kind === "model") Object.assign(attrs, { fill: "#142330" });
      else Object.assign(attrs, { fill: "none", stroke: "#142330", "stroke-width": "1.6", "stroke-dasharray": "2 6", "stroke-linecap": "round" });
      const t = svgEl("text", attrs);
      t.textContent = name;
      svg.appendChild(t);
      svg.__text = t;
    }
    box.appendChild(svg);
  });
  sheet.appendChild(box);
  return { wrap, sheet, svgs: box.querySelectorAll("svg") };
}

function renderTracing(names) {
  const out = $("sheets");
  const rows = parseInt($("rows").value, 10);
  const made = names.map((n) => tracingSheet(n, $("setting").value.trim(), rows));
  made.forEach((m) => out.appendChild(m.wrap));
  /* fit after they are in the page, so text can be measured */
  made.forEach((m) => {
    let size = null;
    m.sheet.querySelectorAll("svg text").forEach((t) => {
      if (size === null) size = fitSvgText(t, 680, 118); else t.setAttribute("font-size", size);
    });
  });
}

function renderLabels(names) {
  const out = $("sheets");
  const per = 24;
  const showSetting = $("small").checked;
  const setting = $("setting").value.trim();
  for (let p = 0; p < names.length; p += per) {
    const { wrap, sheet } = sheetShell("", "");
    sheet.querySelector(".s-head").remove();
    const grid = el("div", "labels");
    names.slice(p, p + per).forEach((n) => {
      const lab = el("div", "lab");
      const nm = el("div", "nm", n); nm.style.fontSize = "26pt";
      lab.appendChild(nm);
      if (showSetting && setting) lab.appendChild(el("div", "st", setting));
      grid.appendChild(lab);
    });
    sheet.appendChild(grid);
    out.appendChild(wrap);
    grid.querySelectorAll(".nm").forEach((nm) => {
      let size = 26, guard = 0;
      while (nm.scrollWidth > 53 * 3.7795 && size > 9 && guard++ < 40) { size -= 1; nm.style.fontSize = size + "pt"; }
    });
  }
}

function renderRegister(names) {
  const out = $("sheets");
  const per = 24;
  const pages = Math.max(1, Math.ceil(names.length / per));
  for (let p = 0; p < pages; p++) {
    const { wrap, sheet } = sheetShell($("setting").value.trim() || "Register", "Week beginning:");
    const box = el("div", "reg");
    const table = el("table");
    const thead = el("thead");
    const tr1 = el("tr"), tr2 = el("tr");
    const nameTh = el("th", "", "Name"); nameTh.rowSpan = 2; nameTh.style.width = "46mm"; tr1.appendChild(nameTh);
    ["Mon", "Tue", "Wed", "Thu", "Fri"].forEach((d) => { const th = el("th", "d", d); th.colSpan = 2; tr1.appendChild(th); });
    for (let i = 0; i < 5; i++) { tr2.appendChild(el("th", "d", "AM")); tr2.appendChild(el("th", "d", "PM")); }
    thead.append(tr1, tr2);
    const tbody = el("tbody");
    for (let r = 0; r < per; r++) {
      const tr = el("tr");
      const nm = names[p * per + r];
      tr.appendChild(el("td", "nm", nm || ""));
      for (let c = 0; c < 10; c++) tr.appendChild(el("td", ""));
      tbody.appendChild(tr);
    }
    table.append(thead, tbody); box.appendChild(table); sheet.appendChild(box);
    out.appendChild(wrap);
  }
}

/* Scale the A4 preview to the width of the page; printing ignores this */
function scaleSheets() {
  const stage = $("sheets");
  const avail = stage.clientWidth;
  const full = 210 * 3.7795;
  const s = Math.min(1, avail / full);
  stage.querySelectorAll(".swrap").forEach((w) => {
    const sheet = w.firstChild;
    sheet.style.transform = "scale(" + s + ")";
    w.style.width = (full * s) + "px";
    w.style.height = (297 * 3.7795 * s) + "px";
  });
}

function render() {
  document.querySelectorAll("#tools .chip").forEach((b) => b.setAttribute("aria-pressed", b.dataset.tool === tool ? "true" : "false"));
  $("rows-field").hidden = tool !== "tracing";
  $("small-field").hidden = tool !== "labels";
  $("setting-label").textContent = tool === "register" ? "Setting or class name (shown at the top)" : "Setting or class name (optional)";
  const names = getNames();
  $("sheets").textContent = "";
  $("empty").hidden = names.length > 0;
  $("print").disabled = names.length === 0;
  if (names.length) {
    if (tool === "tracing") renderTracing(names);
    else if (tool === "labels") renderLabels(names);
    else renderRegister(names);
  }
  const n = $("sheets").querySelectorAll(".swrap").length;
  $("count").textContent = names.length ? names.length + (names.length === 1 ? " name, " : " names, ") + n + (n === 1 ? " page" : " pages") : "";
  scaleSheets();
}

$("names").addEventListener("input", () => { save("ff-make-names", $("names").value); render(); });
$("setting").addEventListener("input", () => { save("ff-make-setting", $("setting").value); render(); });
["rows", "small"].forEach((id) => $(id).addEventListener("change", render));
$("example").addEventListener("click", () => { $("names").value = EXAMPLE.join("\n"); save("ff-make-names", $("names").value); render(); });
$("clear").addEventListener("click", () => { $("names").value = ""; save("ff-make-names", ""); render(); });
$("print").addEventListener("click", () => { try { window.print(); } catch (e) {} });
window.addEventListener("resize", scaleSheets);
if (document.fonts && document.fonts.ready) document.fonts.ready.then(render);
render();
"""


def build_make():
    return page("Make Your Own Sheets", MAKE_BODY, MAKE_CSS, MAKE_JS, "make.html", "")


def wrap_fragment_as_document(fragment, title_override=None):
    """Turn an old fragment-style page (title/style first, no <html>) into a full document."""
    idx = fragment.rfind("</style>")
    head, body = fragment[: idx + len("</style>")], fragment[idx + len("</style>"):]
    head = head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    return ('<!doctype html>\n<html lang="en-GB">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + "\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")


def retarget_nav(html, current):
    html = re.sub(r'<nav class="sitenav".*?</nav>', nav(current), html, flags=re.S)
    if ".wordmark" not in html:
        html = html.replace("</style>", NAV_CSS + "</style>", 1)
    return html


def main():
    os.makedirs(SITE, exist_ok=True)
    # frameworks.html: wrap old fragment as a document if needed, update nav
    fw_path = os.path.join(SITE, "frameworks.html")
    fw = open(fw_path, encoding="utf-8").read()
    if not fw.lstrip().lower().startswith("<!doctype"):
        fw = wrap_fragment_as_document(fw)
    fw = retarget_nav(fw, "frameworks.html")
    open(fw_path, "w", encoding="utf-8").write(fw)
    # printables.html: only the nav changes here
    pr_path = os.path.join(SITE, "printables.html")
    pr = open(pr_path, encoding="utf-8").read()
    pr = retarget_nav(pr, "printables.html")
    open(pr_path, "w", encoding="utf-8").write(pr)
    for name, html in (("index.html", build_home()), ("early-years.html", build_hub()), ("make.html", build_make())):
        open(os.path.join(SITE, name), "w", encoding="utf-8").write(html)
    print("Built pages in", SITE)


if __name__ == "__main__":
    main()
