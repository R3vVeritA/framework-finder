#!/usr/bin/env python3
"""Framework Finder printable library generator.

Usage: python3 generate.py OUTPUT_DIR
Creates OUTPUT_DIR/resources/<category>/<nnn-title>.pdf (200 files) and OUTPUT_DIR/resources.json.
All content is original. Edit BRAND / FOOT below to rebrand every sheet, then run again.
"""
import calendar
import json
import math
import os
import re
import sys

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
BRAND = "Framework Finder"
FOOT = "Free to print and use in your own setting. Not for resale."

TEAL = HexColor("#00756f")
INK = HexColor("#142330")
SOFT = HexColor("#e3f3f1")
LINE = HexColor("#8fa3af")
PALE = HexColor("#c9d6dd")
MARK = HexColor("#ffd84d")
FAINT = HexColor("#eef3f5")
M = 34
FOOT_H = 40

AREAS = [
    "Communication and Language",
    "Personal, Social and Emotional Development",
    "Physical Development",
    "Literacy",
    "Mathematics",
    "Understanding the World",
    "Expressive Arts and Design",
]
STANDARDS = [
    "1. Set high expectations which inspire, motivate and challenge pupils",
    "2. Promote good progress and outcomes by pupils",
    "3. Demonstrate good subject and curriculum knowledge",
    "4. Plan and teach well structured lessons",
    "5. Adapt teaching to respond to the strengths and needs of all pupils",
    "6. Make accurate and productive use of assessment",
    "7. Manage behaviour effectively to ensure a good and safe learning environment",
    "8. Fulfil wider professional responsibilities",
]
COLOURS = {
    "Red": "#e03131", "Blue": "#1c6ed5", "Yellow": "#f7c52a", "Green": "#2f9e44",
    "Orange": "#f08c00", "Purple": "#7048e8", "Pink": "#f06595", "Brown": "#8d5a3b",
    "Black": "#1b1b1b", "White": "#ffffff",
}


# ---------------------------------------------------------------- helpers
def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def fit(c, text, font, size, maxw, minsize=6):
    while size > minsize and c.stringWidth(text, font, size) > maxw:
        size -= 0.5
    return size


