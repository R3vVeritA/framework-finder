#!/usr/bin/env python3
"""Add a new printable PDF to the site's library.

Run this from the site folder (the one that holds printables.html and resources.json):

  python3 add_resource.py my-sheet.pdf "Sheet title" "One-sentence description" \
      --cat ey-activities --roles nursery,teacher --phases early,primary

--cat      folder and category id. Existing ones: see the list printed with --list.
           Use a new id (e.g. "phonics") to create a new category, and add --cat-name "Phonics".
--roles    any of: student, teacher, nursery (comma separated)
--phases   any of: early, primary, secondary (comma separated)
--landscape  add this flag if the PDF is landscape

The script copies the PDF into resources/<cat>/, counts its pages if the 'pypdf'
package is installed (otherwise it records 1), and adds it to resources.json with
today's date so it shows a "New" tag for 30 days. Re-upload the site folder afterwards.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "resources.json")
ROLES = {"student", "teacher", "nursery"}
PHASES = {"early", "primary", "secondary"}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def main():
    ap = argparse.ArgumentParser(description="Add a PDF to the Framework Finder printables library.")
    ap.add_argument("pdf", nargs="?")
    ap.add_argument("title", nargs="?")
    ap.add_argument("desc", nargs="?")
    ap.add_argument("--cat")
    ap.add_argument("--cat-name")
    ap.add_argument("--roles", default="student,teacher,nursery")
    ap.add_argument("--phases", default="early,primary,secondary")
    ap.add_argument("--landscape", action="store_true")
    ap.add_argument("--list", action="store_true", help="show the categories and exit")
    a = ap.parse_args()

    with open(JSON_PATH) as f:
        data = json.load(f)

    if a.list:
        for cid, name in sorted(data["cats"].items()):
            n = sum(1 for i in data["items"] if i["cat"] == cid)
            print("%-24s %s (%d)" % (cid, name, n))
        return

    if not (a.pdf and a.title and a.desc and a.cat):
        ap.error("pdf, title, desc and --cat are all required (or use --list)")
    if not os.path.isfile(a.pdf) or not a.pdf.lower().endswith(".pdf"):
        sys.exit("Not a PDF file: " + a.pdf)

    roles = [r.strip() for r in a.roles.split(",") if r.strip()]
    phases = [p.strip() for p in a.phases.split(",") if p.strip()]
    if not set(roles) <= ROLES:
        sys.exit("roles must be from: " + ", ".join(sorted(ROLES)))
    if not set(phases) <= PHASES:
        sys.exit("phases must be from: " + ", ".join(sorted(PHASES)))

    cat = slug(a.cat)
    if cat not in data["cats"]:
        if not a.cat_name:
            sys.exit("New category '%s'. Add --cat-name \"Display name\" to create it." % cat)
        data["cats"][cat] = a.cat_name
    cat_name = data["cats"][cat]

    folder = os.path.join(HERE, "resources", cat)
    os.makedirs(folder, exist_ok=True)
    n = sum(1 for i in data["items"] if i["cat"] == cat) + 1
    fname = "%02d-%s.pdf" % (n, slug(a.title))
    while os.path.exists(os.path.join(folder, fname)):
        n += 1
        fname = "%02d-%s.pdf" % (n, slug(a.title))
    shutil.copyfile(a.pdf, os.path.join(folder, fname))

    pages = 1
    try:
        from pypdf import PdfReader
        pages = len(PdfReader(a.pdf).pages)
    except Exception:
        pass

    item = {
        "id": cat + "-" + fname[:-4], "title": a.title, "desc": a.desc, "cat": cat, "catName": cat_name,
        "roles": roles, "phases": phases, "file": "resources/%s/%s" % (cat, fname), "pages": pages,
        "land": a.landscape, "added": datetime.date.today().isoformat(),
    }
    # Make page previews so the Preview button works (needs pdftoppm from poppler)
    try:
        sys.path.insert(0, HERE)
        import make_previews
        rel = item["file"].replace("resources/", "previews/", 1)[:-4]
        item["pages"] = make_previews.render(os.path.join(HERE, item["file"]), os.path.join(HERE, rel))
        item["preview"] = rel
    except Exception as e:
        print("No preview made (%s). The sheet is still added; run make_previews.py later." % e)
    data["items"].append(item)
    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=1)
    print("Added '%s' to %s. The library now has %d items." % (a.title, cat_name, len(data["items"])))
    print("Upload the whole site folder again to publish it.")


if __name__ == "__main__":
    main()
