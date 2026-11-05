#!/usr/bin/env python3
"""Make PNG previews of printable PDFs.

  python3 make_previews.py            # previews for every item in resources.json that has none yet
  python3 make_previews.py --all      # redo every preview

Needs 'pdftoppm' (from poppler: "brew install poppler" on Mac, "apt install poppler-utils" on Linux).
Previews go in previews/<category>/<name>-<page>.png and resources.json gets a "preview" entry.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "resources.json")
DPI = 110


def render(pdf_path, out_base):
    """Render every page of pdf_path to out_base-1.png, out_base-2.png ... Returns the page count."""
    if not shutil.which("pdftoppm"):
        raise RuntimeError("pdftoppm not found. Install poppler to make previews.")
    os.makedirs(os.path.dirname(out_base), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-png", "-r", str(DPI), pdf_path, os.path.join(tmp, "p")], check=True)
        files = sorted(f for f in os.listdir(tmp) if f.endswith(".png"))
        for i, f in enumerate(files, 1):
            src = os.path.join(tmp, f)
            dst = "%s-%d.png" % (out_base, i)
            try:
                from PIL import Image
                im = Image.open(src).convert("RGB").quantize(colors=96, method=Image.Quantize.MEDIANCUT)
                im.save(dst, optimize=True)
            except Exception:
                shutil.copyfile(src, dst)
    return len(files)


def main():
    redo = "--all" in sys.argv
    with open(JSON_PATH) as f:
        data = json.load(f)
    done = 0
    for it in data["items"]:
        if it.get("preview") and not redo:
            continue
        pdf = os.path.join(HERE, it["file"])
        rel = it["file"].replace("resources/", "previews/", 1)[:-4]
        n = render(pdf, os.path.join(HERE, rel))
        it["preview"] = rel
        it["pages"] = n
        done += 1
    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=1)
    print("Made previews for %d items." % done)


if __name__ == "__main__":
    main()