def wrap(c, text, font, size, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Doc:
    def __init__(self, path, title, sub="", land=False):
        self.size = landscape(A4) if land else A4
        self.W, self.H = self.size
        self.c = canvas.Canvas(path, pagesize=self.size)
        self.c.setTitle(title)
        self.c.setAuthor(BRAND)
        self.title, self.sub = title, sub
        self.page_no = 1
        self.y = self.start()

    def start(self):
        c, W, H = self.c, self.W, self.H
        c.setFillColor(TEAL)
        c.rect(0, H - 58, W, 58, stroke=0, fill=1)
        c.setFillColor(MARK)
        c.rect(0, H - 62, W, 4, stroke=0, fill=1)
        c.setFillColor(white)
        f = fit(c, self.title, "Helvetica-Bold", 22, W - 2 * M)
        c.setFont("Helvetica-Bold", f)
        c.drawString(M, H - (30 if self.sub else 36), self.title)
        if self.sub:
            c.setFont("Helvetica", 9.5)
            s = fit(c, self.sub, "Helvetica", 9.5, W - 2 * M)
            c.setFont("Helvetica", s)
            c.drawString(M, H - 47, self.sub)
        # footer
        c.setStrokeColor(PALE)
        c.setLineWidth(0.6)
        c.line(M, 30, W - M, 30)
        c.setFillColor(LINE)
        c.setFont("Helvetica", 7.5)
        c.drawString(M, 19, FOOT)
        c.drawRightString(W - M, 19, BRAND)
        return H - 62 - 16

    def new_page(self):
        self.c.showPage()
        self.page_no += 1
        self.y = self.start()

    def need(self, h):
        if self.y - h < FOOT_H:
            self.new_page()

    def save(self):
        self.c.save()


def text_in(c, text, x, y_top, w, h, font="Helvetica", size=9, color=INK, align="left", lead=1.2):
    c.setFillColor(color)
    lines = wrap(c, text, font, size, w)
    while len(lines) * size * lead > h and size > 5.5:
        size -= 0.5
        lines = wrap(c, text, font, size, w)
    th = len(lines) * size * lead
    yy = y_top - (h - th) / 2 - size * 0.85
    c.setFont(font, size)
    for ln in lines:
        if align == "center":
            c.drawCentredString(x + w / 2, yy, ln)
        else:
            c.drawString(x, yy, ln)
        yy -= size * lead


def fields(d, labels, gap=14):
    c, n = d.c, len(labels)
    tw = d.W - 2 * M
    w = (tw - gap * (n - 1)) / n
    y = d.y - 8
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    for i, lab in enumerate(labels):
        x = M + i * (w + gap)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(x, y, lab)
        lw = c.stringWidth(lab, "Helvetica-Bold", 8.5)
        c.line(x + lw + 4, y - 2, x + w, y - 2)
    d.y = y - 18


def box(d, x, ytop, w, h, label=None, ruled=0, fill=None):
    c = d.c
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    if fill:
        c.setFillColor(fill)
        c.roundRect(x, ytop - h, w, h, 4, stroke=1, fill=1)
    else:
        c.roundRect(x, ytop - h, w, h, 4, stroke=1, fill=0)
    if label:
        c.setFillColor(TEAL)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(x + 7, ytop - 13, label)
    if ruled:
        gap = 22 if ruled is True else ruled
        yy = ytop - (36 if label else 20)
        c.setStrokeColor(PALE)
        c.setLineWidth(0.6)
        while yy > ytop - h + 8:
            c.line(x + 7, yy, x + w - 7, yy)
            yy -= gap


def checkbox_list(d, x, ytop, w, items, size=9, gap=17, cols=1):
    c = d.c
    colw = w / cols
    per = math.ceil(len(items) / cols)
    for i, it in enumerate(items):
        cc, rr = divmod(i, per)
        xx = x + cc * colw
        yy = ytop - rr * gap
        c.setStrokeColor(LINE)
        c.setLineWidth(0.9)
        c.rect(xx, yy - 8, 8, 8, stroke=1, fill=0)
        c.setFillColor(INK)
        c.setFont("Helvetica", size)
        s = fit(c, it, "Helvetica", size, colw - 16)
        c.setFont("Helvetica", s)
        c.drawString(xx + 13, yy - 7, it)


def sections(d, secs, gap=8):
    c = d.c
    tw = d.W - 2 * M
    for sec in secs:
        row = sec if isinstance(sec, list) else [sec]
        hs = [(s[1] if not isinstance(s, str) else 120) for s in row]
        h = max([x for x in hs if x != "fill"] or [0])
        if any(x == "fill" for x in hs):
            h = max(h, d.y - FOOT_H - 4)
        else:
            d.need(h)
        n = len(row)
        w = (tw - gap * (n - 1)) / n
        for i, s in enumerate(row):
            x = M + i * (w + gap)
            if isinstance(s, str):  # special
                if s == "@areas":
                    box(d, x, d.y, w, h, "Areas of learning (tick all that apply)")
                    checkbox_list(d, x + 8, d.y - 30, w - 16, AREAS, size=9, gap=17, cols=2 if w > 400 else 1)
                continue
            label, _h, rule = (s + (False,))[:3] if len(s) == 2 else s
            box(d, x, d.y, w, h, label, rule)
        d.y -= h + gap


def draw_arrow(c, x1, y1, x2, y2, size=6):
    c.line(x1, y1, x2, y2)
    ang = math.atan2(y2 - y1, x2 - x1)
    for a in (ang + 2.6, ang - 2.6):
        c.line(x2, y2, x2 + size * math.cos(a), y2 + size * math.sin(a))


def star(c, cx, cy, r, fill=False):
    pts = []
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    p = c.beginPath()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    c.drawPath(p, stroke=1, fill=1 if fill else 0)


# ---------------------------------------------------------------- kinds
def k_form(d, p):
    if p.get("fields"):
        fields(d, p["fields"])
    sections(d, p.get("sections", []))
    if p.get("note"):
        d.c.setFillColor(LINE)
        d.c.setFont("Helvetica-Oblique", 7.5)
        d.c.drawString(M, FOOT_H - 2 + 4, p["note"])


def k_table(d, p):
    c = d.c
    if p.get("fields"):
        fields(d, p["fields"])
    header = p["header"]
    rel = p.get("widths") or [1] * len(header)
    tw = d.W - 2 * M
    widths = [tw * r / sum(rel) for r in rel]
    rh, hh = p.get("row_h", 28), p.get("head_h", 26)
    rows = p.get("rows")
    if not isinstance(rows, list):
        per = int((d.y - FOOT_H - hh - 4) // rh)
        n = rows if isinstance(rows, int) else per
        rows = [[""] * len(header) for _ in range(min(n, per))]
    i = 0
    while i < len(rows):
        per = max(1, int((d.y - FOOT_H - hh - 4) // rh))
        chunk = rows[i:i + per]
        x = M
        for j, hd in enumerate(header):
            c.setFillColor(TEAL)
            c.setStrokeColor(white)
            c.rect(x, d.y - hh, widths[j], hh, stroke=1, fill=1)
            text_in(c, hd, x + 3, d.y, widths[j] - 6, hh, "Helvetica-Bold", 8.5, white, "center")
            x += widths[j]
        y = d.y - hh
        for r_i, row in enumerate(chunk):
            x = M
            for j in range(len(header)):
                cell = row[j] if j < len(row) else ""
                c.setStrokeColor(LINE)
                c.setLineWidth(0.7)
                if p.get("shade_first") and j == 0:
                    c.setFillColor(SOFT)
                    c.rect(x, y - rh, widths[j], rh, stroke=1, fill=1)
                else:
                    c.rect(x, y - rh, widths[j], rh, stroke=1, fill=0)
                if cell:
                    text_in(c, cell, x + 4, y, widths[j] - 8, rh, "Helvetica-Bold" if j == 0 else "Helvetica", 8.5, INK)
                x += widths[j]
            y -= rh
        d.y = y - 8
        i += per
        if i < len(rows):
            d.new_page()


def k_checklist(d, p):
    if p.get("fields"):
        fields(d, p["fields"])
    items = p["items"]
    c = d.c
    cols = p.get("cols", 1)
    gap = p.get("gap", 24)
    per = math.ceil(len(items) / cols)
    checkbox_list(d, M + 4, d.y - 4, d.W - 2 * M - 8, items, size=p.get("size", 10.5), gap=gap, cols=cols)
    d.y -= per * gap + 14
    if p.get("notes", True):
        h = d.y - FOOT_H - 4
        if h > 50:
            box(d, M, d.y, d.W - 2 * M, h, "Notes", True)


def face(c, cx, cy, r, mood):
    c.setStrokeColor(INK)
    c.setLineWidth(2)
    c.setFillColor(HexColor("#fff3b0"))
    c.circle(cx, cy, r, stroke=1, fill=1)
    c.setFillColor(INK)
    ex = r * 0.38
    ey = cy + r * 0.2
    if mood in ("tired", "calm"):
        c.setLineWidth(2)
        for s in (-1, 1):
            c.arc(cx + s * ex - r * 0.18, ey - r * 0.12, cx + s * ex + r * 0.18, ey + r * 0.12, 190, 160)
    elif mood == "surprised":
        for s in (-1, 1):
            c.circle(cx + s * ex, ey, r * 0.12, stroke=1, fill=0)
    elif mood == "scared":
        for s in (-1, 1):
            c.circle(cx + s * ex, ey, r * 0.14, stroke=1, fill=0)
            c.circle(cx + s * ex, ey, r * 0.04, stroke=0, fill=1)
    else:
        for s in (-1, 1):
            c.circle(cx + s * ex, ey, r * 0.09, stroke=0, fill=1)
    c.setLineWidth(2)
    c.setFillColor(INK)
    if mood == "happy":
        c.arc(cx - r * 0.5, cy - r * 0.6, cx + r * 0.5, cy + r * 0.1, 200, 140)
    elif mood == "excited":
        p = c.beginPath()
        p.moveTo(cx - r * 0.5, cy - r * 0.18)
        p.curveTo(cx - r * 0.4, cy - r * 0.8, cx + r * 0.4, cy - r * 0.8, cx + r * 0.5, cy - r * 0.18)
        p.close()
        c.drawPath(p, stroke=1, fill=1)
    elif mood in ("sad", "angry"):
        c.arc(cx - r * 0.4, cy - r * 0.8, cx + r * 0.4, cy - r * 0.25, 30, 120)
        if mood == "angry":
            c.line(cx - ex - r * 0.2, ey + r * 0.3, cx - ex + r * 0.2, ey + r * 0.15)
            c.line(cx + ex + r * 0.2, ey + r * 0.3, cx + ex - r * 0.2, ey + r * 0.15)
    elif mood == "surprised":
        c.ellipse(cx - r * 0.12, cy - r * 0.55, cx + r * 0.12, cy - r * 0.2, stroke=1, fill=0)
    elif mood == "scared":
        c.line(cx - r * 0.3, cy - r * 0.4, cx - r * 0.1, cy - r * 0.32)
        c.line(cx - r * 0.1, cy - r * 0.32, cx + r * 0.1, cy - r * 0.42)
        c.line(cx + r * 0.1, cy - r * 0.42, cx + r * 0.3, cy - r * 0.34)
    elif mood == "tired":
        c.line(cx - r * 0.25, cy - r * 0.4, cx + r * 0.25, cy - r * 0.4)
    elif mood == "calm":
        c.arc(cx - r * 0.35, cy - r * 0.5, cx + r * 0.35, cy - r * 0.15, 200, 140)


def k_cards(d, p):
    c = d.c
    items, cols, rows = p["items"], p["cols"], p["rows"]
    style = p.get("style", "text")
    per = cols * rows
    for i, it in enumerate(items):
        if i > 0 and i % per == 0:
            d.new_page()
        k = i % per
        r, cc = divmod(k, cols)
        top = d.y
        cw = (d.W - 2 * M) / cols
        ch = (top - FOOT_H - 4) / rows
        x, y = M + cc * cw, top - (r + 1) * ch
        c.setDash(3, 3)
        c.setStrokeColor(PALE)
        c.setLineWidth(0.8)
        c.rect(x + 2, y + 2, cw - 4, ch - 4, stroke=1, fill=0)
        c.setDash()
        if style == "text":
            size = fit(c, it, "Helvetica-Bold", p.get("size", 90), cw - 24, 10)
            c.setFillColor(TEAL)
            c.setFont("Helvetica-Bold", size)
            c.drawCentredString(x + cw / 2, y + ch / 2 - size * 0.35, it)
        elif style == "colour":
            c.setFillColor(HexColor(COLOURS.get(it, "#cccccc")))
            c.setStrokeColor(INK)
            c.setLineWidth(1.5)
            c.roundRect(x + 14, y + 40, cw - 28, ch - 60, 10, stroke=1, fill=1)
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 20)
            c.drawCentredString(x + cw / 2, y + 16, it)
        elif style == "face":
            r0 = min(cw, ch) * 0.3
            face(c, x + cw / 2, y + ch / 2 + 12, r0, it.lower())
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(x + cw / 2, y + 16, it)
        elif style == "sign":
            c.setStrokeColor(TEAL)
            c.setLineWidth(2)
            c.roundRect(x + 8, y + 8, cw - 16, ch - 16, 8, stroke=1, fill=0)
            text_in(c, it, x + 18, y + ch - 10, cw - 36, ch - 20, "Helvetica-Bold", p.get("size", 22), INK, "center")
        elif style == "slip":
            c.setFillColor(TEAL)
            c.setFont("Helvetica-Bold", 13)
            c.drawString(x + 14, y + ch - 24, p.get("slip_title", "WOW moment"))
            c.setFont("Helvetica", 8.5)
            c.setFillColor(INK)
            labs = p.get("slip_labels", ["Child", "Date"])
            yy = y + ch - 44
            half = (cw - 28) / 2
            c.setStrokeColor(LINE)
            c.setLineWidth(0.7)
            for j, lab in enumerate(labs):
                xx = x + 14 + j * (half + 6)
                c.drawString(xx, yy, lab)
                c.line(xx + c.stringWidth(lab, "Helvetica", 8.5) + 3, yy - 2, xx + half - 4, yy - 2)
            yy -= 22
            while yy > y + 14:
                c.line(x + 14, yy, x + cw - 14, yy)
                yy -= 20
        elif style == "ticket":
            c.setFillColor(TEAL)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x + 14, y + ch - 24, "Exit ticket")
            c.setFont("Helvetica", 8.5)
            c.setFillColor(INK)
            c.drawString(x + 14, y + ch - 40, "Name:")
            c.setStrokeColor(LINE)
            c.line(x + 44, y + ch - 42, x + cw - 14, y + ch - 42)
            yy = y + ch - 62
            for q in p.get("prompts", ["Today I learned", "I am still unsure about", "Rate your confidence 1 to 5"]):
                c.drawString(x + 14, yy, q)
                yy -= 18
                c.line(x + 14, yy, x + cw - 14, yy)
                yy -= 14
        elif style == "label":
            c.setStrokeColor(LINE)
            c.setLineWidth(0.8)
            c.roundRect(x + 8, y + 8, cw - 16, ch - 16, 6, stroke=1, fill=0)
            if it:
                size = fit(c, it, "Helvetica-Bold", p.get("size", 18), cw - 30, 8)
                c.setFillColor(INK)
                c.setFont("Helvetica-Bold", size)
                c.drawCentredString(x + cw / 2, y + ch / 2 - size * 0.3, it)
        elif style == "dots":
            n = int(it)
            layouts = {
                1: [(.5, .5)], 2: [(.3, .3), (.7, .7)], 3: [(.25, .25), (.5, .5), (.75, .75)],
                4: [(.3, .3), (.7, .3), (.3, .7), (.7, .7)], 5: [(.3, .3), (.7, .3), (.5, .5), (.3, .7), (.7, .7)],
                6: [(.3, .22), (.3, .5), (.3, .78), (.7, .22), (.7, .5), (.7, .78)],
                7: [(.3, .22), (.3, .5), (.3, .78), (.7, .22), (.7, .5), (.7, .78), (.5, .5)],
                8: [(.3, .17), (.3, .39), (.3, .61), (.3, .83), (.7, .17), (.7, .39), (.7, .61), (.7, .83)],
                9: [(a, b) for a in (.25, .5, .75) for b in (.25, .5, .75)],
                10: [(a, b) for a in (.15, .325, .5, .675, .85) for b in (.33, .67)],
            }
            bw, bh = cw - 40, ch - 40
            c.setStrokeColor(INK)
            c.setLineWidth(2)
            c.setFillColor(white)
            c.roundRect(x + 20, y + 20, bw, bh, 14, stroke=1, fill=1)
            r_dot = min(bw, bh) * (0.07 if n <= 6 else 0.055)
            c.setFillColor(TEAL)
            for fx, fy in layouts[n]:
                c.circle(x + 20 + bw * fx, y + 20 + bh * fy, r_dot, stroke=0, fill=1)
        elif style == "bookmark":
            c.setFillColor(SOFT)
            c.rect(x + 20, y + 10, cw - 40, ch - 20, stroke=0, fill=1)
            c.setFillColor(TEAL)
            tsz = fit(c, "My bookmark", "Helvetica-Bold", 14, cw - 70, 8)
            c.setFont("Helvetica-Bold", tsz)
            c.drawCentredString(x + cw / 2, y + ch - 36, "My bookmark")
            c.setFillColor(INK)
            c.setFont("Helvetica", 9)
            yy = y + ch - 62
            for ln in it.split("|"):
                c.drawString(x + 28, yy, ln)
                yy -= 20
                c.setStrokeColor(LINE)
                c.setLineWidth(0.6)
                c.line(x + 28, yy + 14, x + cw - 28, yy + 14)
                yy -= 8
    d.y = FOOT_H


def k_certificate(d, p):
    c, W, H = d.c, d.W, d.H
    # redraw as a full-page certificate (cover the generic header)
    c.setFillColor(white)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setStrokeColor(TEAL)
    c.setLineWidth(6)
    c.rect(18, 18, W - 36, H - 36, stroke=1, fill=0)
    c.setStrokeColor(MARK)
    c.setLineWidth(2)
    c.rect(30, 30, W - 60, H - 60, stroke=1, fill=0)
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(W / 2, H - 100, p.get("heading", "Certificate of Achievement"))
    c.setFillColor(INK)
    c.setFont("Helvetica", 15)
    c.drawCentredString(W / 2, H - 150, "This certificate is proudly presented to")
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.line(W / 2 - 220, H - 205, W / 2 + 220, H - 205)
    c.setFont("Helvetica", 15)
    c.drawCentredString(W / 2, H - 250, p.get("line", "for being a star."))
    c.line(W / 2 - 250, H - 290, W / 2 + 250, H - 290)
    c.line(W / 2 - 250, H - 330, W / 2 + 250, H - 330)
    star(c, W / 2, 110, 26, fill=False)
    c.setFillColor(MARK)
    star(c, W / 2, 110, 26, fill=True)
    c.setFillColor(INK)
    c.setFont("Helvetica", 11)
    c.drawString(80, 90, "Signed")
    c.line(120, 88, 300, 88)
    c.drawString(W - 300, 90, "Date")
    c.line(W - 270, 88, W - 80, 88)
    c.setFillColor(LINE)
    c.setFont("Helvetica", 7.5)
    c.drawString(60, 44, FOOT)
    c.drawRightString(W - 60, 44, BRAND)


def k_reward(d, p):
    c = d.c
    fields(d, p.get("fields", ["Name", "Goal"]))
    cols, rows = p["cols"], p["rows"]
    labels = p.get("row_labels")
    top = d.y - 6
    lw = 70 if labels else 0
    cw = (d.W - 2 * M - lw) / cols
    ch = min((top - FOOT_H - 10) / rows, cw * 1.1, 110)
    c.setStrokeColor(INK)
    c.setLineWidth(1.4)
    for r in range(rows):
        if labels:
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(M + 2, top - r * ch - ch / 2 - 4, labels[r])
        for k in range(cols):
            cx = M + lw + k * cw + cw / 2
            cy = top - r * ch - ch / 2
            c.setStrokeColor(INK)
            if p.get("shape", "star") == "star":
                star(c, cx, cy, min(cw, ch) * 0.4)
            else:
                c.circle(cx, cy, min(cw, ch) * 0.36, stroke=1, fill=0)
    d.y = top - rows * ch - 10
    h = d.y - FOOT_H
    if h > 50:
        box(d, M, d.y, d.W - 2 * M, min(h, 90), "My reward when the chart is full", True)


def k_numline(d, p):
    c = d.c
    a, b = p["start"], p["end"]
    lab = p.get("label_step", 1)
    n = b - a
    lines = p.get("lines", 5)
    if p.get("fields"):
        fields(d, p["fields"])
    area = d.y - FOOT_H - 10
    gap = area / lines
    x0, x1 = M + 14, d.W - M - 14
    for i in range(lines):
        y = d.y - gap * (i + 0.5)
        c.setStrokeColor(INK)
        c.setLineWidth(1.6)
        draw_arrow(c, x0 - 8, y, x1 + 8, y, 7)
        c.line(x1 + 8, y, x0 - 8, y)
        draw_arrow(c, x1 + 8, y, x0 - 8, y, 7)
        for k in range(n + 1):
            x = x0 + (x1 - x0) * k / n
            major = (a + k) % lab == 0
            c.setLineWidth(1.4 if major else 0.8)
            c.line(x, y - (9 if major else 5), x, y + (9 if major else 5))
            if major:
                v = a + k
                c.setFillColor(INK)
                size = 11 if n <= 25 else 9
                c.setFont("Helvetica-Bold", size)
                c.drawCentredString(x, y - 24, str(v) if v >= 0 else "-" + str(abs(v)))
    d.y = FOOT_H


def k_hundred(d, p):
    c = d.c
    start = p.get("from", 1)
    blank = p.get("blank", False)
    if p.get("fields"):
        fields(d, p["fields"])
    side = min((d.W - 2 * M) / 10, (d.y - FOOT_H - 10) / 10)
    x0 = (d.W - side * 10) / 2
    top = d.y - 6
    for r in range(10):
        for k in range(10):
            x, y = x0 + k * side, top - (r + 1) * side
            c.setStrokeColor(LINE)
            c.setLineWidth(0.9)
            if (r + k) % 2 == 0 and not blank:
                c.setFillColor(FAINT)
                c.rect(x, y, side, side, stroke=1, fill=1)
            else:
                c.rect(x, y, side, side, stroke=1, fill=0)
            if not blank:
                c.setFillColor(INK)
                c.setFont("Helvetica-Bold", side * 0.34)
                c.drawCentredString(x + side / 2, y + side * 0.33, str(start + r * 10 + k))
    d.y = FOOT_H


def k_multgrid(d, p):
    c = d.c
    blank = p.get("blank", False)
    n = 13
    if p.get("fields"):
        fields(d, p["fields"])
    side = min((d.W - 2 * M) / n, (d.y - FOOT_H - 10) / n)
    x0 = (d.W - side * n) / 2
    top = d.y - 6
    for r in range(n):
        for k in range(n):
            x, y = x0 + k * side, top - (r + 1) * side
            head = r == 0 or k == 0
            c.setStrokeColor(LINE)
            c.setLineWidth(0.8)
            if head:
                c.setFillColor(TEAL if (r or k) else white)
                c.rect(x, y, side, side, stroke=1, fill=1)
            else:
                c.setFillColor(FAINT if (r == k) else white)
                c.rect(x, y, side, side, stroke=1, fill=1)
            txt = None
            if r == 0 and k == 0:
                txt, col = "x", INK
            elif head:
                txt, col = str(max(r, k)), white
            elif not blank:
                txt, col = str(r * k), INK
            if txt:
                c.setFillColor(col)
                c.setFont("Helvetica-Bold", side * 0.36)
                c.drawCentredString(x + side / 2, y + side * 0.32, txt)
    d.y = FOOT_H


def k_patterns(d, p):
    c = d.c
    kind = p["pattern"]
    fields(d, ["Name", "Date"])
    rows = p.get("rows", 8)
    area = d.y - FOOT_H - 6
    rh = area / rows
    x0, x1 = M + 20, d.W - M - 20
    c.setStrokeColor(INK)
    c.setLineWidth(2.2)
    c.setDash(1, 5)
    c.setLineCap(1)
    for r in range(rows):
        yc = d.y - rh * (r + 0.5)
        amp = min(rh * 0.32, 16)
        pts = []
        if kind == "straight":
            if r % 2 == 0:
                for k in range(14):
                    x = x0 + (x1 - x0) * (k + 0.5) / 14
                    c.line(x, yc - amp, x, yc + amp)
                pts = None
            else:
                c.line(x0, yc, x1, yc)
                pts = None
        elif kind == "waves":
            steps = 200
            for s in range(steps + 1):
                t = s / steps
                pts.append((x0 + (x1 - x0) * t, yc + amp * math.sin(t * math.pi * 2 * (4 + r % 3))))
        elif kind == "zigzag":
            segs = 8 + (r % 3) * 2
            for s in range(segs + 1):
                pts.append((x0 + (x1 - x0) * s / segs, yc + (amp if s % 2 == 0 else -amp)))
        elif kind == "loops":
            if r % 2 == 0:
                for s in range(401):
                    t = s / 400 * math.pi * 2 * 6
                    pts.append((x0 + (x1 - x0) * s / 400 + amp * 0.9 * math.sin(t), yc + amp * math.cos(t)))
            else:
                for k in range(4):
                    cx = x0 + (x1 - x0) * (k + 0.5) / 4
                    pts_s = []
                    for s in range(201):
                        t = s / 200 * math.pi * 6
                        rad = amp * 0.15 + amp * 0.85 * (s / 200)
                        pts_s.append((cx + rad * math.cos(t), yc + rad * math.sin(t)))
                    pp = c.beginPath()
                    pp.moveTo(*pts_s[0])
                    for q in pts_s[1:]:
                        pp.lineTo(*q)
                    c.drawPath(pp, stroke=1, fill=0)
                pts = None
        if pts:
            pp = c.beginPath()
            pp.moveTo(*pts[0])
            for q in pts[1:]:
                pp.lineTo(*q)
            c.drawPath(pp, stroke=1, fill=0)
        c.setDash()
        c.setFillColor(TEAL)
        c.circle(x0 - 10, yc, 4, stroke=0, fill=1)
        c.setFillColor(MARK)
        c.setStrokeColor(INK)
        c.setLineWidth(0.8)
        c.circle(x1 + 10, yc, 4, stroke=1, fill=1)
        c.setStrokeColor(INK)
        c.setLineWidth(2.2)
        c.setDash(1, 5)
    c.setDash()
    c.setLineCap(0)
    d.y = FOOT_H


def k_shape(d, p):
    c = d.c
    fields(d, ["Name", "Date"])
    shape = p["shape"]
    top = d.y
    cx, cy = d.W / 2, top - 200
    c.setStrokeColor(INK)
    c.setLineWidth(3.4)
    c.setDash(1, 7)
    c.setLineCap(1)
    if shape == "circle":
        c.circle(cx, cy, 150, stroke=1, fill=0)
    elif shape == "square":
        c.rect(cx - 140, cy - 140, 280, 280, stroke=1, fill=0)
    elif shape == "triangle":
        pp = c.beginPath()
        pp.moveTo(cx, cy + 150)
        pp.lineTo(cx - 165, cy - 120)
        pp.lineTo(cx + 165, cy - 120)
        pp.close()
        c.drawPath(pp, stroke=1, fill=0)
    elif shape == "rectangle":
        c.rect(cx - 190, cy - 100, 380, 200, stroke=1, fill=0)
    c.setDash()
    c.setLineCap(0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(cx, top - 400, "This is a " + shape + ".")
    box(d, M, top - 420, d.W - 2 * M, top - 420 - FOOT_H - 4, "Now draw your own " + shape + " and colour it in", False)
    d.y = FOOT_H


def k_shapehunt(d, p):
    c = d.c
    fields(d, ["Name", "Date"])
    shapes = ["circle", "square", "triangle", "rectangle"]
    top = d.y
    ch = (top - FOOT_H - 6) / 4
    for i, sh in enumerate(shapes):
        y = top - (i + 1) * ch
        c.setStrokeColor(INK)
        c.setLineWidth(2)
        cx, cy = M + 70, y + ch / 2
        if sh == "circle":
            c.circle(cx, cy, 34, stroke=1, fill=0)
        elif sh == "square":
            c.rect(cx - 32, cy - 32, 64, 64, stroke=1, fill=0)
        elif sh == "triangle":
            pp = c.beginPath()
            pp.moveTo(cx, cy + 36)
            pp.lineTo(cx - 40, cy - 30)
            pp.lineTo(cx + 40, cy - 30)
            pp.close()
            c.drawPath(pp, stroke=1, fill=0)
        else:
            c.rect(cx - 44, cy - 26, 88, 52, stroke=1, fill=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(M + 140, cy + 4, "I found a " + sh + " in:")
        box(d, M + 140, y + ch - 14, d.W - 2 * M - 140, ch - 24, None, False)
    d.y = FOOT_H


def k_numtrace(d, p):
    c = d.c
    digits = p["digits"]
    fields(d, ["Name", "Date"])
    top = d.y
    rh = (top - FOOT_H - 6) / len(digits)
    for i, dg in enumerate(digits):
        y = top - (i + 1) * rh
        c.setFillColor(TEAL)
        c.setFont("Helvetica-Bold", rh * 0.72)
        c.drawString(M + 6, y + rh * 0.2, str(dg))
        c.setStrokeColor(INK)
        c.setLineWidth(1.4)
        c.setDash(2, 3)
        c.setFillColor(white)
        for k in range(4):
            t = c.beginText(M + 110 + k * 100, y + rh * 0.2)
            t.setFont("Helvetica-Bold", rh * 0.72)
            t.setTextRenderMode(1)
            t.textOut(str(dg))
            c.drawText(t)
        c.setDash()
        c.setStrokeColor(PALE)
        c.setLineWidth(0.6)
        c.line(M, y + 4, d.W - M, y + 4)
    d.y = FOOT_H


def k_countsheet(d, p):
    c = d.c
    counts = p["counts"]
    fields(d, ["Name", "Date"])
    top = d.y
    rh = (top - FOOT_H - 6) / len(counts)
    for i, n in enumerate(counts):
        y = top - (i + 1) * rh
        cols = 5 if n <= 5 else 5
        c.setStrokeColor(INK)
        c.setLineWidth(1.6)
        for k in range(n):
            r_, c_ = divmod(k, cols)
            cx = M + 40 + c_ * 52
            cy = y + rh - 30 - r_ * 50
            if p.get("object", "star") == "star":
                c.setFillColor(MARK)
                star(c, cx, cy, 20, fill=True)
            else:
                c.setFillColor(SOFT)
                c.circle(cx, cy, 18, stroke=1, fill=1)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(d.W - M - 250, y + rh / 2 + 4, "How many?")
        box(d, d.W - M - 130, y + rh / 2 + 24, 110, 50, None)
        c.setStrokeColor(PALE)
        c.setLineWidth(0.6)
        c.line(M, y + 3, d.W - M, y + 3)
    d.y = FOOT_H


def k_tenframes(d, p):
    c = d.c
    fields(d, ["Name", "Date"])
    top = d.y
    cols, rows = 2, 4
    cw = (d.W - 2 * M) / cols
    ch = (top - FOOT_H - 6) / rows
    for r in range(rows):
        for k in range(cols):
            x0 = M + k * cw + 12
            fw = cw - 24
            sq = fw / 5
            y0 = top - (r + 1) * ch + (ch - 2 * sq) / 2
            for rr in range(2):
                for cc in range(5):
                    c.setStrokeColor(INK)
                    c.setLineWidth(1.4)
                    c.rect(x0 + cc * sq, y0 + rr * sq, sq, sq, stroke=1, fill=0)
    d.y = FOOT_H


def k_paper(d, p):
    c = d.c
    kind = p["paper"]
    top = d.y if not p.get("fields") else (fields(d, p["fields"]) or d.y)
    top = d.y
    bottom = FOOT_H
    if kind == "squared":
        step = p.get("step", 28.35)
        c.setStrokeColor(PALE)
        c.setLineWidth(0.6)
        x = M
        while x <= d.W - M + 0.1:
            c.line(x, bottom, x, top)
            x += step
        y = top
        while y >= bottom:
            c.line(M, y, d.W - M, y)
            y -= step
    elif kind == "dots":
        step = 28.35
        c.setFillColor(LINE)
        y = top
        while y >= bottom:
            x = M
            while x <= d.W - M:
                c.circle(x, y, 1.1, stroke=0, fill=1)
                x += step
            y -= step
    elif kind == "iso":
        step = 28.35
        c.setFillColor(LINE)
        row = 0
        y = top
        while y >= bottom:
            x = M + (step / 2 if row % 2 else 0)
            while x <= d.W - M:
                c.circle(x, y, 1.1, stroke=0, fill=1)
                x += step
            y -= step * 0.866
            row += 1
    d.y = FOOT_H


def k_hwlines(d, p):
    c = d.c
    fields(d, ["Name", "Date"])
    style = p.get("style", "ks1")
    y = d.y - 10
    while y > FOOT_H + 50:
        if style == "ks1":
            c.setStrokeColor(PALE)
            c.setLineWidth(0.8)
            c.line(M, y, d.W - M, y)
            c.line(M, y - 26, d.W - M, y - 26)
            c.setStrokeColor(LINE)
            c.setDash(4, 3)
            c.line(M, y - 13, d.W - M, y - 13)
            c.setDash()
            c.setStrokeColor(INK)
            c.setLineWidth(1.1)
            c.line(M, y - 26, d.W - M, y - 26) if False else None
            c.setStrokeColor(LINE)
            c.line(M, y - 39, d.W - M, y - 39)
            y -= 62
        else:
            c.setStrokeColor(LINE)
            c.setLineWidth(0.7)
            c.line(M, y, d.W - M, y)
            y -= 24
    d.y = FOOT_H


def k_organiser(d, p):
    c = d.c
    t = p["type"]
    if p.get("fields", True):
        fields(d, p.get("fields_list", ["Name", "Topic", "Date"]))
    top, bot = d.y, FOOT_H + 4
    W = d.W
    H = top - bot
    if t == "kwl":
        labs = p.get("labels", ["What I know", "What I want to know", "What I learned"])
        n = len(labs)
        cw = (W - 2 * M) / n
        for i, lab in enumerate(labs):
            x = M + i * cw
            c.setFillColor(TEAL)
            c.rect(x, top - 28, cw, 28, stroke=0, fill=1)
            text_in(c, lab, x + 4, top, cw - 8, 28, "Helvetica-Bold", 11, white, "center")
            c.setStrokeColor(LINE)
            c.setLineWidth(1)
            c.rect(x, bot, cw, H - 28, stroke=1, fill=0)
    elif t in ("venn2", "venn3"):
        c.setLineWidth(2)
        if t == "venn2":
            r = min(H / 2.2, (W - 2 * M) / 3.4)
            cy = bot + H / 2 - 10
            for dx, col in ((-0.55, TEAL), (0.55, MARK)):
                c.setFillColor(col)
                c.setFillAlpha(0.14)
                c.setStrokeColor(INK)
                c.circle(W / 2 + dx * r, cy, r, stroke=1, fill=1)
                c.setFillAlpha(1)
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(W / 2 - 0.9 * r, cy + r + 8, "Only A")
            c.drawCentredString(W / 2 + 0.9 * r, cy + r + 8, "Only B")
            c.drawCentredString(W / 2, cy - r - 16, "Both")
        else:
            r = min(H / 3.0, (W - 2 * M) / 3.2)
            cx, cy = W / 2, bot + H / 2
            pos = [(-0.55 * r, 0.4 * r, TEAL), (0.55 * r, 0.4 * r, MARK), (0, -0.55 * r, HexColor("#f06595"))]
            for dx, dy, col in pos:
                c.setFillColor(col)
                c.setFillAlpha(0.14)
                c.setStrokeColor(INK)
                c.circle(cx + dx, cy + dy, r, stroke=1, fill=1)
                c.setFillAlpha(1)
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(cx - 1.25 * r, cy + 1.45 * r, "A")
            c.drawCentredString(cx + 1.25 * r, cy + 1.45 * r, "B")
            c.drawCentredString(cx, cy - 1.7 * r, "C")
    elif t == "mindmap":
        cx, cy = W / 2, bot + H / 2
        centre = p.get("centre", "Main idea")
        n = 6
        rx, ry = (W - 2 * M) / 2 - 70, H / 2 - 40
        for i in range(n):
            ang = math.pi / 2 + i * 2 * math.pi / n
            bx, by = cx + rx * math.cos(ang), cy + ry * math.sin(ang)
            c.setStrokeColor(LINE)
            c.setLineWidth(1.5)
            c.line(cx, cy, bx, by)
        for i in range(n):
            ang = math.pi / 2 + i * 2 * math.pi / n
            bx, by = cx + rx * math.cos(ang), cy + ry * math.sin(ang)
            c.setFillColor(white)
            c.setStrokeColor(TEAL)
            c.setLineWidth(1.6)
            c.ellipse(bx - 70, by - 32, bx + 70, by + 32, stroke=1, fill=1)
        c.setFillColor(TEAL)
        c.roundRect(cx - 75, cy - 34, 150, 68, 10, stroke=0, fill=1)
        text_in(c, centre, cx - 70, cy + 34, 140, 68, "Helvetica-Bold", 14, white, "center")
    elif t == "timeline":
        y = bot + H / 2
        c.setStrokeColor(INK)
        c.setLineWidth(2.5)
        draw_arrow(c, M, y, W - M, y, 9)
        n = 8
        bw = (W - 2 * M) / 4.3
        for i in range(n):
            x = M + 30 + (W - 2 * M - 60) * i / (n - 1)
            c.setFillColor(TEAL)
            c.circle(x, y, 6, stroke=0, fill=1)
            up = i % 2 == 0
            bx = min(max(x - bw / 2, M), W - M - bw)
            by = y + 18 if up else y - 18 - 110
            c.setStrokeColor(LINE)
            c.setLineWidth(1)
            c.line(x, y + (6 if up else -6), x, by if not up else by)
            c.setFillColor(white)
            c.roundRect(bx, by, bw, 110, 4, stroke=1, fill=1)
            c.setFillColor(TEAL)
            c.setFont("Helvetica-Bold", 8.5)
            c.drawString(bx + 6, by + 98, "Date:")
    elif t == "frayer":
        side = min(W - 2 * M, H)
        x0, y0 = (W - side) / 2, bot + (H - side) / 2
        c.setStrokeColor(INK)
        c.setLineWidth(1.6)
        c.rect(x0, y0, side, side, stroke=1, fill=0)
        c.line(x0, y0, x0 + side, y0 + side)
        c.line(x0, y0 + side, x0 + side, y0)
        c.setFillColor(white)
        c.ellipse(W / 2 - 80, y0 + side / 2 - 36, W / 2 + 80, y0 + side / 2 + 36, stroke=1, fill=1)
        c.setFillColor(TEAL)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(W / 2, y0 + side / 2 - 4, "Word")
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(W / 2, y0 + side - 16, "Definition")
        c.drawCentredString(W / 2, y0 + 8, "Non-examples")
        c.saveState()
        c.translate(x0 + 14, y0 + side / 2)
        c.rotate(90)
        c.drawCentredString(0, 0, "Characteristics")
        c.restoreState()
        c.saveState()
        c.translate(x0 + side - 6, y0 + side / 2)
        c.rotate(-90)
        c.drawCentredString(0, 0, "Examples")
        c.restoreState()
    elif t == "cause_effect":
        n = p.get("rows", 4)
        rh = H / n
        bw = (W - 2 * M - 70) / 2
        for i in range(n):
            y = top - (i + 1) * rh + 8
            box(d, M, y + rh - 16, bw, rh - 16, "Cause", True)
            box(d, M + bw + 70, y + rh - 16, bw, rh - 16, "Effect", True)
            c.setStrokeColor(INK)
            c.setLineWidth(2)
            draw_arrow(c, M + bw + 8, y + rh / 2 - 8, M + bw + 62, y + rh / 2 - 8, 8)
    elif t == "tchart":
        labs = p.get("labels", ["Heading A", "Heading B"])
        cw = (W - 2 * M) / 2
        for i, lab in enumerate(labs):
            x = M + i * cw
            c.setFillColor(TEAL)
            c.rect(x, top - 30, cw, 30, stroke=0, fill=1)
            text_in(c, lab, x + 4, top, cw - 8, 30, "Helvetica-Bold", 12, white, "center")
            c.setStrokeColor(LINE)
            c.setLineWidth(1)
            c.rect(x, bot, cw, H - 30, stroke=1, fill=0)
            yy = top - 52
            while yy > bot + 6:
                c.setStrokeColor(PALE)
                c.setLineWidth(0.6)
                c.line(x + 8, yy, x + cw - 8, yy)
                yy -= 26
    elif t == "flowchart":
        n = 5
        bh = min(70, (H - 40 * (n - 1)) / n)
        bw = 320
        for i in range(n):
            y = top - i * (bh + 36) - bh
            c.setFillColor(SOFT if i % 2 == 0 else white)
            c.setStrokeColor(TEAL)
            c.setLineWidth(1.6)
            c.roundRect(W / 2 - bw / 2, y, bw, bh, 10, stroke=1, fill=1)
            if i < n - 1:
                c.setStrokeColor(INK)
                draw_arrow(c, W / 2, y - 4, W / 2, y - 32, 7)
    elif t == "sequence":
        labs = ["First", "Next", "Then", "Finally"]
        gap = 26
        bw = (W - 2 * M - gap * 3) / 4
        for i, lab in enumerate(labs):
            x = M + i * (bw + gap)
            box(d, x, top - 4, bw, H - 8, lab, False)
            c.setStrokeColor(PALE)
            c.setLineWidth(0.6)
            yy = bot + 16 + 5 * 22
            for _ in range(5):
                c.line(x + 7, yy, x + bw - 7, yy)
                yy -= 22
            if i < 3:
                c.setStrokeColor(INK)
                c.setLineWidth(2)
                draw_arrow(c, x + bw + 3, top - H / 2, x + bw + gap - 3, top - H / 2, 7)
    elif t == "mountain":
        mh = min(260, H * 0.45)
        pts = [(M, top - mh), (M + (W - 2 * M) * 0.2, top - mh * 0.55), (M + (W - 2 * M) * 0.4, top - mh * 0.3),
               (M + (W - 2 * M) * 0.55, top - 6), (M + (W - 2 * M) * 0.78, top - mh * 0.55), (W - M, top - mh)]
        pp = c.beginPath()
        pp.moveTo(*pts[0])
        for q in pts[1:]:
            pp.lineTo(*q)
        pp.lineTo(W - M, top - mh)
        pp.close()
        c.setFillColor(SOFT)
        c.setStrokeColor(TEAL)
        c.setLineWidth(2)
        c.drawPath(pp, stroke=1, fill=1)
        names = ["Opening", "Build-up", "Problem", "Resolution", "Ending"]
        # labels at points 1..5 approx
        lab_pos = [pts[0], pts[1], pts[3], pts[4], pts[5]]
        for nm, (px, py) in zip(names, lab_pos):
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(min(max(px, M + 24), W - M - 24), py + 8, nm)
        by = top - mh - 14
        bh = (by - bot) / 3 - 6
        bw = (W - 2 * M - 8) / 2
        for i, nm in enumerate(names):
            r_, c_ = divmod(i, 2)
            box(d, M + c_ * (bw + 8), by - r_ * (bh + 6), bw if i < 4 else bw, bh, nm, True)
    elif t == "lights":
        items = p.get("items", ["I can explain what I have learned", "I can give an example", "I can use new vocabulary", "I can check my own work"])
        rh = min(70, H / (len(items) + 1))
        c.setFillColor(TEAL)
        c.rect(M, top - 26, W - 2 * M, 26, stroke=0, fill=1)
        text_in(c, "I can...", M + 6, top, 200, 26, "Helvetica-Bold", 10.5, white)
        for j, nm in enumerate(["Got it", "Nearly", "Not yet"]):
            text_in(c, nm, W - M - (3 - j) * 70, top, 70, 26, "Helvetica-Bold", 9, white, "center")
        for i, it in enumerate(items):
            y = top - 26 - (i + 1) * rh
            c.setStrokeColor(LINE)
            c.setLineWidth(0.8)
            c.rect(M, y, W - 2 * M, rh, stroke=1, fill=0)
            text_in(c, it, M + 8, y + rh, W - 2 * M - 230, rh, "Helvetica", 10.5, INK)
            for j, col in enumerate(["#2f9e44", "#f7c52a", "#e03131"]):
                c.setFillColor(white)
                c.setStrokeColor(HexColor(col))
                c.setLineWidth(2.2)
                c.circle(W - M - (3 - j) * 70 + 35, y + rh / 2, 14, stroke=1, fill=0)
    elif t == "stars":
        c.setFillColor(INK)
        yy = top - 10
        for i, (lab, h) in enumerate([("Two stars: what went well", 170), ("A wish: what could be even better", 170)]):
            if i == 0:
                for s_i in range(2):
                    c.setFillColor(MARK)
                    c.setStrokeColor(INK)
                    c.setLineWidth(1)
                    star(c, M + 20 + s_i * 36, yy - 24, 14, fill=True)
                box(d, M, yy - 50, W - 2 * M, 130, None, True)
                yy -= 50 + 130 + 14
            else:
                c.setFillColor(INK)
                c.setFont("Helvetica-Bold", 13)
                c.drawString(M, yy - 18, "A wish: what could be even better")
                box(d, M, yy - 30, W - 2 * M, 130, None, True)
                yy -= 30 + 130 + 14
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(M, yy - 18, "My response and next step")
        box(d, M, yy - 30, W - 2 * M, max(60, yy - 30 - bot), None, True)
    d.y = FOOT_H


def k_cal_year(d, p):
    c = d.c
    start_year = p.get("year", 2026)
    months = [(start_year, m) for m in range(9, 13)] + [(start_year + 1, m) for m in range(1, 9)]
    cols, rows = 4, 3
    top = d.y
    cw = (d.W - 2 * M) / cols
    ch = (top - FOOT_H - 6) / rows
    for i, (yr, mo) in enumerate(months):
        r_, c_ = divmod(i, cols)
        x = M + c_ * cw + 6
        y = top - r_ * ch
        w = cw - 12
        c.setFillColor(TEAL)
        c.rect(x, y - 20, w, 20, stroke=0, fill=1)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 6, y - 14, calendar.month_name[mo] + " " + str(yr))
        cell = w / 7
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 6.5)
        for k, dn in enumerate("MTWTFSS"):
            c.drawCentredString(x + cell * (k + 0.5), y - 30, dn)
        weeks = calendar.Calendar(0).monthdayscalendar(yr, mo)
        rh = (ch - 52) / 6
        for wi, wk in enumerate(weeks):
            for k, day in enumerate(wk):
                if day:
                    c.setFont("Helvetica", 7)
                    c.setFillColor(LINE if k > 4 else INK)
                    c.drawCentredString(x + cell * (k + 0.5), y - 42 - wi * rh, str(day))
        c.setStrokeColor(PALE)
        c.setLineWidth(0.6)
        c.rect(x, y - ch + 14, w, ch - 14, stroke=1, fill=0)
    d.y = FOOT_H


def k_cal_month(d, p):
    c = d.c
    fields(d, ["Month and year", "Class or focus"])
    top = d.y
    cw = (d.W - 2 * M) / 7
    hh = 22
    ch = (top - FOOT_H - hh - 4) / 6
    for k, dn in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
        c.setFillColor(TEAL)
        c.setStrokeColor(white)
        c.rect(M + k * cw, top - hh, cw, hh, stroke=1, fill=1)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(M + k * cw + cw / 2, top - 15, dn)
    for r in range(6):
        for k in range(7):
            c.setStrokeColor(LINE)
            c.setLineWidth(0.7)
            c.setFillColor(FAINT if k > 4 else white)
            c.rect(M + k * cw, top - hh - (r + 1) * ch, cw, ch, stroke=1, fill=1)
    d.y = FOOT_H


def k_seating(d, p):
    c = d.c
    fields(d, ["Class", "Teacher", "Term"])
    top = d.y
    W = d.W
    c.setFillColor(INK)
    c.roundRect(W / 2 - 100, top - 24, 200, 24, 4, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(W / 2, top - 16, "BOARD / FRONT OF ROOM")
    area_top, bot = top - 40, FOOT_H + 6
    style = p["style"]

    def desk(x, y, w, h):
        c.setFillColor(white)
        c.setStrokeColor(INK)
        c.setLineWidth(1.1)
        c.roundRect(x, y, w, h, 4, stroke=1, fill=1)
        c.setStrokeColor(PALE)
        c.setLineWidth(0.6)
        c.line(x + 5, y + h * 0.32, x + w - 5, y + h * 0.32)

    if style == "rows":
        cols, rows = p.get("cols", 5), p.get("rows", 6)
        gw = (W - 2 * M) / cols
        gh = (area_top - bot) / rows
        for r in range(rows):
            for k in range(cols):
                desk(M + k * gw + 6, area_top - (r + 1) * gh + 6, gw - 12, gh - 12)
    elif style == "groups":
        cols, rows = 3, 2
        gw = (W - 2 * M) / cols
        gh = (area_top - bot) / rows
        for r in range(rows):
            for k in range(cols):
                x, y = M + k * gw + 10, area_top - (r + 1) * gh + 10
                c.setFillColor(SOFT)
                c.setStrokeColor(TEAL)
                c.setLineWidth(1.4)
                c.roundRect(x, y, gw - 20, gh - 20, 8, stroke=1, fill=1)
                sw, sh = (gw - 20 - 30) / 2, (gh - 20 - 40) / 3
                for s in range(6):
                    sr, sc = divmod(s, 2)
                    desk(x + 10 + sc * (sw + 10), y + gh - 20 - 10 - (sr + 1) * sh - sr * 6, sw, sh)
    elif style == "horseshoe":
        n_side, n_bot = 6, 7
        dw, dh = 70, 40
        gap_y = (area_top - bot - 10) / n_side
        for i in range(n_side):
            y = area_top - (i + 1) * gap_y + (gap_y - dh) / 2
            desk(M + 6, y, dw, dh)
            desk(W - M - 6 - dw, y, dw, dh)
        gx = (W - 2 * M - 2 * dw - 20) / n_bot
        for k in range(n_bot):
            desk(M + dw + 14 + k * gx + 3, bot + 4, gx - 6, dh)
    d.y = FOOT_H


def k_fracwall(d, p):
    c = d.c
    fields(d, ["Name", "Date"])
    top = d.y
    rows = 12
    rh = (top - FOOT_H - 6) / rows
    tw = d.W - 2 * M
    for n in range(1, rows + 1):
        y = top - n * rh
        for k in range(n):
            x = M + tw * k / n
            c.setFillColor(HexColor(["#cfeeea", "#fff0b3", "#ffd9e4", "#d9e6ff"][(n - 1) % 4]))
            c.setStrokeColor(INK)
            c.setLineWidth(1)
            c.rect(x, y + 2, tw / n, rh - 4, stroke=1, fill=1)
            c.setFillColor(INK)
            lab = "1" if n == 1 else "1/" + str(n)
            c.setFont("Helvetica-Bold", min(11, tw / n * 0.3))
            c.drawCentredString(x + tw / n / 2, y + rh / 2 - 3, lab)
    d.y = FOOT_H


def k_clocks(d, p):
    c = d.c
    fields(d, ["Name", "Date"])
    top = d.y
    cols, rows = 2, 2
    cw = (d.W - 2 * M) / cols
    ch = (top - FOOT_H - 6) / rows
    numbers = p.get("numbers", True)
    for r in range(rows):
        for k in range(cols):
            cx, cy = M + k * cw + cw / 2, top - r * ch - ch / 2 + 6
            R = min(cw, ch) * 0.36
            c.setStrokeColor(INK)
            c.setLineWidth(2.4)
            c.setFillColor(white)
            c.circle(cx, cy, R, stroke=1, fill=1)
            for t in range(60):
                ang = math.pi / 2 - t * math.pi / 30
                r1 = R * (0.9 if t % 5 == 0 else 0.95)
                c.setLineWidth(1.6 if t % 5 == 0 else 0.6)
                c.line(cx + R * 0.99 * math.cos(ang), cy + R * 0.99 * math.sin(ang), cx + r1 * math.cos(ang), cy + r1 * math.sin(ang))
            if numbers:
                c.setFillColor(INK)
                c.setFont("Helvetica-Bold", R * 0.17)
                for h in range(1, 13):
                    ang = math.pi / 2 - h * math.pi / 6
                    c.drawCentredString(cx + R * 0.74 * math.cos(ang), cy + R * 0.74 * math.sin(ang) - R * 0.06, str(h))
            c.setFillColor(INK)
            c.circle(cx, cy, 3, stroke=0, fill=1)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(cx - R * 0.6, cy - R - 22, "Time:")
            c.setStrokeColor(LINE)
            c.setLineWidth(0.8)
            c.line(cx - R * 0.6 + 36, cy - R - 24, cx + R * 0.7, cy - R - 24)
    d.y = FOOT_H


def k_bonds(d, p):
    c = d.c
    total = p["total"]
    fields(d, ["Name", "Date"])
    top = d.y
    # bond shapes
    for i in range(3):
        cx = M + 90 + i * 170
        cy = top - 70
        c.setStrokeColor(TEAL)
        c.setLineWidth(1.8)
        c.line(cx, cy - 20, cx - 34, cy - 66)
        c.line(cx, cy - 20, cx + 34, cy - 66)
        c.setFillColor(SOFT)
        c.circle(cx, cy, 24, stroke=1, fill=1)
        c.setFillColor(white)
        c.circle(cx - 34, cy - 80, 22, stroke=1, fill=1)
        c.circle(cx + 34, cy - 80, 22, stroke=1, fill=1)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 16)
        if i == 0:
            c.drawCentredString(cx, cy - 5, str(total))
    y = top - 200
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(M, y, "Complete the number sentences.")
    y -= 14
    n = total + 1
    per = math.ceil(n / 2)
    rh = min(34, (y - FOOT_H - 10) / per)
    for i in range(n):
        col, r = divmod(i, per)
        x = M + col * ((d.W - 2 * M) / 2)
        yy = y - (r + 1) * rh
        c.setFont("Helvetica", 15)
        c.setFillColor(INK)
        c.drawString(x + 4, yy + 8, f"{i}  +")
        c.setStrokeColor(LINE)
        c.setLineWidth(0.8)
        c.rect(x + 50, yy, 40, 24, stroke=1, fill=0)
        c.drawString(x + 100, yy + 8, f"=  {total}")
    d.y = FOOT_H


def k_partwhole(d, p):
    c = d.c
    fields(d, ["Name", "Date"])
    top = d.y
    cols, rows = 2, 3
    cw = (d.W - 2 * M) / cols
    ch = (top - FOOT_H - 6) / rows
    for r in range(rows):
        for k in range(cols):
            cx, cy = M + k * cw + cw / 2, top - r * ch - 60
            c.setStrokeColor(TEAL)
            c.setLineWidth(2)
            if p.get("model") == "bar":
                bw = cw - 50
                c.setFillColor(SOFT)
                c.rect(cx - bw / 2, cy - 10, bw, 40, stroke=1, fill=1)
                c.setFillColor(white)
                c.rect(cx - bw / 2, cy - 70, bw / 2, 40, stroke=1, fill=1)
                c.rect(cx, cy - 70, bw / 2, 40, stroke=1, fill=1)
                c.setFillColor(INK)
                c.setFont("Helvetica-Bold", 12)
                c.drawCentredString(cx, cy + 6, "Whole")
            else:
                c.line(cx, cy - 20, cx - 44, cy - 66)
                c.line(cx, cy - 20, cx + 44, cy - 66)
                c.setFillColor(SOFT)
                c.circle(cx, cy, 30, stroke=1, fill=1)
                c.setFillColor(white)
                c.circle(cx - 44, cy - 88, 28, stroke=1, fill=1)
                c.circle(cx + 44, cy - 88, 28, stroke=1, fill=1)
    d.y = FOOT_H


def k_column(d, p):
    c = d.c
    op = p["op"]
    fields(d, ["Name", "Date"])
    top = d.y
    cols, rows = 3, 3
    cw = (d.W - 2 * M) / cols
    ch = (top - FOOT_H - 6) / rows
    for r in range(rows):
        for k in range(cols):
            x0 = M + k * cw + 24
            y0 = top - (r + 1) * ch + 16
            heads = ["Th", "H", "T", "O"]
            colw = (cw - 60) / 4
            for j, hd in enumerate(heads):
                c.setStrokeColor(LINE)
                c.setLineWidth(0.8)
                c.setFillColor(SOFT)
                c.rect(x0 + 18 + j * colw, y0 + ch - 50, colw, 16, stroke=1, fill=1)
                c.setFillColor(INK)
                c.setFont("Helvetica-Bold", 8)
                c.drawCentredString(x0 + 18 + j * colw + colw / 2, y0 + ch - 45, hd)
                c.rect(x0 + 18 + j * colw, y0 + 20, colw, ch - 70 - 20, stroke=1, fill=0)
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 20)
            c.drawString(x0, y0 + ch - 130, op)
            c.setStrokeColor(INK)
            c.setLineWidth(1.6)
            c.line(x0 + 18, y0 + 66, x0 + 18 + 4 * colw, y0 + 66)
    d.y = FOOT_H


def k_spelling(d, p):
    c = d.c
    fields(d, ["Name", "Week beginning"])
    header = ["Word", "Look", "Cover", "Write", "Check", "Write again", "Tick"]
    k_table(d, {"header": header, "widths": [2, 2, 2, 2, 1, 2, 1], "rows": None, "row_h": 34})


KINDS = {
    "form": k_form, "table": k_table, "checklist": k_checklist, "cards": k_cards, "certificate": k_certificate,
    "reward": k_reward, "numline": k_numline, "hundred": k_hundred, "multgrid": k_multgrid, "patterns": k_patterns,
    "shape": k_shape, "shapehunt": k_shapehunt, "numtrace": k_numtrace, "countsheet": k_countsheet,
    "tenframes": k_tenframes, "paper": k_paper, "hwlines": k_hwlines, "organiser": k_organiser,
    "cal_year": k_cal_year, "cal_month": k_cal_month, "seating": k_seating, "fracwall": k_fracwall,
    "clocks": k_clocks, "bonds": k_bonds, "partwhole": k_partwhole, "column": k_column, "spelling": k_spelling,
}

# ---------------------------------------------------------------- catalogue
CATS = {
    "ey-observation": ("Early years: observation and assessment", ["nursery", "teacher", "student"], ["early"]),
    "ey-planning": ("Early years: planning and provision", ["nursery", "teacher", "student"], ["early"]),
    "ey-records": ("Early years: records and checklists", ["nursery"], ["early"]),
    "ey-activities": ("Early years: child activity sheets", ["nursery", "teacher", "student"], ["early", "primary"]),
    "ey-literacy": ("Early years: letters, sounds and words", ["nursery", "teacher", "student"], ["early", "primary"]),
    "ey-maths": ("Early years: early maths", ["nursery", "teacher", "student"], ["early", "primary"]),
    "ey-roleplay": ("Early years: role play and provision", ["nursery", "teacher", "student"], ["early"]),
    "ey-topics": ("Early years: topics and seasons", ["nursery", "teacher", "student"], ["early", "primary"]),
    "primary-planning": ("Primary: planning and assessment", ["teacher", "student"], ["primary"]),
    "primary-maths-literacy": ("Primary: maths and literacy tools", ["teacher", "student"], ["primary"]),
    "organisers": ("Graphic organisers and study skills", ["teacher", "student"], ["primary", "secondary"]),
    "secondary": ("Secondary teaching tools", ["teacher", "student"], ["secondary"]),
    "trainee": ("Student teacher and early career toolkit", ["student", "teacher"], ["early", "primary", "secondary"]),
    "display": ("Display, rewards and certificates", ["teacher", "nursery", "student"], ["early", "primary", "secondary"]),
}
SPECS = []


AREA_NAMES = {
    "communication": "Communication and Language",
    "personal-social": "Personal, Social and Emotional Development",
    "physical": "Physical Development",
    "literacy": "Literacy",
    "mathematics": "Mathematics",
    "understanding-world": "Understanding the World",
    "expressive-arts": "Expressive Arts and Design",
}
AREA_BY_NAME = {v: k for k, v in AREA_NAMES.items()}
# Suggested tags for early years items, matched on the title. Items may also pass areas=[...] to add().
AREA_RULES = [
    (r"pre-writing|mark-making", ["physical", "expressive-arts"]),
    (r"trace and draw", ["physical", "mathematics"]),
    (r"name tracing|letter formation|draw and write", ["literacy", "physical"]),
    (r"trace the numbers", ["mathematics", "physical"]),
    (r"number|ten frames|count|shape|clock|measur|dot cards|days of|months of|position|size words|maths", ["mathematics"]),
    (r"alphabet|letter|sound|digraph|word|reading|bookmark|phonics|story", ["literacy"]),
    (r"emotion|all about me|key person|transition|rules|helper|wellbeing|feelings|child's voice|parent voice|birthday", ["personal-social"]),
    (r"colour|weather|season|topic|nature|minibeast|role play|café|cafe|shop|vet|surgery|post office|garden|builders|space|farm|dinosaur|sea|growing|transport|people who help|family|small world|animals", ["understanding-world"]),
    (r"open questions|language|vocabulary|timetable|conversation|talk", ["communication"]),
    (r"creative|art|music|display|enhancement", ["expressive-arts"]),
]


def infer_areas(title, cat):
    import re as _re
    if not cat.startswith("ey-"):
        return []
    m = _re.match(r"Child tracker: (.+)", title)
    if m and m.group(1) in AREA_BY_NAME:
        return [AREA_BY_NAME[m.group(1)]]
    found = []
    low = title.lower()
    for pat, ids in AREA_RULES:
        if _re.search(pat, low):
            for i in ids:
                if i not in found:
                    found.append(i)
    return found


def add(cat, title, desc, kind, sub="", land=False, **p):
    areas = p.pop("areas", None)
    SPECS.append(dict(cat=cat, title=title, desc=desc, kind=kind, sub=sub, land=land, p=p, areas=areas))


F4 = ["Child", "Date", "Practitioner", "Age"]
EYNOTE = "Adapt to match your setting's policies and the current statutory requirements."

# --- Early years: observation and assessment (20)
c_ = "ey-observation"
add(c_, "Observation sheet", "A one-page observation with areas of learning, analysis and next steps.", "form",
    "Record what you saw and heard, then decide what it tells you.",
    fields=F4, sections=[("What I saw and heard", 118, True), "@areas", [("What it tells me", 92, True), ("Characteristics of learning seen", 92, True)], ("Next steps", "fill", True)])
add(c_, "WOW moment slips", "Eight tear-off slips for capturing special moments to share with families.", "cards", "Cut along the dotted lines.",
    items=[""] * 8, cols=2, rows=4, style="slip", slip_title="WOW moment!", slip_labels=["Child", "Date"])
add(c_, "Next steps planner", "Plan a next step for each area of learning, with how you will help.", "table", "One row for each area.",
    fields=["Child", "Key person", "Date"], header=["Area of learning", "Where the child is now", "Next step", "How I will help", "Review date"],
    widths=[2.2, 3, 3, 3, 1.4], rows=[[a] for a in AREAS], row_h=60, shade_first=True)
add(c_, "Group observation sheet", "Note what several children did and said during one activity.", "table", "Good for adult-led activities.",
    fields=["Activity", "Date", "Practitioner"], header=["Child", "What they did", "What they said", "Area(s) of learning"], widths=[1.5, 4, 4, 2], rows=None, row_h=44)
add(c_, "Learning journey page", "A photo and story page for a child's learning journey book.", "form", "Add a photo, then write about what happened.",
    fields=["Child", "Term", "Date"], sections=[("Photo or drawing", 250, False), ("What happened", 100, True), ("In the child's own words", 70, True), ("Next steps", "fill", True)])
for a in AREAS:
    add(c_, "Child tracker: " + a, "Record dated observations and next steps for " + a.lower() + ".", "table", "Keep one sheet per child, per area.",
        fields=["Child", "Key person"], header=["Date", "What I observed", "Child's response", "Next step"], widths=[1.2, 4, 3, 3], rows=None, row_h=46)
add(c_, "All about me: key person profile", "A starting profile to help a child feel settled with their key person.", "form", "Complete with the family.",
    fields=["Name", "Date of birth", "Key person"], sections=[("Things I love", 90, True), ("What helps me feel settled", 90, True), ("My family and home", 90, True), ("Things I find tricky", 90, True), ("Important to know", "fill", True)])
add(c_, "Transition handover sheet", "Pass on strengths, interests and needs when a child moves room or school.", "form", "",
    fields=["Child", "Moving from", "Moving to", "Date"], sections=[[("Strengths", 110, True), ("Interests", 110, True)], [("Where support helps", 110, True), ("Home context", 110, True)], ("Ideas that work well", 90, True), ("Questions for the next teacher", "fill", True)])
add(c_, "Baseline snapshot", "A quick look at each area of learning when a child starts.", "table", "Write what you notice, not a judgement.",
    fields=["Child", "Date started", "Key person"], header=["Area of learning", "What I notice on entry", "Support needed?", "Notes"], widths=[2.4, 4, 2, 3], rows=[[a] for a in AREAS], row_h=58, shade_first=True)
add(c_, "Progress check at 2: practitioner notes", "Notes sheet to prepare for the two-year-old progress check conversation.", "form", "A planning aid, not the official summary.",
    fields=["Child", "Date of birth", "Key person", "Date"], sections=[("Communication and Language", 110, True), ("Physical Development", 110, True), ("Personal, Social and Emotional Development", 110, True), [("Strengths", 100, True), ("Where extra support could help", 100, True)], ("Ideas to share with parents", "fill", True)])
add(c_, "Characteristics of learning observation", "Notice how a child learns: playing and exploring, active learning, creative thinking.", "form", "",
    fields=F4, sections=[("Playing and exploring", 130, True), ("Active learning", 130, True), ("Creating and thinking critically", 130, True), ("What I will do next", "fill", True)])
add(c_, "Support plan: targets and review", "Small targets, strategies and review dates for a child who needs extra help.", "table", "",
    fields=["Child", "Key person", "Plan start date"], header=["Target", "Strategies", "Who helps", "Review date", "Progress"], widths=[3, 4, 2, 1.6, 3], rows=None, row_h=56)
add(c_, "Interests and schemas tracker", "Spot patterns in play so you can plan provision that fits.", "table", "",
    fields=["Group", "Term"], header=["Child", "Interests", "Pattern or schema seen", "Provision to offer"], widths=[1.6, 3, 3.5, 3.5], rows=None, row_h=40)
add(c_, "Parent voice: what we do at home", "A sheet for families to share what their child enjoys and can do at home.", "form", "Send home with the child.",
    fields=["Child", "Date", "Completed by"], sections=[("What I love doing at home", 100, True), ("New things I can do", 100, True), ("Words and songs I enjoy", 100, True), ("Anything you would like us to know", "fill", True)])
add(c_, "Child's voice: all about my day", "Let children show and tell what matters to them.", "form", "Draw or write with a grown-up.",
    fields=["Name", "Date"], sections=[[("My favourite thing here", 190, False), ("My best friend is", 190, False)], [("What I like to play with", 190, False), ("What makes me happy", 190, False)], ("Draw yourself", "fill", False)])
add(c_, "Weekly observation overview", "See at a glance which children you have observed this week.", "table", "",
    fields=["Week beginning", "Practitioner"], header=["Child", "Mon", "Tue", "Wed", "Thu", "Fri", "Area covered"], widths=[2.5, 1, 1, 1, 1, 1, 2.5], rows=None, row_h=30)
add(c_, "Language development notes", "Capture new words, phrases and conversations to share with families.", "table", "",
    fields=["Child", "Key person"], header=["Date", "What the child said", "Context", "Follow-up idea"], widths=[1.2, 4.5, 3, 3], rows=None, row_h=44)

# --- Early years: planning and provision (14)
c_ = "ey-planning"
add(c_, "Weekly plan: seven areas of learning", "Plan across all seven areas for the week.", "table", "",
    fields=["Week beginning", "Theme"], header=["Area of learning", "Mon", "Tue", "Wed", "Thu", "Fri"], widths=[2.4, 2, 2, 2, 2, 2], rows=[[a] for a in AREAS], row_h=54, shade_first=True, land=True)
add(c_, "Continuous provision plan", "List what is out in each area and how adults will join in.", "table", "",
    fields=["Week beginning", "Practitioner"], header=["Area of provision", "Resources out", "Enhancement this week", "Adult role"], widths=[2, 3.5, 3.5, 3],
    rows=[[x] for x in ["Role play", "Small world", "Construction", "Mark making", "Sand", "Water", "Malleable", "Book area", "Outdoors", "Creative"]], row_h=50, shade_first=True)
add(c_, "Adult-led activity plan", "Plan a short adult-led activity: intent, vocabulary, questions and review.", "form", "",
    fields=["Activity", "Date", "Group size", "Adult"], sections=[[("Learning intention", 70, True), ("Area(s) of learning", 70, True)], ("Resources and preparation", 80, True), ("What the adult will do and say", 110, True), [("Key vocabulary", 90, True), ("Open questions to ask", 90, True)], ("How it went and next steps", "fill", True)])
add(c_, "Topic web", "Map out a topic and the ideas that grow from it.", "organiser", "Write the topic in the middle.", type="mindmap", centre="Our topic", fields_list=["Topic", "Term", "Practitioner"])
add(c_, "Enhancements by area of learning", "Plan enhancements to the provision for each area of learning.", "table", "",
    fields=["Theme", "Week beginning"], header=["Area of learning", "Indoors", "Outdoors", "Why we chose it"], widths=[2.4, 4, 4, 3], rows=[[a] for a in AREAS], row_h=60, shade_first=True)
add(c_, "Outdoor learning plan", "Plan a learning experience outdoors, with a space for safety notes.", "form", "",
    fields=["Activity", "Date", "Adult", "Group"], sections=[[("Learning focus", 80, True), ("Resources", 80, True)], ("What children will do", 100, True), ("Safety considerations", 90, True), ("Reflection", "fill", True)], note=EYNOTE)
add(c_, "Small world planner", "Plan small world play linked to a story or interest.", "form", "",
    fields=["Theme", "Week", "Adult"], sections=[("Resources to set up", 100, True), ("Language to model", 100, True), ("Questions to ask", 100, True), ("Child-led ideas to follow up", "fill", True)])
add(c_, "Letter to families", "A friendly letter template to explain this half term's learning.", "form", "Fill in and photocopy.",
    fields=["Date", "To"], sections=[("Dear families,", 130, True), ("What we will be learning", 190, True), ("How you can help at home", 150, True), ("Dates for your diary", "fill", True)])
add(c_, "Newsletter template", "A two-column newsletter layout for your setting.", "form", "",
    fields=["Term", "Date"], sections=[("Welcome", 90, True), [("News", 220, True), ("Dates", 220, True)], ("Learning this month", 120, True), ("Thank you and reminders", "fill", True)])
add(c_, "Home learning ideas sheet", "Simple ideas for families to try at home.", "form", "",
    fields=["Child", "This week's theme"], sections=[("Let's talk about", 100, True), ("Let's make or play", 100, True), ("Let's read, sing or count", 100, True), ("We tried it! (draw or write)", "fill", False)])
add(c_, "Open questions prompt cards", "Six prompt cards to extend children's thinking.", "cards", "Cut out and keep with the adults.",
    items=["What do you notice?", "What could we try next?", "Tell me about what you made.", "What do you think will happen?", "How did you do that?", "What else could we use?"],
    cols=2, rows=3, style="sign", size=24)
add(c_, "Story of the week planner", "Plan a core story across the week with activities in each area.", "table", "",
    fields=["Book", "Week beginning"], header=["Day", "Story focus", "Activity", "Vocabulary", "Resources"], widths=[1.2, 3, 4, 3, 3], rows=[["Monday"], ["Tuesday"], ["Wednesday"], ["Thursday"], ["Friday"]], row_h=72, shade_first=True)
add(c_, "Risk-benefit assessment: activity", "Think through benefits and risks before an activity.", "table", "",
    fields=["Activity", "Date", "Assessor"], header=["What could go wrong?", "Benefit of the activity", "How we reduce the risk", "Who is responsible"], widths=[3, 3, 4, 2], rows=None, row_h=52, note=EYNOTE)
add(c_, "Trip permission slip", "A short permission slip for a trip or visit.", "form", "",
    fields=["Child", "Date of trip"], sections=[("Trip details", 110, True), ("Medical information or needs we should know about", 120, True), ("Emergency contact", 90, True), ("Parent or carer permission and signature", "fill", True)], note=EYNOTE)

# --- Early years: records and checklists (12)
c_ = "ey-records"
add(c_, "Daily register", "A simple daily attendance register.", "table", EYNOTE,
    fields=["Room", "Week beginning"], header=["Child", "Mon in", "Mon out", "Tue in", "Tue out", "Wed in", "Wed out", "Thu in", "Thu out", "Fri in", "Fri out"],
    widths=[2.6] + [1] * 10, rows=None, row_h=26, land=True)
add(c_, "Safer sleep check chart", "Record regular checks on sleeping babies and children.", "table", "Record checks in line with your safer sleep policy.",
    fields=["Room", "Date"], header=["Child", "Time down", "Check 1", "Check 2", "Check 3", "Check 4", "Time up", "Initials"], widths=[2.4, 1.3, 1.1, 1.1, 1.1, 1.1, 1.3, 1.1], rows=None, row_h=34)
add(c_, "Nappy and toileting record", "Keep a clear record of nappy changes and toilet visits.", "table", "",
    fields=["Room", "Date"], header=["Child", "Time", "Wet", "Soiled", "Cream used", "Practitioner"], widths=[2.4, 1.3, 1, 1, 1.6, 2], rows=None, row_h=26)
add(c_, "Meal and snack planner", "Plan the week's meals, snacks and dietary notes.", "table", "",
    fields=["Week beginning", "Cook"], header=["Day", "Breakfast", "Morning snack", "Lunch", "Afternoon snack", "Tea"], widths=[1.4, 2.4, 2.4, 3, 2.4, 2.4],
    rows=[["Monday"], ["Tuesday"], ["Wednesday"], ["Thursday"], ["Friday"]], row_h=70, shade_first=True)
add(c_, "Cleaning and hygiene checklist", "Daily and weekly hygiene tasks to tick off.", "checklist", EYNOTE,
    fields=["Room", "Week beginning", "Checked by"],
    items=["Surfaces wiped and sanitised", "Toys washed or rotated", "Role play clothes checked", "Bins emptied", "Nappy area cleaned", "Toilets cleaned", "Soap and paper towels stocked", "Floors cleaned", "Water tray emptied and refilled", "Sleep area linen changed", "Door handles wiped", "Fridge temperature checked"], cols=2)
add(c_, "Staff rota", "Plan staff on shift for the week.", "table", "",
    fields=["Week beginning", "Manager"], header=["Staff", "Mon", "Tue", "Wed", "Thu", "Fri", "Hours"], widths=[2.5, 1.7, 1.7, 1.7, 1.7, 1.7, 1.2], rows=None, row_h=34)
add(c_, "Daily handover note", "A short note to pass information between shifts or to families.", "form", "",
    fields=["Child", "Date", "Written by"], sections=[("Eating and drinking", 80, True), ("Sleep", 80, True), ("Toileting or nappies", 80, True), ("Play and learning today", 100, True), ("Anything to pass on", "fill", True)])
add(c_, "Parent communication log", "Keep track of conversations with families.", "table", "",
    fields=["Child", "Key person"], header=["Date", "Who", "Topic", "Actions or follow-up"], widths=[1.3, 2, 3.5, 4], rows=None, row_h=40)
add(c_, "Visitors sign-in sheet", "Sign in and out for visitors to your setting.", "table", "",
    fields=["Date"], header=["Name", "Organisation", "Reason for visit", "Time in", "Time out", "Badge no."], widths=[2.5, 2.5, 3, 1.2, 1.2, 1.2], rows=None, row_h=30)
add(c_, "Fire drill log", "Record evacuation drills and learning points.", "table", EYNOTE,
    fields=["Setting"], header=["Date", "Time", "Evacuation time", "Number evacuated", "Issues noticed", "Signed"], widths=[1.4, 1.2, 1.5, 1.5, 4, 1.4], rows=None, row_h=36)
add(c_, "Outdoor area daily check", "Safety walk-round checklist before children use the outdoor space.", "checklist", EYNOTE,
    fields=["Date", "Checked by"], items=["Gates secure", "Fencing intact", "No litter or hazards on the ground", "Climbing equipment checked", "Water play area safe", "Shade available", "Sandpit covered or checked", "Surfaces not slippery", "Plants and hazards checked", "Tools and equipment put away"], cols=2)
add(c_, "Resource and equipment check", "Check toys, furniture and equipment on a regular schedule.", "table", EYNOTE,
    fields=["Room", "Date", "Checked by"], header=["Item or area", "Condition", "Action needed", "Done?"], widths=[3, 2, 4, 1.2], rows=None, row_h=32)

# --- Early years: child activity sheets (26)
c_ = "ey-activities"
add(c_, "Pre-writing patterns: straight lines", "Trace vertical and horizontal lines to build pencil control.", "patterns", "Start at the green dot.", pattern="straight")
add(c_, "Pre-writing patterns: waves and curves", "Trace wavy lines to build pencil control.", "patterns", "Start at the green dot.", pattern="waves")
add(c_, "Pre-writing patterns: zigzags", "Trace zigzag lines of different sizes.", "patterns", "Start at the green dot.", pattern="zigzag")
add(c_, "Pre-writing patterns: loops and spirals", "Trace loops and spirals for flowing hand movements.", "patterns", "Start at the green dot.", pattern="loops")
for sh in ["circle", "square", "triangle", "rectangle"]:
    add(c_, "Trace and draw a " + sh, "Trace a large dotted " + sh + ", then draw your own.", "shape", "", shape=sh)
add(c_, "Shape hunt", "Find circles, squares, triangles and rectangles around the setting.", "shapehunt", "Go on a hunt and draw what you find.")
add(c_, "Number cards 0 to 10", "Large number cards for counting games and displays.", "cards", "Cut along the dotted lines.", items=[str(i) for i in range(0, 11)], cols=2, rows=3, style="text", size=130)
add(c_, "Number cards 11 to 20", "Large number cards from 11 to 20.", "cards", "Cut along the dotted lines.", items=[str(i) for i in range(11, 21)], cols=2, rows=3, style="text", size=120)
add(c_, "Ten frames", "Eight blank ten frames for counting and number bonds.", "tenframes", "Use counters or draw dots.")
add(c_, "Trace the numbers 0 to 4", "Trace each number, then write it yourself.", "numtrace", "", digits=[0, 1, 2, 3, 4])
add(c_, "Trace the numbers 5 to 9", "Trace each number, then write it yourself.", "numtrace", "", digits=[5, 6, 7, 8, 9])
add(c_, "Count the stars 1 to 5", "Count the stars and write how many.", "countsheet", "", counts=[1, 2, 3, 4, 5])
add(c_, "Count the stars 6 to 10", "Count the stars and write how many.", "countsheet", "", counts=[6, 7, 8, 9, 10])
add(c_, "Alphabet cards: capital letters", "Twenty-six large capital letter cards.", "cards", "Cut along the dotted lines.", items=[chr(65 + i) for i in range(26)], cols=2, rows=3, style="text", size=130)
add(c_, "Alphabet cards: lower case letters", "Twenty-six large lower case letter cards.", "cards", "Cut along the dotted lines.", items=[chr(97 + i) for i in range(26)], cols=2, rows=3, style="text", size=150)
add(c_, "Name tracing template", "A blank frame for writing a child's name to trace.", "hwlines", "Write the name in the first line, then trace it.", style="ks1")
add(c_, "Emotion faces cards", "Eight faces to talk about feelings.", "cards", "Cut out and use for circle time.", items=["Happy", "Sad", "Angry", "Surprised", "Scared", "Tired", "Excited", "Calm"], cols=2, rows=4, style="face")
add(c_, "Visual timetable cards", "Pictureless word cards to build a daily routine.", "cards", "Cut out and arrange on a display.", items=["Arrive", "Play", "Snack", "Story", "Outside", "Lunch", "Tidy up", "Home time"], cols=2, rows=4, style="sign", size=28)
add(c_, "Colour cards", "Ten colour cards for matching and naming games.", "cards", "Cut along the dotted lines.", items=list(COLOURS.keys()), cols=2, rows=5, style="colour")
add(c_, "Colour sorting mats", "Two sorting mats for sorting objects by colour.", "table", "Place objects in the right box.", header=["Red", "Blue", "Yellow", "Green"], widths=[1, 1, 1, 1], rows=1, row_h=620)
add(c_, "Birthday chart", "A year of birthdays on one page.", "table", "", header=["Month", "Names and dates"], widths=[2, 9],
    rows=[[m] for m in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]], row_h=52, fields=["Class", "Year"], shade_first=True)
