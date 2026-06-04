def convert_docx_to_html(file_path):
    """
    Converts a DOCX file to HTML with inline images and Word page breaks.
    Returns a list of pages, each as HTML string.
    """
    import mammoth
    import base64

    def convert_image(image):
        with image.open() as image_bytes:
            data = image_bytes.read()
        base64_data = base64.b64encode(data).decode("utf-8")
        return {"src": f"data:{image.content_type};base64,{base64_data}"}

    with open(file_path, "rb") as f:
        style_map = "page-break => div.page-break"
        result = mammoth.convert_to_html(
            f,
            convert_image=mammoth.images.inline(convert_image),
            style_map=style_map
        )
        html_content = result.value

    # Split content at page breaks
    pages = html_content.split('<div class="page-break"></div>')
    # Wrap each page
    wrapped_pages = [f'<div class="page">{p}</div>' for p in pages if p.strip()]

    # Return **list of pages**, not a single string
    return wrapped_pages


    











# from docx import Document
# from docx.enum.text import WD_BREAK
# from html import escape

# def convert_docx_to_html_with_pages(file_path):
#     """
#     Converts a DOCX file to HTML, preserving manual page breaks.
#     Returns a single HTML string with <div class="page-break"></div> between pages.
#     """
#     doc = Document(file_path)
#     pages = []
#     current_page = []

#     for para in doc.paragraphs:
#         # Convert paragraph text to HTML-safe string
#         text = escape(para.text)
#         if not text:
#             text = "<br>"  # preserve empty lines

#         # Wrap in <p>
#         current_page.append(f"<p>{text}</p>")

#         # Check for manual page break in paragraph runs
#         for run in para.runs:
#             if run.break_type == WD_BREAK.PAGE:
#                 # End of page detected
#                 pages.append("\n".join(current_page))
#                 current_page = []

#     # Add any remaining content as last page
#     if current_page:
#         pages.append("\n".join(current_page))

#     # Join pages with <div class="page-break"></div>
#     html_content = ('<div class="page-break"></div>').join(pages)
#     return html_content
