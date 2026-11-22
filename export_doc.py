from pathlib import Path
from docx import Document


def save_markdown(content: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def save_docx(content: str, output_path: Path, title: str = "Meeting Minutes") -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    doc.add_heading(title, level=1)

    for line in content.splitlines():
        clean = line.strip()
        if not clean:
            continue
        if clean.startswith("### "):
            doc.add_heading(clean[4:], level=3)
        elif clean.startswith("## "):
            doc.add_heading(clean[3:], level=2)
        elif clean.startswith("# "):
            doc.add_heading(clean[2:], level=1)
        elif clean.startswith(("- ", "* ")):
            doc.add_paragraph(clean[2:], style="List Bullet")
        else:
            doc.add_paragraph(clean)

    doc.save(output_path)
    return output_path