add(c_, "Weather chart", "Record the weather for the week.", "table", "", header=["Day", "Sunny", "Cloudy", "Rainy", "Windy", "Snowy"], widths=[1.6, 1, 1, 1, 1, 1],
    rows=[["Monday"], ["Tuesday"], ["Wednesday"], ["Thursday"], ["Friday"]], row_h=70, fields=["Week beginning"], shade_first=True)
add(c_, "Helper chart", "A simple rota for classroom helpers.", "table", "", header=["Day", "Door monitor", "Lunch monitor", "Tidy-up leader", "Line leader"], widths=[1.4, 2, 2, 2, 2],
    rows=[["Monday"], ["Tuesday"], ["Wednesday"], ["Thursday"], ["Friday"]], row_h=70, fields=["Week beginning"], shade_first=True)

# --- Primary: planning and assessment (22)
c_ = "primary-planning"
add(c_, "Lesson plan: one page", "A clean one-page lesson plan template.", "form", "",
    fields=["Class", "Date", "Subject", "Teacher"], sections=[[("Learning objective", 70, True), ("Success criteria", 70, True)], ("Key vocabulary and resources", 70, True), ("Starter", 80, True), ("Main teaching", 120, True), ("Independent task and support", 100, True), ("Plenary and assessment", "fill", True)])
