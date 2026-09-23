from docx import Document
from docx.oxml.ns import qn
from collections import Counter

path = r"C:\Users\crist\Desktop\medina\EP1_ISY1102_Estudiante_Formato_Informe.docx"
doc = Document(path)

print("=== STYLES USED ===")
used = Counter()
for p in doc.paragraphs:
    used[p.style.name if p.style else "?"] += 1
for k, v in used.most_common():
    print(f"  {k}: {v}")

print("\n=== ALL PARAGRAPH STYLES IN DOC ===")
for s in doc.styles:
    if s.type is not None and "PARAGRAPH" in str(s.type):
        fn = s.font.name if s.font else None
        fs = s.font.size.pt if s.font and s.font.size else None
        fb = s.font.bold if s.font else None
        print(f"  {s.name}: font={fn} size={fs} bold={fb}")

print("\n=== FULL DOCUMENT FLOW (body order) ===")
body = doc.element.body
ti = 0
for child in body.iterchildren():
    if child.tag == qn("w:p"):
        p = next((para for para in doc.paragraphs if para._p is child), None)
        if p is None:
            continue
        style = p.style.name if p.style else "?"
        text = p.text
        if text.strip() or style != "Normal":
            # font info from first run
            fonts, sizes, bolds, colors = set(), set(), set(), set()
            for r in p.runs:
                if r.font.name:
                    fonts.add(r.font.name)
                if r.font.size:
                    sizes.add(f"{r.font.size.pt}pt")
                bolds.add(bool(r.bold))
                if r.font.color and r.font.color.rgb:
                    colors.add(str(r.font.color.rgb))
            meta = f" font={fonts or '-'} size={sizes or '-'} bold={bolds} color={colors or '-'} align={p.alignment}"
            print(f"P[{style}]{meta}")
            print(f"  {text}")
    elif child.tag == qn("w:tbl"):
        t = doc.tables[ti]
        print(f"\n>>> TABLE {ti} ({len(t.rows)}x{len(t.columns)})")
        for ri, row in enumerate(t.rows):
            cells = [c.text.replace("\n", " / ") for c in row.cells]
            print(f"  R{ri}: {cells}")
        print()
        ti += 1

print("\n=== SECTIONS ===")
for si, sec in enumerate(doc.sections):
    print(
        f"Section {si}: w={sec.page_width} h={sec.page_height} "
        f"L={sec.left_margin} R={sec.right_margin} T={sec.top_margin} B={sec.bottom_margin}"
    )
    for p in sec.header.paragraphs:
        if p.text.strip():
            print(f"  header: {p.text!r}")
    for p in sec.footer.paragraphs:
        if p.text.strip():
            print(f"  footer: {p.text!r}")

print("\n=== NUMBERING / TOC field check ===")
# look for TOC field
xml = doc.element.body.xml
if "TOC" in xml:
    print("  Contains TOC field instruction")
print(f"  Total paragraphs: {len(doc.paragraphs)}")
print(f"  Total tables: {len(doc.tables)}")
