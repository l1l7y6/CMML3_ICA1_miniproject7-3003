from __future__ import annotations

import datetime as _dt
import struct
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = REPO_ROOT / "analysis"

REPORT_MD = ANALYSIS_DIR / "ica1_report.md"
SUPP_MD = ANALYSIS_DIR / "ica1_supplementary_methods.md"
SUPP_DISPLAY_MD = ANALYSIS_DIR / "ica1_supporting_display_items.md"
REFLECTION_MD = ANALYSIS_DIR / "ica1_reflection.md"
FIG1 = ANALYSIS_DIR / "ica1_figure1_spike_fits.png"
FIG2 = ANALYSIS_DIR / "ica1_figure2_system_outputs.png"

REPORT_DOCX = ANALYSIS_DIR / "ica1_report.docx"
SUPP_DOCX = ANALYSIS_DIR / "ica1_supporting_materials.docx"
SUPP_METHODS_DOCX = ANALYSIS_DIR / "ica1_supplementary_methods.docx"
SUPP_DISPLAY_DOCX = ANALYSIS_DIR / "ica1_supporting_display_items.docx"
REFLECTION_DOCX = ANALYSIS_DIR / "ica1_reflection.docx"
ROLL_NUMBER = "3003"

EMU_PER_INCH = 914400
MAX_FIGURE_WIDTH_IN = 6.2


def read_png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        signature = handle.read(8)
        if signature != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"{path} is not a PNG")
        _chunk_len = struct.unpack(">I", handle.read(4))[0]
        chunk_type = handle.read(4)
        if chunk_type != b"IHDR":
            raise ValueError(f"{path} has no IHDR chunk")
        width, height = struct.unpack(">II", handle.read(8))
        return width, height


def paragraph_xml(text: str, bold: bool = False, size_half_points: int = 24, align: str | None = None) -> str:
    # Strip inline markdown code marks so exported coursework reads like a normal Word document.
    text = text.replace("`", "")
    text = escape(text)
    jc = f"<w:pPr><w:jc w:val=\"{align}\"/></w:pPr>" if align else ""
    run_props = [f"<w:sz w:val=\"{size_half_points}\"/>", f"<w:szCs w:val=\"{size_half_points}\"/>"]
    if bold:
        run_props.append("<w:b/>")
    rpr = f"<w:rPr>{''.join(run_props)}</w:rPr>"
    return (
        "<w:p>"
        f"{jc}"
        "<w:r>"
        f"{rpr}"
        f"<w:t xml:space=\"preserve\">{text}</w:t>"
        "</w:r>"
        "</w:p>"
    )


def first_markdown_heading(markdown_path: Path, fallback: str) -> str:
    for line in markdown_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def blank_paragraph_xml() -> str:
    return "<w:p/>"


def image_paragraph_xml(rid: str, cx: int, cy: int, docpr_id: int, name: str) -> str:
    name = escape(name)
    return f"""
<w:p>
  <w:pPr><w:jc w:val="center"/></w:pPr>
  <w:r>
    <w:drawing>
      <wp:inline distT="0" distB="0" distL="0" distR="0"
        xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
        xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
        xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
        <wp:extent cx="{cx}" cy="{cy}"/>
        <wp:docPr id="{docpr_id}" name="{name}"/>
        <wp:cNvGraphicFramePr>
          <a:graphicFrameLocks noChangeAspect="1"/>
        </wp:cNvGraphicFramePr>
        <a:graphic>
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic>
              <pic:nvPicPr>
                <pic:cNvPr id="0" name="{name}"/>
                <pic:cNvPicPr/>
              </pic:nvPicPr>
              <pic:blipFill>
                <a:blip r:embed="{rid}"/>
                <a:stretch><a:fillRect/></a:stretch>
              </pic:blipFill>
              <pic:spPr>
                <a:xfrm>
                  <a:off x="0" y="0"/>
                  <a:ext cx="{cx}" cy="{cy}"/>
                </a:xfrm>
                <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
              </pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>
""".strip()