add(c_, "Lesson plan with success criteria", "Lesson plan with space for 'I can' statements and checks for understanding.", "form", "",
    fields=["Class", "Date", "Subject"], sections=[("Learning objective", 56, True), ("I can... (success criteria)", 90, True), ("Prior learning", 60, True), ("Teaching sequence", 140, True), ("Questions to check understanding", 90, True), ("Adaptations and support", 80, True), ("Reflection", "fill", True)])
add(c_, "Lesson plan: five-part structure", "Hook, input, guided practice, independent practice, review.", "form", "",
    fields=["Class", "Date", "Subject"], sections=[("1. Hook", 80, True), ("2. Input", 100, True), ("3. Guided practice", 100, True), ("4. Independent practice", 100, True), ("5. Review", "fill", True)])
add(c_, "Cover lesson plan", "Everything a cover teacher needs in one page.", "form", "",
    fields=["Class", "Date", "Teacher absent", "Cover teacher"], sections=[[("Timings", 90, True), ("Seating and groups", 90, True)], ("Lesson tasks", 130, True), ("Pupils who need support", 80, True), ("Key routines and behaviour systems", 90, True), ("Notes for the class teacher", "fill", True)])
for subj, extra in [("English", "Vocabulary, grammar and writing focus"), ("Maths", "Fluency, reasoning and problem solving"), ("Science", "Working scientifically and key vocabulary"),
                    ("History", "Chronology, sources and enquiry question"), ("Geography", "Locational knowledge and fieldwork"), ("Computing", "Computational thinking and online safety"),
                    ("Art and design", "Techniques, artists and sketchbook work"), ("Design and technology", "Design, make, evaluate"), ("PE", "Skills, warm-up and safety"),
                    ("RE", "Key question, beliefs and reflection"), ("Music", "Listening, performing and composing"), ("PSHE", "Discussion, scenarios and reflection")]:
    add(c_, "Lesson plan: " + subj, "Lesson plan with prompts for " + extra.lower() + ".", "form", "",
        fields=["Class", "Date", "Teacher"], sections=[("Learning objective", 56, True), ("Prior knowledge", 56, True), (extra, 120, True), ("Activities", 130, True), ("Vocabulary and resources", 70, True), ("Assessment and next steps", "fill", True)])
