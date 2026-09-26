import json
import os


def create_chunks(text, chunk_size=500, overlap=50):
    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def normalize_document(extracted_data, document_name):
    """
    Convert Member 2's different document formats
    into one common structure for RAG.
    """

    document_type = extracted_data.get("type")

    sections = []

    # -------------------------
    # PDF
    # -------------------------

    if document_type == "pdf":

        for page in extracted_data.get("pages", []):

            sections.append({
                "text": page.get("text", ""),
                "page": page.get("page"),
                "slide": None,
                "sheet": None,
                "section": "PDF Page",
            })

    # -------------------------
    # PPTX
    # -------------------------

    elif document_type == "pptx":

        for slide in extracted_data.get("slides", []):

            sections.append({
                "text": slide.get("text", ""),
                "page": None,
                "slide": slide.get("slide"),
                "sheet": None,
                "section": "PowerPoint Slide",
            })

    # -------------------------
    # IMAGE / OCR
    # -------------------------

    elif document_type == "image":

        sections.append({
            "text": extracted_data.get("text", ""),
            "page": None,
            "slide": None,
            "sheet": None,
            "section": "OCR",
        })

    # -------------------------
    # TXT
    # -------------------------

    elif document_type == "txt":

        sections.append({
            "text": extracted_data.get("text", ""),
            "page": None,
            "slide": None,
            "sheet": None,
            "section": "Text File",
        })

    # -------------------------
    # DOCX
    # -------------------------

    elif document_type == "docx":

        for text in extracted_data.get("paragraphs", []):

            sections.append({
                "text": text,
                "page": None,
                "slide": None,
                "sheet": None,
                "section": "DOCX Paragraph",
            })

        for table in extracted_data.get("tables", []):

            table_text = "\n".join(
                " | ".join(row)
                for row in table.get("rows", [])
            )

            sections.append({
                "text": table_text,
                "page": None,
                "slide": None,
                "sheet": None,
                "section": f"DOCX Table {table.get('table')}",
            })

    # -------------------------
    # CSV
    # -------------------------

    elif document_type == "csv":

        columns = extracted_data.get("columns", [])
        rows = extracted_data.get("rows", [])

        csv_text = " | ".join(map(str, columns))

        for row in rows:
            csv_text += "\n" + " | ".join(
                str(row.get(column, ""))
                for column in columns
            )

        sections.append({
            "text": csv_text,
            "page": None,
            "slide": None,
            "sheet": None,
            "section": "CSV",
        })

    # -------------------------
    # XLSX
    # -------------------------

    elif document_type == "xlsx":

        for sheet in extracted_data.get("sheets", []):

            columns = sheet.get("columns", [])
            rows = sheet.get("rows", [])

            sheet_text = " | ".join(
                map(str, columns)
            )

            for row in rows:

                sheet_text += "\n" + " | ".join(
                    str(row.get(column, ""))
                    for column in columns
                )

            sections.append({
                "text": sheet_text,
                "page": None,
                "slide": None,
                "sheet": sheet.get("sheet_name"),
                "section": "Excel Sheet",
            })

    else:

        raise ValueError(
            f"Unsupported extracted document type: {document_type}"
        )

    # -------------------------
    # CREATE FINAL CHUNKS
    # -------------------------

    all_chunks = []

    chunk_id = 0

    for section in sections:

        text = section["text"]

        if not text:
            continue

        chunks = create_chunks(text)

        for chunk in chunks:

            all_chunks.append({

                "id": chunk_id,

                "text": chunk,

                "document": document_name,

                "page": section["page"],

                "slide": section["slide"],

                "sheet": section["sheet"],

                "section": section["section"]

            })

            chunk_id += 1

    return all_chunks


def save_chunks(chunks):

    data_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "data"
        )
    )

    os.makedirs(data_folder, exist_ok=True)

    output_path = os.path.join(
        data_folder,
        "chunks.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("Chunks saved to:", output_path)
    print("Number of chunks:", len(chunks))