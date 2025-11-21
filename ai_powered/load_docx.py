from docx import Document

def load_docx_content(file_path):
    doc = Document(file_path)
    content = []
    for para in doc.paragraphs:
        if para.text.strip():
            content.append(para.text.strip())
    return "\n".join(content)