add(c_, "Weekly planner", "Plan the week's lessons at a glance.", "table", "",
    fields=["Class", "Week beginning"], header=["Time", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], widths=[1.1, 2, 2, 2, 2, 2],
    rows=[["8:45"], ["9:30"], ["10:30"], ["11:15"], ["12:00"], ["1:15"], ["2:15"], ["3:00"]], row_h=48, shade_first=True, land=True)
add(c_, "Medium-term plan", "Plan a unit across several weeks.", "table", "",
    fields=["Subject", "Class", "Unit title"], header=["Week", "Learning focus", "Key knowledge", "Vocabulary", "Assessment"], widths=[1, 3.5, 3.5, 3, 2.5], rows=[[f"Week {i}"] for i in range(1, 9)], row_h=58, shade_first=True)
add(c_, "Behaviour log", "Record behaviour incidents and follow-up.", "table", "",
    fields=["Class", "Term"], header=["Date", "Pupil", "What happened", "Action taken", "Follow-up"], widths=[1.2, 2, 4, 3, 3], rows=None, row_h=42)
add(c_, "Parent meeting notes", "Notes for a meeting with a parent or carer.", "form", "",
    fields=["Pupil", "Date", "Attending"], sections=[("Strengths and progress", 110, True), ("Concerns or questions", 110, True), ("Actions agreed", 100, True), ("Follow-up date and notes", "fill", True)])
