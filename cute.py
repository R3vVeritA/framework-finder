#!/usr/bin/env python3
"""Gives every page a cute early-years look. Run AFTER build_site.py:  python3 cute.py SITE_DIR
It is safe to run twice."""
import re, sys, os
SITE = sys.argv[1] if len(sys.argv) > 1 else "site-final"
MARK = "/* cute-early-years */"
FONT = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Andika:wght@400;700'
        '&family=Fredoka:wght@500;600;700&family=Nunito:wght@400;600;700;800&display=swap">')
CSS = MARK + """
:root {
  --bg: #fff8ec; --surface: #ffffff; --ink: #2b2a4c; --muted: #6a6788; --line: #f0e2c8;
  --accent: #e8590c; --accent-soft: #ffe9d6; --mark: #ffd84d; --focus: #3b5bdb;
  --display: "Fredoka", "Nunito", "Trebuchet MS", system-ui, sans-serif;
  --body: "Nunito", "Trebuchet MS", system-ui, sans-serif;
  --a-communication: #3b82e0; --a-personal-social: #e0457b; --a-physical: #f08a24; --a-literacy: #8b5cf6;
  --a-mathematics: #14a8b8; --a-understanding-world: #3aa655; --a-expressive-arts: #e0a812;
  --pop: 4px 4px 0 var(--ink);
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #211f3d; --surface: #2d2a52; --ink: #fff3de; --muted: #c5c0e6; --line: #433f75; --accent: #ff9a5c; --accent-soft: #4a3560; --focus: #8fb0ff; --pop: 4px 4px 0 #0f0e22; } }
:root[data-theme="dark"] { --bg: #211f3d; --surface: #2d2a52; --ink: #fff3de; --muted: #c5c0e6; --line: #433f75; --accent: #ff9a5c; --accent-soft: #4a3560; --focus: #8fb0ff; --pop: 4px 4px 0 #0f0e22; }
body { font-family: var(--body); font-weight: 600; background-image: radial-gradient(circle at 12px 12px, rgba(232,89,12,.07) 3px, transparent 4px); background-size: 48px 48px; }
h1, h2, h3, .rl-t, .tile .t-name, .wordmark { font-family: var(--display) !important; letter-spacing: 0 !important; font-weight: 600 !important; }
h1 { font-weight: 700 !important; }
.eyebrow, .grouplabel, .field > span, .a-kind { font-family: var(--display); letter-spacing: .06em; }
.eyebrow { display: inline-block; padding: 4px 14px; border-radius: 999px; background: var(--accent-soft); }
/* rainbow ribbon at the very top */
body::before { content: ""; display: block; height: 10px; margin-inline: calc(-1 * max(16px, env(safe-area-inset-left, 0px))); margin-bottom: 0;
  background: linear-gradient(90deg, var(--a-communication) 0 14.28%, var(--a-personal-social) 0 28.56%, var(--a-physical) 0 42.84%, var(--a-literacy) 0 57.12%, var(--a-mathematics) 0 71.4%, var(--a-understanding-world) 0 85.68%, var(--a-expressive-arts) 0); }
.sitenav a { border: 2px solid var(--ink) !important; border-radius: 999px; background: var(--surface); box-shadow: 2px 2px 0 var(--ink); transition: transform .12s; }
.sitenav a:hover { transform: translateY(-2px) rotate(-1.5deg); }
.sitenav a[aria-current="page"] { background: var(--accent) !important; color: #fff !important; border-color: var(--ink) !important; }
.sitenav a.wordmark { border: 0 !important; box-shadow: none; background: none; font-size: 1.55rem; color: var(--accent); }
.sitenav a.wordmark::before { content: "\\2605 "; color: var(--mark); -webkit-text-stroke: 1.5px var(--ink); }
.btn, .chip, .vbar button, .item .prev, .item .open, .linkbtn { border-radius: 999px !important; border: 2px solid var(--ink) !important; box-shadow: 3px 3px 0 var(--ink); font-family: var(--display); font-weight: 600 !important; transition: transform .12s, box-shadow .12s; }
.btn:hover, .chip:hover { transform: translate(-1px,-2px); box-shadow: 4px 5px 0 var(--ink); filter: none; }
.btn:active, .chip:active { transform: translate(2px,2px); box-shadow: 1px 1px 0 var(--ink); }
.btn.primary { background: var(--accent); color: #fff; }
.chip[aria-pressed="true"] { background: var(--a-communication) !important; color: #fff !important; }
.tile, .area { border-radius: 26px !important; border: 3px solid var(--ink); box-shadow: var(--pop); transition: transform .15s; }
.tile:hover, .area:hover { transform: translateY(-4px) rotate(-1deg); filter: none; }
.tiles .tile:nth-child(even):hover { transform: translateY(-4px) rotate(1deg); }
.tile .t-n { background: rgba(255,255,255,.25); align-self: flex-start; padding: 2px 12px; border-radius: 999px; }
.tile[href*="frameworks"], .tile[href$="teacher"], .tile[href$="student"] { background: var(--a-mathematics); }
.tile[href$="student"] { background: var(--a-literacy); } .tile[href*="frameworks"] { background: var(--a-understanding-world); }
.rule-list { border-top: 0 !important; display: grid; gap: 12px; }
.rule-list li { border: 3px solid var(--ink) !important; border-radius: 22px; background: var(--surface); box-shadow: 3px 3px 0 var(--ink); overflow: hidden; }
.rule-list a { padding: 14px 20px; } .rule-list li:hover { transform: translateY(-2px); }
.rl-n { background: var(--accent-soft); border-radius: 999px; padding: 4px 14px; color: var(--accent); }
.hero h1 span, .mast h1 span, .mkhead h1 { background-size: 100% 100%; }
.hero h1 span { background: linear-gradient(transparent 58%, var(--mark) 58%, var(--mark) 92%, transparent 92%); border-radius: 10px; }
.controls { border: 3px solid var(--ink) !important; border-radius: 26px; background: var(--surface); padding: 18px !important; box-shadow: var(--pop); }
.field input, .field select, .field textarea { border: 2px solid var(--ink) !important; border-radius: 16px !important; background: var(--bg) !important; font-family: var(--body); font-weight: 600; }
.item { border: 3px solid var(--ink) !important; border-radius: 22px; background: var(--surface); padding: 16px 20px !important; margin-bottom: 12px; box-shadow: 3px 3px 0 var(--ink); }
.index { padding-left: 0 !important; list-style: none; } .group-head { border: 0 !important; color: var(--accent); }
.tag { border-radius: 999px !important; border: 2px solid var(--line) !important; background: var(--bg); padding: 3px 12px !important; }
.tag.new { background: var(--mark) !important; border-color: var(--ink) !important; color: #2b2a4c !important; }
.tag.area { background: var(--accent-soft) !important; border-color: var(--accent-soft) !important; color: var(--accent); }
.note { border-radius: 18px; border: 2px dashed var(--accent); background: var(--accent-soft); }
.swrap { border-radius: 8px; }
footer { border-top: 3px dashed var(--accent) !important; font-weight: 600; }
.viewer { background: #1d1b3a !important; }
a { text-decoration-thickness: 2px; text-underline-offset: 3px; }
/* hero decorations */
.hero { position: relative; }
.hero .deco { position: absolute; right: 0; top: 24px; width: min(300px, 38vw); height: auto; pointer-events: none; }
@media (max-width: 640px) { .hero .deco { width: 120px; top: 10px; opacity: .9; } }
.feature .f-art { border-radius: 22px; box-shadow: var(--pop); border: 3px solid var(--ink); }
@media (prefers-reduced-motion: no-preference) { .hero .deco .bob { animation: bob 3.2s ease-in-out infinite; transform-box: fill-box; transform-origin: center; } .hero .deco .bob2 { animation-delay: -1.2s; } }
@keyframes bob { 50% { transform: translateY(-8px) rotate(6deg); } }
"""
DECO = """<svg class="deco" viewBox="0 0 300 260" aria-hidden="true">
  <g class="bob"><path d="M70 20l14 30 33 4-25 22 7 33-29-17-29 17 7-33-25-22 33-4z" fill="#ffd84d" stroke="#2b2a4c" stroke-width="5" stroke-linejoin="round"/></g>
  <g class="bob bob2"><circle cx="218" cy="62" r="40" fill="#e0457b" stroke="#2b2a4c" stroke-width="5"/><circle cx="205" cy="55" r="5" fill="#2b2a4c"/><circle cx="232" cy="55" r="5" fill="#2b2a4c"/><path d="M203 72q15 14 30 0" fill="none" stroke="#2b2a4c" stroke-width="5" stroke-linecap="round"/><circle cx="196" cy="68" r="6" fill="#ff9db8"/><circle cx="240" cy="68" r="6" fill="#ff9db8"/></g>
  <g class="bob"><rect x="40" y="130" width="88" height="88" rx="16" fill="#3b82e0" stroke="#2b2a4c" stroke-width="5"/><text x="84" y="195" text-anchor="middle" font-family="Fredoka, Nunito, sans-serif" font-size="64" font-weight="700" fill="#fff">A</text></g>
  <g class="bob bob2"><rect x="150" y="150" width="88" height="88" rx="16" fill="#3aa655" stroke="#2b2a4c" stroke-width="5" transform="rotate(8 194 194)"/><text x="194" y="214" text-anchor="middle" font-family="Fredoka, Nunito, sans-serif" font-size="64" font-weight="700" fill="#fff" transform="rotate(8 194 194)">1</text></g>
</svg>"""
for name in ["index.html", "early-years.html", "printables.html", "make.html", "frameworks.html"]:
    p = os.path.join(SITE, name)
    s = open(p, encoding="utf-8").read()
    if MARK in s:
        continue
    s = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>', FONT, s, count=1)
    s = s.replace("</style>", CSS + "</style>", 1)
    if name == "index.html":
        s = s.replace('<header class="hero">', '<header class="hero">\n    ' + DECO, 1)
    open(p, "w", encoding="utf-8").write(s)
print("cute applied")