def png_dimensions_emu(path: Path, max_width_in: float = MAX_FIGURE_WIDTH_IN) -> tuple[int, int]:
    width_px, height_px = read_png_size(path)
    scale = min(1.0, max_width_in / max(width_px / 96.0, 1e-9))
    width_in = (width_px / 96.0) * scale
    height_in = (height_px / 96.0) * scale
    return int(width_in * EMU_PER_INCH), int(height_in * EMU_PER_INCH)


def core_props_xml(title: str) -> str:
    now = _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{escape(title)}</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>
"""


APP_PROPS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
</Properties>
"""


CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""


PACKAGE_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


STYLES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
        <w:sz w:val="24"/>
        <w:szCs w:val="24"/>
        <w:lang w:val="en-GB"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:after="120" w:line="360" w:lineRule="auto"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>
</w:styles>
"""


def build_document_xml(body_blocks: list[str]) -> str:
    body = "".join(body_blocks)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
 xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
 xmlns:v="urn:schemas-microsoft-com:vml"
 xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:w10="urn:schemas-microsoft-com:office:word"
 xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
 xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
 xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
 xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
 xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
 mc:Ignorable="w14 wp14">
  <w:body>
    {body}
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>
"""


def build_document_rels(image_targets: list[str]) -> str:
    rels = [
        '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    ]
    for index, target in enumerate(image_targets, start=1):
        rels.append(
            f'<Relationship Id="rIdImage{index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{target}"/>'
        )
    rels_text = "".join(rels)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {rels_text}
</Relationships>
"""


def write_docx(output_path: Path, title: str, body_blocks: list[str], images: list[Path]) -> None:
    image_names = [f"image{idx}{path.suffix.lower()}" for idx, path in enumerate(images, start=1)]
    document_xml = build_document_xml(body_blocks)
    rels_xml = build_document_rels(image_names)

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES_XML)
        zf.writestr("_rels/.rels", PACKAGE_RELS_XML)
        zf.writestr("docProps/core.xml", core_props_xml(title))
        zf.writestr("docProps/app.xml", APP_PROPS_XML)
        zf.writestr("word/document.xml", document_xml)
        zf.writestr("word/styles.xml", STYLES_XML)
        zf.writestr("word/_rels/document.xml.rels", rels_xml)
        for image_name, image_path in zip(image_names, images):
            zf.write(image_path, f"word/media/{image_name}")


def append_markdown_to_doc(
    body: list[str],
    images: list[Path],
    markdown_path: Path,
    title: str | None = None,
) -> None:
    if title is not None:
        body.append(paragraph_xml(title, bold=True, size_half_points=32, align="center"))
        body.append(blank_paragraph_xml())

    lines = markdown_path.read_text(encoding="utf-8").splitlines()
    skip_first_h1 = title is not None

    for line in lines:
        stripped = line.strip()
        if skip_first_h1 and line.startswith("# "):
            skip_first_h1 = False
            continue
        if not stripped:
            body.append(blank_paragraph_xml())
            continue
        if stripped.startswith("[[IMAGE:") and stripped.endswith("]]"):
            image_rel = stripped[len("[[IMAGE:") : -2]
            image_path = (markdown_path.parent / image_rel).resolve()
            images.append(image_path)
            cx, cy = png_dimensions_emu(image_path)
            image_index = len(images)
            body.append(image_paragraph_xml(f"rIdImage{image_index}", cx, cy, image_index, image_path.stem))
            continue
        if line.startswith("# "):
            body.append(paragraph_xml(line[2:], bold=True, size_half_points=28))
            continue
        if line.startswith("**") and line.endswith("**"):
            body.append(paragraph_xml(line.strip("*"), bold=True, size_half_points=24))
            continue
        body.append(paragraph_xml(line))


def markdown_text_doc_body(title: str, markdown_path: Path) -> list[str]:
    body: list[str] = []
    append_markdown_to_doc(body, [], markdown_path, title=title)
    return body


def build_report_docx() -> None:
    body: list[str] = []
    report_title = first_markdown_heading(
        REPORT_MD,
        "A simple depolarising afterpotential increases secretion output and captures selected DAP-like spike-train features",
    )
    body.append(paragraph_xml(report_title, bold=True, size_half_points=32, align="center"))
    body.append(paragraph_xml("ICA1 Report", bold=False, size_half_points=24, align="center"))
    body.append(paragraph_xml(f"Roll Number: {ROLL_NUMBER}", bold=False, size_half_points=24, align="center"))
    body.append(blank_paragraph_xml())

    report_text = REPORT_MD.read_text(encoding="utf-8").splitlines()

    skip_prefixes = ("# ",)
    section_lines: list[str] = []
    for line in report_text:
        if line.startswith(skip_prefixes):
            continue
        if not line.strip():
            section_lines.append("")
            continue
        section_lines.append(line.rstrip())

    fig1_cx, fig1_cy = png_dimensions_emu(FIG1)
    fig2_cx, fig2_cy = png_dimensions_emu(FIG2)

    docpr_id = 1
    for line in section_lines:
        if not line:
            body.append(blank_paragraph_xml())
            continue
        if line.startswith("**") and line.endswith("**"):
            heading = line.strip("*")
            body.append(paragraph_xml(heading, bold=True, size_half_points=26))
            continue
        if line.startswith("Figure 1."):
            body.append(image_paragraph_xml("rIdImage1", fig1_cx, fig1_cy, docpr_id, "Figure 1"))
            docpr_id += 1
            body.append(paragraph_xml(line, size_half_points=22))
            continue
        if line.startswith("Figure 2."):
            body.append(image_paragraph_xml("rIdImage2", fig2_cx, fig2_cy, docpr_id, "Figure 2"))
            docpr_id += 1
            body.append(paragraph_xml(line, size_half_points=22))
            continue
        body.append(paragraph_xml(line))

    write_docx(REPORT_DOCX, report_title, body, [FIG1, FIG2])


def build_supporting_docx() -> None:
    body: list[str] = []
    images: list[Path] = []
    body.append(paragraph_xml("ICA1 Supporting Materials", bold=True, size_half_points=32, align="center"))
    body.append(paragraph_xml(f"Roll Number: {ROLL_NUMBER}", bold=False, size_half_points=24, align="center"))
    body.append(blank_paragraph_xml())
    append_markdown_to_doc(body, images, SUPP_MD)
    if SUPP_DISPLAY_MD.exists():
        body.append(blank_paragraph_xml())
        append_markdown_to_doc(body, images, SUPP_DISPLAY_MD)
    body.append(blank_paragraph_xml())
    append_markdown_to_doc(body, images, REFLECTION_MD)
    write_docx(SUPP_DOCX, "ICA1 Supporting Materials", body, images)


def build_supplementary_methods_docx() -> None:
    body = markdown_text_doc_body("ICA1 Supplementary Methods", SUPP_MD)
    write_docx(SUPP_METHODS_DOCX, "ICA1 Supplementary Methods", body, [])


def build_supporting_display_docx() -> None:
    body: list[str] = []
    images: list[Path] = []
    append_markdown_to_doc(body, images, SUPP_DISPLAY_MD, title="ICA1 Supporting Display Items")
    write_docx(SUPP_DISPLAY_DOCX, "ICA1 Supporting Display Items", body, images)


def build_reflection_docx() -> None:
    body = markdown_text_doc_body("ICA1 Reflection", REFLECTION_MD)
    write_docx(REFLECTION_DOCX, "ICA1 Reflection", body, [])


def main() -> None:
    build_report_docx()
    build_supporting_docx()
    print(f"wrote {REPORT_DOCX}")
    print(f"wrote {SUPP_DOCX}")


if __name__ == "__main__":
    main()