add(c_, "Guided reading plan", "Plan a guided reading session with questions.", "form", "",
    fields=["Group", "Text", "Date"], sections=[[("Vocabulary to pre-teach", 90, True), ("Fluency focus", 90, True)], ("Retrieval questions", 90, True), ("Inference questions", 90, True), ("Notes on how each child read", "fill", True)])
add(c_, "Small-group intervention plan", "Plan targeted support for a small group of pupils.", "form", "",
    fields=["Group", "Focus", "Start date"], sections=[("Gaps identified", 90, True), ("Planned sessions", 140, True), ("How we will measure progress", 90, True), ("Review notes", "fill", True)])

# --- Primary: maths and literacy tools (26)
c_ = "primary-maths-literacy"
add(c_, "Number line 0 to 10", "Five large number lines from 0 to 10.", "numline", "", start=0, end=10, label_step=1, lines=5)
add(c_, "Number line 0 to 20", "Five number lines from 0 to 20.", "numline", "", start=0, end=20, label_step=1, lines=5)
add(c_, "Number line 0 to 100", "Number lines with every 10 labelled.", "numline", "", start=0, end=100, label_step=10, lines=5)
add(c_, "Number line -10 to 10", "Number lines with negative numbers.", "numline", "", start=-10, end=10, label_step=1, lines=5)
add(c_, "Hundred square", "A hundred square from 1 to 100.", "hundred", "", **{"from": 1})
add(c_, "Blank hundred square", "A blank hundred grid to fill in.", "hundred", "", blank=True, fields=["Name", "Date"])
add(c_, "Multiplication square 1 to 12", "A full 12 by 12 multiplication grid.", "multgrid", "")
add(c_, "Blank multiplication grid", "Fill in the products for a 12 by 12 grid.", "multgrid", "", blank=True, fields=["Name", "Date"])
add(c_, "Place value chart: hundreds, tens, ones", "A large place value chart for three-digit numbers.", "table", "", fields=["Name", "Date"],
    header=["Hundreds", "Tens", "Ones"], widths=[1, 1, 1], rows=6, row_h=100)
add(c_, "Place value chart: to thousands", "A place value chart for four-digit numbers.", "table", "", fields=["Name", "Date"],
    header=["Thousands", "Hundreds", "Tens", "Ones"], widths=[1, 1, 1, 1], rows=6, row_h=100)
add(c_, "Fraction wall", "Twelve rows of fractions from one whole to twelfths.", "fracwall", "")
add(c_, "Bar model template", "Six bar models for word problems.", "partwhole", "", model="bar")
add(c_, "Part-whole model template", "Six part-whole models for number work.", "partwhole", "", model="circle")
add(c_, "Number bonds to 10", "Practise number bonds with number sentences.", "bonds", "", total=10)
add(c_, "Number bonds to 20", "Practise number bonds to 20.", "bonds", "", total=20)
add(c_, "Clock faces", "Four analogue clock faces for telling the time.", "clocks", "", numbers=True)
add(c_, "Blank clock faces", "Four clock faces without numbers for children to complete.", "clocks", "", numbers=False)
add(c_, "Squared paper", "1 cm squared paper for graphs and arrays.", "paper", "", paper="squared", step=28.35)
add(c_, "Small squared paper", "5 mm squared paper for detailed work.", "paper", "", paper="squared", step=14.17)
add(c_, "Dot paper", "Square dot paper for symmetry and shapes.", "paper", "", paper="dots")
add(c_, "Isometric dot paper", "Triangular dot paper for 3D drawing.", "paper", "", paper="iso")
add(c_, "Column addition frame", "Nine grids for column addition.", "column", "", op="+")
add(c_, "Column subtraction frame", "Nine grids for column subtraction.", "column", "", op="-")
add(c_, "Handwriting lines: four-line guide", "Four-line handwriting guides for early writing.", "hwlines", "", style="ks1")
add(c_, "Writing lines", "Plain ruled lines for writing.", "hwlines", "", style="ks2")
add(c_, "Spelling practice grid", "Look, cover, write, check practice grid.", "spelling", "")

