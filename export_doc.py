from pathlib import Path
from docx import Document
from docx.oxml.ns import qn


def _apply_myanmar_font(run, font_name: str = "Pyidaungsu") -> None:
    """Apply Myanmar Unicode font settings to a Word run."""
    run.font.name = font_name
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = run._element.makeelement(qn("w:rFonts"), {})
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)
    rFonts.set(qn("w:cs"), font_name)


def save_markdown(content: str, output_path: Path) -> Path:
    """Save text or Markdown content to a UTF-8 file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def save_docx(
    content: str,
    output_path: Path,
    title: str = "အစည်းအဝေး မှတ်တမ်း",
    font_name: str = "Pyidaungsu",
) -> Path:
    """Save structured minutes to a .docx Word file formatted with Pyidaungsu."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()

    normal_style = doc.styles["Normal"]
    normal_style.font.name = font_name
    normal_style._element.rPr.rFonts.set(qn("w:cs"), font_name)

    heading = doc.add_heading(title, level=1)
    for run in heading.runs:
        _apply_myanmar_font(run, font_name)

    for line in content.splitlines():
        clean = line.strip()
        if not clean:
            continue

        if clean.startswith("### "):
            p = doc.add_heading(clean[4:], level=3)
        elif clean.startswith("## "):
            p = doc.add_heading(clean[3:], level=2)
        elif clean.startswith("# "):
            p = doc.add_heading(clean[2:], level=1)
        elif clean.startswith(("- ", "* ")):
            p = doc.add_paragraph(clean[2:], style="List Bullet")
        else:
            p = doc.add_paragraph(clean)

        for run in p.runs:
            _apply_myanmar_font(run, font_name)

    doc.save(output_path)
    return output_path
