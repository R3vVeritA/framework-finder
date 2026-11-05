# Framework Finder website

Five pages and a library of 267 printable PDFs.

| File or folder | What it is |
|---|---|
| `index.html` | Homepage: areas of learning, quick starts, links to everything |
| `early-years.html` | Early years hub: the seven EYFS areas, official sources, setting essentials |
| `printables.html` | Searchable printables library. Filters by role, category, phase and area of learning. Reads `resources.json` |
| `make.html` | Make your own: name tracing sheets, name labels, class register (names stay in the browser) |
| `frameworks.html` | Directory of official frameworks and free materials (England, Scotland, Wales, Northern Ireland) |
| `resources.json` | Every printable: title, description, category, who it is for, areas of learning, file path |
| `resources/` | The PDFs, one folder per category |
| `previews/` | A picture of every PDF page, used by the Preview button |
| `add_resource.py` | Adds a new PDF to the library (and makes its previews) |
| `make_previews.py` | Makes previews for any PDF that has none. Needs `pdftoppm` from poppler |
| `generate.py` | Makes all 267 PDFs from scratch. Edit the `BRAND` and `FOOT` lines at the top to rebrand |
| `build_site.py` | Rebuilds the homepage, early years hub and make-your-own pages |

## Put it online (free)

1. Go to app.netlify.com/drop.
2. Drag this whole folder onto the page.
3. You get a link straight away. To update later, drag the folder on again.

The printables page needs a web host. Double-clicking `printables.html` shows a message instead of the list.

## Add more things

**A new printable PDF**

```
python3 add_resource.py my-sheet.pdf "Sheet title" "One-sentence description" --cat ey-activities --roles nursery,teacher --phases early
```

Run `python3 add_resource.py --list` to see the categories. To make a new category, use a new `--cat` id and add `--cat-name "Display name"`. New items show a "New" tag for 30 days.

Areas of learning are set in `resources.json` with an `"areas": ["literacy", "mathematics"]` list on an item. Valid ids: communication, personal-social, physical, literacy, mathematics, understanding-world, expressive-arts. The tags on the generated sheets are suggestions, so check them.

**A new framework or link**

Open `frameworks.html`, find the `const R = [` list in the script, and copy an existing entry. Only add links you have checked on the owner's own page.

**Links into the library**

`printables.html#early`, `#primary`, `#student`, `#teacher`, `#nursery`, `#area-literacy`, or a category id such as `#ey-observation`.

## Before you share or sell

- Every PDF footer says "Free to print and use in your own setting. Not for resale." Change `FOOT` in `generate.py` and regenerate if you want different wording.
- Safeguarding, safer sleep, fire drill and risk assessment sheets are general templates. Users must follow their own setting's policies and the current official rules.
- Do not use the logos of the DfE, Ofsted or any other organisation.
- Check the licence of anything you link to before copying its content. This site links out and does not copy it.