# --- Graphic organisers and study skills (14)
c_ = "organisers"
add(c_, "KWL chart", "Record what you know, want to know and learned.", "organiser", "", type="kwl")
add(c_, "Venn diagram: two circles", "Compare and contrast two ideas.", "organiser", "", type="venn2")
add(c_, "Venn diagram: three circles", "Compare three ideas.", "organiser", "", type="venn3")
add(c_, "Mind map", "A mind map with a central idea and six branches.", "organiser", "", type="mindmap", centre="Main idea")
add(c_, "Timeline", "Put events in order on a timeline.", "organiser", "", type="timeline", land=True)
add(c_, "Frayer model", "Define a word with characteristics, examples and non-examples.", "organiser", "", type="frayer")
add(c_, "Cause and effect chart", "Link causes to their effects.", "organiser", "", type="cause_effect", rows=4)
add(c_, "T-chart", "Two columns to compare or sort.", "organiser", "", type="tchart", labels=["Heading A", "Heading B"])
add(c_, "Flow chart", "Plan a process or sequence.", "organiser", "", type="flowchart")
add(c_, "Four-step sequence", "First, next, then, finally.", "organiser", "", type="sequence")
add(c_, "Story mountain", "Plan a story: opening, build-up, problem, resolution, ending.", "organiser", "", type="mountain")
add(c_, "Exit tickets", "Eight exit tickets to check understanding.", "cards", "Cut along the dotted lines.", items=[""] * 8, cols=2, rows=4, style="ticket")
add(c_, "Two stars and a wish", "Peer or self feedback with two positives and one wish.", "organiser", "", type="stars")
add(c_, "Self-assessment traffic lights", "Pupils rate their confidence on 'I can' statements.", "organiser", "", type="lights")

# --- Secondary teaching tools (18)
c_ = "secondary"
add(c_, "Lesson plan: secondary", "A one-page secondary lesson plan.", "form", "",
    fields=["Class", "Date", "Period", "Teacher"], sections=[[("Learning objective", 70, True), ("Success criteria", 70, True)], ("Starter and retrieval", 80, True), ("Teaching and modelling", 120, True), ("Practice and checking understanding", 110, True), ("Plenary and homework", "fill", True)])
add(c_, "Scheme of work: unit planner", "Plan a whole unit lesson by lesson.", "table", "",
    fields=["Subject", "Year group", "Unit"], header=["Lesson", "Learning objective", "Key content", "Assessment", "Notes"], widths=[1, 3.5, 3.5, 2.5, 2.5], rows=[[f"{i}"] for i in range(1, 11)], row_h=52, shade_first=True)
add(c_, "Seating plan: rows", "Rows of desks facing the front.", "seating", "", style="rows", cols=5, rows=6)
add(c_, "Seating plan: groups", "Six tables of six.", "seating", "", style="groups")
add(c_, "Seating plan: horseshoe", "A horseshoe layout for discussion.", "seating", "", style="horseshoe")
add(c_, "Marking codes key", "Create your own marking code key for pupils.", "table", "Fill in your codes and what they mean.",
    header=["Code", "Meaning", "What the pupil should do"], widths=[1.4, 4, 5], rows=14, row_h=36)
add(c_, "Feedback sheet: what went well and even better if", "A feedback and improvement sheet.", "form", "",
    fields=["Pupil", "Task", "Date"], sections=[("What went well", 120, True), ("Even better if", 120, True), ("My response and improvement task", "fill", True)])
add(c_, "Improvement task planner", "Plan time for pupils to respond to feedback.", "table", "",
    fields=["Class", "Task"], header=["Pupil", "Targeted improvement", "Completed?", "Teacher check"], widths=[2.5, 5, 1.5, 2.5], rows=None, row_h=34)
add(c_, "Revision timetable", "A weekly revision planner.", "table", "",
    fields=["Name", "Week beginning"], header=["Time", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], widths=[1.4, 2, 2, 2, 2, 2, 2, 2], rows=[[t] for t in ["Before school", "Morning", "Lunchtime", "After school", "Early evening", "Evening"]], row_h=70, shade_first=True, land=True)
add(c_, "Exam countdown planner", "Plan revision topic by topic before the exams.", "table", "",
    fields=["Name", "Subject"], header=["Topic", "Confidence 1 to 5", "Revision done", "Date", "Check complete?"], widths=[4, 1.8, 2.5, 1.5, 1.8], rows=None, row_h=34)
add(c_, "Cornell notes page", "Cue column, notes column and summary box.", "form", "",
    fields=["Name", "Subject", "Date"], sections=[[("Cues and questions", 480, False), ("Notes", 480, True)], ("Summary", "fill", True)])
add(c_, "Retrieval practice grid", "Low-stakes quizzing across topics.", "table", "",
    fields=["Name", "Date"], header=["Question", "My answer", "Correct answer", "Got it?"], widths=[4, 4, 4, 1.4], rows=None, row_h=44)
add(c_, "Knowledge organiser template", "Summarise one topic on one page.", "form", "",
    fields=["Subject", "Topic", "Year"], sections=[[("Key facts", 230, True), ("Key vocabulary", 230, True)], [("Key people or ideas", 180, True), ("Timeline or process", 180, True)], ("Check yourself questions", "fill", True)])
add(c_, "Class data tracker", "Track assessment marks for a class.", "table", "",
    fields=["Class", "Subject"], header=["Pupil", "Test 1", "Test 2", "Test 3", "Test 4", "Target", "Notes"], widths=[3, 1.2, 1.2, 1.2, 1.2, 1.4, 3], rows=None, row_h=26, land=True)
add(c_, "Parents' evening notes", "Quick notes for each appointment.", "table", "",
    fields=["Class", "Date"], header=["Time", "Pupil", "Strengths", "Next steps", "Actions"], widths=[1.2, 2, 3.5, 3.5, 3], rows=None, row_h=44)
add(c_, "Homework planner", "A weekly homework planner for pupils.", "table", "",
    fields=["Name", "Week beginning"], header=["Day", "Subject", "Task", "Due", "Done?"], widths=[1.4, 2, 5, 1.4, 1.2], rows=None, row_h=36)
add(c_, "Behaviour reflection form", "A restorative reflection sheet for pupils.", "form", "",
    fields=["Name", "Date", "Teacher"], sections=[("What happened?", 100, True), ("Who has been affected?", 100, True), ("What could I do differently?", 100, True), ("How will I put things right?", "fill", True)])

# --- Student teacher and early career toolkit (28)
c_ = "trainee"
add(c_, "Weekly placement reflection", "A weekly reflection for your placement.", "form", "",
    fields=["Name", "Week", "School"], sections=[("What went well this week", 110, True), ("What I found challenging", 110, True), ("What I learned about pupils", 100, True), ("Targets for next week", "fill", True)])
add(c_, "Lesson observation form", "For a mentor to record strengths and targets after observing a lesson.", "form", "",
    fields=["Trainee", "Observer", "Date", "Class"], sections=[("Lesson and context", 70, True), ("Strengths seen", 130, True), ("Areas to develop", 130, True), ("Agreed targets", "fill", True)])
add(c_, "Post-lesson reflection", "Reflect quickly after teaching a lesson.", "form", "",
    fields=["Trainee", "Date", "Class"], sections=[("What did pupils learn?", 100, True), ("How do I know?", 100, True), ("What would I change?", 100, True), ("One thing to try next time", "fill", True)])
add(c_, "Teachers' Standards self-assessment", "Rate your confidence against the eight Teachers' Standards headings.", "table", "Check the wording against the current Teachers' Standards.",
    fields=["Name", "Date"], header=["Standard heading", "Confidence 1 to 5", "Evidence", "Next step"], widths=[5, 1.4, 3.5, 3], rows=[[s] for s in STANDARDS], row_h=62, shade_first=True)
add(c_, "Placement diary page", "A daily page for your placement diary.", "form", "",
    fields=["Date", "Class"], sections=[("What I did today", 140, True), ("What I noticed", 120, True), ("Questions for my mentor", 100, True), ("Targets", "fill", True)])
add(c_, "Mentor meeting agenda", "An agenda to plan a mentor meeting.", "form", "",
    fields=["Trainee", "Mentor", "Date"], sections=[("What I want to talk about", 100, True), ("Observations to discuss", 100, True), ("Progress against targets", 100, True), ("Support needed", "fill", True)])
add(c_, "Mentor meeting record", "Record the discussion and agreed actions.", "table", "",
    fields=["Trainee", "Mentor"], header=["Date", "Discussed", "Actions", "Who", "Review date"], widths=[1.3, 4, 4, 1.5, 1.5], rows=None, row_h=52)
add(c_, "Evidence log", "Keep track of evidence for each Teachers' Standards heading.", "table", "",
    fields=["Name", "Placement"], header=["Date", "Evidence", "Standard(s)", "Stored where?"], widths=[1.3, 4.5, 2, 2.5], rows=None, row_h=38)
add(c_, "Subject knowledge audit", "Rate your knowledge across a subject.", "table", "",
    fields=["Name", "Subject"], header=["Topic", "Confident", "Some gaps", "Need to study", "Plan"], widths=[4, 1.2, 1.2, 1.4, 3.5], rows=None, row_h=32)
add(c_, "Behaviour management reflective log", "Reflect on strategies that worked.", "table", "",
    fields=["Name", "Class"], header=["Date", "Situation", "What I did", "How it went", "Try next time"], widths=[1.2, 3, 3, 2.5, 2.5], rows=None, row_h=46)
add(c_, "Pupil case study template", "Structure for a case study of one pupil.", "form", "Keep the pupil anonymous.",
    fields=["Pupil (initials only)", "Year group", "Date"], sections=[("Background and context", 100, True), ("Strengths and interests", 90, True), ("Barriers to learning", 90, True), ("Strategies I tried", 100, True), ("Impact and reflection", "fill", True)])
add(c_, "Action research planner", "Plan a small piece of classroom research.", "form", "",
    fields=["Name", "Date"], sections=[("Research question", 70, True), ("Why this matters", 80, True), ("What I will do", 100, True), ("How I will collect evidence", 100, True), ("What I found", "fill", True)])
add(c_, "Professional development plan", "Set SMART goals for your development.", "table", "",
    fields=["Name", "Term"], header=["Goal", "Actions", "Support needed", "Success measure", "Review"], widths=[3, 4, 2.5, 3, 1.5], rows=None, row_h=64)
add(c_, "Interview preparation sheet", "Plan answers for teaching interviews.", "form", "",
    fields=["School", "Date", "Post"], sections=[("Why I want to teach here", 90, True), ("A lesson I taught and what I learned", 110, True), ("How I manage behaviour", 90, True), ("Safeguarding: what I would do", 90, True), ("Questions I will ask them", "fill", True)])
add(c_, "First-week checklist", "Get ready for your first week in school.", "checklist", "",
    fields=["Name", "School"], items=["Meet my mentor", "Get ID badge and keys", "Read safeguarding policy", "Find out who the safeguarding lead is", "Read the behaviour policy", "Learn fire exits and routines", "Get class lists and seating plans", "Learn pupils' names", "Ask for timetable", "Find resources and photocopying", "Meet the SENCo", "Plan first lessons"], cols=2)
add(c_, "Classroom setup checklist", "Set up your classroom for the first day.", "checklist", "",
    fields=["Name", "Class"], items=["Name labels and pegs", "Seating plan", "Display boards", "Behaviour system visible", "Resources organised", "Books out", "Whiteboard ready", "Register ready", "Visual timetable", "Emergency information", "Water and snack arrangements", "Welcome message"], cols=2)
add(c_, "Lesson plan linked to Teachers' Standards", "A lesson plan with space to link to the standards.", "form", "",
    fields=["Class", "Date", "Subject"], sections=[[("Learning objective", 70, True), ("Standards addressed", 70, True)], ("Teaching sequence", 150, True), ("Assessment", 90, True), ("Evaluation", "fill", True)])
add(c_, "ECT induction meeting log", "Record induction meetings during your early career years.", "table", "",
    fields=["Name", "School", "Mentor"], header=["Date", "Focus", "Evidence", "Next steps"], widths=[1.3, 3.5, 4, 3.5], rows=None, row_h=52)
add(c_, "ECT weekly planner", "A weekly planner for early career teachers.", "table", "",
    fields=["Name", "Week beginning"], header=["Day", "Lessons", "Marking and planning", "Meetings", "Personal time"], widths=[1.4, 3, 3, 2.5, 2.5], rows=[["Monday"], ["Tuesday"], ["Wednesday"], ["Thursday"], ["Friday"]], row_h=70, shade_first=True)
add(c_, "Workload planner", "Plan your week to protect your time.", "table", "",
    fields=["Name", "Week beginning"], header=["Task", "Time needed", "Day", "Done?"], widths=[5, 1.6, 1.6, 1.2], rows=None, row_h=34)
add(c_, "Wellbeing check-in", "A weekly self check-in.", "form", "",
    fields=["Name", "Date"], sections=[("How am I feeling this week (1 to 10)?", 70, True), ("What gave me energy?", 90, True), ("What drained me?", 90, True), ("One thing I will do to look after myself", "fill", True)])
add(c_, "Assignment planner", "Plan assignment work back from the deadline.", "table", "",
    fields=["Name", "Assignment", "Deadline"], header=["Task", "Target date", "Done?", "Notes"], widths=[5, 1.8, 1.2, 4], rows=None, row_h=34)
add(c_, "Research reading log", "Log what you read and what it means for your practice.", "table", "",
    fields=["Name"], header=["Source", "Key idea", "Link to my practice", "Date"], widths=[3.5, 4, 4, 1.4], rows=None, row_h=44)
add(c_, "Source evaluation grid", "Check how reliable a source is.", "table", "",
    fields=["Source", "Date"], header=["Question", "Notes", "Score 1 to 5"], widths=[4, 6, 1.6],
    rows=[["Who wrote it and why?"], ["Is it up to date?"], ["Is it based on evidence?"], ["Is it balanced?"], ["Can I check it elsewhere?"], ["How useful is it for me?"]], row_h=70, shade_first=True)
add(c_, "Essay planning sheet", "Plan an academic essay.", "form", "",
    fields=["Name", "Title", "Word count"], sections=[("My argument in one sentence", 70, True), ("Introduction", 80, True), ("Main point 1 and evidence", 100, True), ("Main point 2 and evidence", 100, True), ("Main point 3 and evidence", 100, True), ("Conclusion", "fill", True)])
add(c_, "Reference list tracker", "Keep a tidy list of the sources you use.", "table", "",
    fields=["Name", "Assignment"], header=["Author", "Year", "Title", "Publisher or website", "Used in"], widths=[2.5, 1, 4, 3.5, 1.6], rows=None, row_h=32)
