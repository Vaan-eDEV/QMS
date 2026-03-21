from docx import Document
from bs4 import BeautifulSoup

def convert_html_to_docx(html, output_file):
    soup = BeautifulSoup(html, "html.parser")
    doc = Document()

    # Default font settings
    style = doc.styles['Normal']
    font = style.font
    font.name = "Arial"
    font.size = None  # Prevent overriding inline font sizes

    for element in soup.recursiveChildGenerator():

        if element.name == "p":
            p = doc.add_paragraph()
            add_html_text_formatting(p, element)

        elif element.name in ["h1", "h2", "h3", "h4"]:
            p = doc.add_heading(level=int(element.name[1]))
            add_html_text_formatting(p, element)

        elif element.name == "ul":
            for li in element.find_all("li"):
                p = doc.add_paragraph(style="List Bullet")
                add_html_text_formatting(p, li)

        elif element.name == "ol":
            for li in element.find_all("li"):
                p = doc.add_paragraph(style="List Number")
                add_html_text_formatting(p, li)

        elif element.name == "table":
            rows = element.find_all("tr")
            if not rows:
                continue

            cols = max(len(r.find_all(["td", "th"])) for r in rows)
            table = doc.add_table(rows=len(rows), cols=cols)

            for i, row in enumerate(rows):
                cells = row.find_all(["td", "th"])
                for j, cell in enumerate(cells):
                    cell_content = table.rows[i].cells[j].paragraphs[0]
                    add_html_text_formatting(cell_content, cell)

    doc.save(output_file)


def add_html_text_formatting(paragraph, html_element):
    """ Apply formatting like bold, italic, underline and font size """

    for child in html_element.children:
        if child.name is None:  # Plain text
            paragraph.add_run(str(child))

        else:
            run = paragraph.add_run(child.get_text())

            style = child.get("style", "")

            if child.name == "b" or "font-weight:bold" in style:
                run.bold = True

            if child.name == "i" or "font-style:italic" in style:
                run.italic = True

            if child.name == "u" or "text-decoration:underline" in style:
                run.underline = True

            if "font-size" in style:
                size = style.split("font-size:")[1].split(";")[0].replace("px", "").strip()
                try:
                    run.font.size = Pt(int(size) * 0.75)  # px → pt conversion
                except:
                    pass