add(c_, "Placement contacts sheet", "Keep key contacts in one place.", "table", "",
    fields=["Name", "School"], header=["Role", "Name", "Contact", "Notes"], widths=[3, 3, 3, 3], rows=[["Mentor"], ["Class teacher"], ["Safeguarding lead"], ["SENCo"], ["Headteacher"], ["University tutor"], ["School office"]], row_h=50, shade_first=True)
add(c_, "Safeguarding quick card", "Fill in the key names and steps at your placement school.", "form", "Always follow the school's own safeguarding policy.",
    fields=["Name", "School"], sections=[("Designated safeguarding lead (name and number)", 70, True), ("Deputy lead", 70, True), ("Where to find the safeguarding policy", 70, True), ("What I do if a pupil tells me something", 100, True), ("Notes", "fill", True)])

# --- Display, rewards and certificates (20)
c_ = "display"
for ttl, line in [("Star of the Week", "for being a star this week."), ("Super Reader", "for brilliant reading."), ("Kind Friend", "for being kind to others."), ("Maths Star", "for great work in maths."),
                  ("Great Effort", "for working so hard."), ("Brilliant Writer", "for fantastic writing."), ("Super Scientist", "for curious thinking in science."), ("Great Listener", "for listening so well."),
                  ("Headteacher's Award", "for outstanding achievement."), ("Certificate of Achievement", "")]:
    add(c_, "Certificate: " + ttl, "A printable " + ttl.lower() + " certificate.", "certificate", "", land=True, heading=ttl, line=line)
add(c_, "Sticker reward chart: 10 stars", "A ten-star reward chart.", "reward", "", cols=5, rows=2, shape="star")
add(c_, "Sticker reward chart: 20 stars", "A twenty-star reward chart.", "reward", "", cols=5, rows=4, shape="star")
add(c_, "Weekly behaviour chart", "A Monday to Friday chart for positive choices.", "reward", "", cols=3, rows=5, shape="circle", row_labels=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
add(c_, "Class rules poster", "A poster with space for your class rules.", "form", "",
    sections=[("Our class rules", 70, False), ("Rule 1", 100, True), ("Rule 2", 100, True), ("Rule 3", 100, True), ("Rule 4", 100, True), ("Rule 5", "fill", True)])
add(c_, "Door signs", "Six door and area signs.", "cards", "Cut out and laminate.", items=["Welcome", "Quiet please", "Reading corner", "Come in", "Please knock", "Tidy up time"], cols=2, rows=3, style="sign", size=36)
add(c_, "Peg and drawer labels", "Thirty-six blank labels for pegs and drawers.", "cards", "Write names on each label.", items=[""] * 36, cols=3, rows=12, style="label")
add(c_, "School year planner 2026 to 2027", "A year-at-a-glance planner, September 2026 to August 2027.", "cal_year", "", land=True, year=2026)
add(c_, "Monthly planner", "A blank monthly planner grid.", "cal_month", "", land=True)

# ===================== Early years expansion =====================
CUT = "Cut along the dotted lines."

# --- Letters, sounds and words
c_ = "ey-literacy"
add(c_, "Single letter sound cards", "Twenty-six large lower case letter cards for sound games and displays.", "cards", CUT,
    items=list("satpinmdgockeurhbfljvwxyzq"), cols=2, rows=3, style="text", size=150)
add(c_, "Digraph and trigraph cards", "Large cards for common letter pairs and groups, such as sh, ch, ai and igh.", "cards", CUT,
    items=["sh", "ch", "th", "ng", "ai", "ee", "igh", "oa", "oo", "ar", "or", "ur", "ow", "oi", "ear", "air", "ure", "er"], cols=2, rows=3, style="text", size=130)
add(c_, "Common word cards", "Eighteen high-frequency words for reading and matching games.", "cards", CUT,
    items=["the", "to", "I", "no", "go", "into", "he", "she", "we", "me", "be", "was", "you", "they", "all", "are", "my", "her"], cols=2, rows=3, style="text", size=100)
add(c_, "Simple word cards: cat, dog, sun", "Twelve simple three-letter words to sound out and blend.", "cards", CUT,
    items=["cat", "dog", "sun", "pen", "sit", "hop", "bus", "mug", "red", "bed", "pig", "hat"], cols=2, rows=3, style="text", size=110)
for i, grp in enumerate([list("abcde"), list("fghij"), list("klmno"), list("pqrst"), list("uvwxyz")], 1):
    add(c_, "Letter formation: %s to %s" % (grp[0], grp[-1]), "Trace each lower case letter, then write it yourself.", "numtrace", "", digits=grp)
add(c_, "Reading record", "A simple record of books read in the setting and at home.", "table", "",
    fields=["Child", "Key person"], header=["Date", "Book", "Read with", "Comments", "Initials"], widths=[1.3, 3.5, 2, 4, 1.2], rows=None, row_h=36)
add(c_, "Sounds tracker", "Record which letters and sounds a child knows and the next ones to teach.", "table", "Use alongside your own phonics programme.",
    fields=["Child", "Key person"], header=["Date checked", "Sounds known so far", "Sounds to practise", "Next steps"], widths=[1.5, 4, 3.5, 3.5], rows=None, row_h=46)
add(c_, "Reading bookmarks", "Four bookmarks for children to fill in and keep.", "cards", "Cut out along the dotted lines.",
    items=["Title|Author|Started|Finished"] * 4, cols=4, rows=1, style="bookmark")
add(c_, "Draw and write", "A picture box with writing lines for early writers.", "form", "",
    fields=["Name", "Date"], sections=[("My picture", 330, False), ("My writing", "fill", True)])
add(c_, "Word wall cards", "Eighteen blank cards to build your own word wall.", "cards", "Write a word on each card.",
    items=[""] * 18, cols=3, rows=6, style="label", size=20)
add(c_, "Mark-making prompt cards", "Eight prompts to spark drawing and early writing.", "cards", CUT,
    items=["Draw a spiral", "Make big circles", "Write your name", "Draw a rainbow", "Make zigzags", "Draw a house", "Draw your family", "Make a map"], cols=2, rows=4, style="sign", size=26,
    areas=["literacy", "physical", "expressive-arts"])

# --- Early maths
c_ = "ey-maths"
add(c_, "Dot pattern cards 1 to 10", "Dot patterns for recognising small amounts at a glance.", "cards", CUT,
    items=[str(i) for i in range(1, 11)], cols=2, rows=5, style="dots", areas=["mathematics"])
add(c_, "Shape name cards", "Eight shape names for matching and display.", "cards", CUT,
    items=["circle", "square", "triangle", "rectangle", "oval", "star", "heart", "hexagon"], cols=2, rows=4, style="sign", size=36)
add(c_, "Days of the week cards", "Seven day cards for calendar time.", "cards", CUT,
    items=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], cols=2, rows=4, style="sign", size=34)
add(c_, "Months of the year cards", "Twelve month cards for calendar time.", "cards", CUT,
    items=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], cols=2, rows=6, style="sign", size=26)
add(c_, "Number word cards zero to ten", "Number words to match with numerals.", "cards", CUT,
    items=["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"], cols=2, rows=6, style="sign", size=30)
add(c_, "Position word cards", "Words for where things are: in, on, under and more.", "cards", CUT,
    items=["in", "on", "under", "over", "behind", "in front of", "next to", "between"], cols=2, rows=4, style="sign", size=34)
add(c_, "Size and measure word cards", "Words for comparing: big, small, long, short, heavy, light.", "cards", CUT,
    items=["big", "small", "long", "short", "heavy", "light", "full", "empty"], cols=2, rows=4, style="sign", size=36)
add(c_, "Open maths question cards", "Six questions to deepen thinking during maths play.", "cards", CUT,
    items=["How many ways can you make 5?", "Can you find something longer than your hand?", "What comes next? Make a pattern.", "How many can you hold in one hand?", "Which is heavier? How do you know?", "Can you share these equally?"],
    cols=2, rows=3, style="sign", size=20, areas=["mathematics", "communication"])
add(c_, "Measuring record", "Record what children find when they compare lengths and weights.", "table", "",
    fields=["Child", "Date"], header=["Object", "Longer or shorter", "Heavier or lighter", "Notes"], widths=[3, 2.5, 2.5, 4], rows=None, row_h=40)
add(c_, "Number hunt checklist", "Hunt for the numbers 1 to 10 and tick them off.", "checklist", "",
    fields=["Name", "Date"], items=["Number %d" % i for i in range(1, 11)], cols=2)
add(c_, "Counting record", "Note what was counted and how many.", "table", "",
    fields=["Child", "Date"], header=["Date", "What we counted", "How many", "Notes"], widths=[1.3, 4, 1.6, 4], rows=None, row_h=40)

# --- Role play and provision
c_ = "ey-roleplay"
for ttl, words in [
    ("Café", ["Menu", "Open", "Closed", "Table", "Please pay here", "Welcome"]),
    ("Shop", ["Open", "Closed", "Sale", "Please pay here", "Basket", "Welcome"]),
    ("Vet", ["Vet", "Reception", "Waiting room", "Open", "Closed", "Please wait here"]),
    ("Doctor's surgery", ["Reception", "Waiting room", "Appointments", "Open", "Closed", "Please wait here"]),
    ("Post office", ["Post office", "Stamps", "Letters", "Parcels", "Open", "Closed"]),
    ("Garden centre", ["Garden centre", "Plants", "Seeds", "Open", "Closed", "Pay here"]),
    ("Builders' yard", ["Builders", "Hard hats on", "Bricks", "Open", "Closed", "Please wait here"]),
    ("Space station", ["Space station", "Mission control", "Rocket launch", "Countdown", "Astronauts only", "Welcome aboard"]),
]:
    add(c_, "Role play signs: " + ttl, "Six signs to set up a " + ttl.lower() + " role play area.", "cards", "Cut out and laminate if you can.",
        items=words, cols=2, rows=3, style="sign", size=30, areas=["understanding-world", "communication", "literacy"])
add(c_, "Provision area labels", "Ten labels for the areas of your continuous provision.", "cards", "Cut out and laminate if you can.",
    items=["Mark making", "Small world", "Construction", "Sand", "Water", "Role play", "Book corner", "Creative area", "Outdoors", "Malleable"], cols=2, rows=5, style="sign", size=28,
    areas=["expressive-arts", "understanding-world", "physical"])

# --- Topics and seasons
c_ = "ey-topics"
TOPICS = [
    ("Minibeasts", ["ladybird", "snail", "worm", "butterfly", "spider", "bee", "caterpillar", "ant"]),
    ("Growing", ["seed", "soil", "water", "sun", "roots", "shoot", "flower", "leaf"]),
    ("Transport", ["car", "bus", "train", "aeroplane", "boat", "bicycle", "lorry", "helicopter"]),
    ("People who help us", ["doctor", "nurse", "teacher", "firefighter", "police officer", "dentist", "vet", "postal worker"]),
    ("Under the sea", ["fish", "shark", "whale", "octopus", "crab", "turtle", "starfish", "jellyfish"]),
    ("Space", ["rocket", "planet", "star", "moon", "sun", "astronaut", "comet", "telescope"]),
    ("Dinosaurs", ["dinosaur", "fossil", "egg", "tail", "claw", "volcano", "swamp", "footprint"]),
    ("Farm", ["tractor", "barn", "cow", "sheep", "pig", "hen", "field", "farmer"]),
    ("Wild animals", ["lion", "monkey", "snake", "parrot", "elephant", "tiger", "giraffe", "zebra"]),
    ("My family and home", ["grown-up", "baby", "brother", "sister", "grandparent", "friend", "pet", "home"]),
]
for name, words in TOPICS:
    add(c_, "Topic web: " + name, "Plan a " + name.lower() + " topic from children's ideas and interests.", "organiser", "Write ideas around the centre.",
        type="mindmap", centre=name, fields_list=["Topic", "Term", "Practitioner"], areas=["understanding-world"])
    add(c_, "Vocabulary cards: " + name, "Eight key words for a " + name.lower() + " topic.", "cards", CUT,
        items=words, cols=2, rows=4, style="sign", size=34, areas=["communication", "understanding-world"])
SEASONS = [
    ("Autumn", ["leaf", "conker", "acorn", "hedgehog", "rain", "wind", "pumpkin", "scarf"], ["a red leaf", "a yellow leaf", "an acorn", "a conker case", "a feather", "a spider's web", "a puddle", "a seed"]),
    ("Winter", ["snow", "ice", "frost", "coat", "gloves", "hat", "snowman", "icicle"], ["frost on a window or plant", "an icy puddle", "a bare tree", "a bird", "your breath in the cold air", "a hat", "an evergreen tree", "a footprint"]),
    ("Spring", ["seed", "blossom", "lamb", "chick", "rainbow", "puddle", "daffodil", "nest"], ["a new shoot", "blossom", "a bud", "a bird's nest from a distance", "a worm", "a bee", "a rainbow", "a puddle"]),
    ("Summer", ["sun", "sun hat", "ice cream", "beach", "picnic", "shade", "bee", "sandcastle"], ["a butterfly", "a bee", "a flower", "a shady spot", "a cloud shape", "a ladybird", "something green", "something that grows"]),
]
for name, words, hunt in SEASONS:
    add(c_, "Season web: " + name, "Plan " + name.lower() + " learning from what children notice.", "organiser", "Write ideas around the centre.",
        type="mindmap", centre=name, fields_list=["Season", "Year", "Practitioner"], areas=["understanding-world"])
    add(c_, "Season vocabulary cards: " + name, "Eight " + name.lower() + " words to talk about and display.", "cards", CUT,
        items=words, cols=2, rows=4, style="sign", size=34, areas=["communication", "understanding-world"])
    add(c_, "Nature hunt: " + name, "A " + name.lower() + " walk checklist. Look and tick. Do not pick or eat anything.", "checklist", "Go with an adult. Look, do not pick or eat.",
        fields=["Name", "Date"], items=hunt, cols=1, areas=["understanding-world", "physical"])

print("Resources defined:", len(SPECS))
assert len(SPECS) == 267, "expected 267 resources, found %d" % len(SPECS)


# ---------------------------------------------------------------- build
def build():
    os.makedirs(OUT, exist_ok=True)
    out = []
    counters = {}
    for s in SPECS:
        cat = s["cat"]
        counters[cat] = counters.get(cat, 0) + 1
        folder = os.path.join(OUT, "resources", cat)
        os.makedirs(folder, exist_ok=True)
        fname = "%02d-%s.pdf" % (counters[cat], slug(s["title"]))
        path = os.path.join(folder, fname)
        d = Doc(path, s["title"], s["sub"], s["land"])
        if s["kind"] == "certificate":
            KINDS[s["kind"]](d, s["p"])
        else:
            KINDS[s["kind"]](d, s["p"])
        d.save()
        name, roles, phases = CATS[cat]
        out.append({
            "id": cat + "-" + fname[:-4], "title": s["title"], "desc": s["desc"], "cat": cat, "catName": name,
            "roles": roles, "phases": phases, "file": "resources/%s/%s" % (cat, fname), "pages": d.page_no,
            "land": s["land"], "areas": s["areas"] if s["areas"] is not None else infer_areas(s["title"], cat),
        })
    with open(os.path.join(OUT, "resources.json"), "w") as f:
        json.dump({"brand": BRAND, "cats": {k: v[0] for k, v in CATS.items()}, "areaNames": AREA_NAMES, "items": out}, f, indent=1)
    print("Built", len(out), "PDFs in", OUT)


if __name__ == "__main__":
    build()
