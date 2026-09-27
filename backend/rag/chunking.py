import json
import os


# ============================================================
# CREATE TEXT CHUNKS
# ============================================================

def create_chunks(text, chunk_size=500, overlap=50):

    chunks = []

    if not text:
        return chunks

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


# ============================================================
# NORMALIZE DOCUMENT
# ============================================================

def normalize_document(extracted_data, document_name):

    document_type = extracted_data.get("type")

    sections = []


    # ========================================================
    # PDF
    # ========================================================

    if document_type == "pdf":

        for page in extracted_data.get("pages", []):

            sections.append({
                "text": page.get("text", ""),
                "page": page.get("page"),
                "slide": None,
                "sheet": None,
                "section": "PDF Page",
                "visual": page.get("visual")
            })


    # ========================================================
    # PPTX
    # ========================================================

    elif document_type == "pptx":

        for slide in extracted_data.get("slides", []):

            slide_text = slide.get("text", "")

            if isinstance(slide_text, list):
                slide_text = "\n".join(
                    str(item)
                    for item in slide_text
                )

            sections.append({
                "text": slide_text,
                "page": None,
                "slide": slide.get("slide"),
                "sheet": None,
                "section": "PowerPoint Slide",
                "visual": slide.get("visual")
            })


    # ========================================================
    # IMAGE / OCR
    # ========================================================

    elif document_type == "image":

        sections.append({
            "text": extracted_data.get("text", ""),
            "page": None,
            "slide": None,
            "sheet": None,
            "section": "OCR",
            "visual": extracted_data.get("visual")
        })


    # ========================================================
    # TXT
    # ========================================================

    elif document_type == "txt":

        sections.append({
            "text": extracted_data.get("text", ""),
            "page": None,
            "slide": None,
            "sheet": None,
            "section": "Text File",
            "visual": None
        })


    # ========================================================
    # DOCX
    # ========================================================

    elif document_type == "docx":

        # Paragraphs
        for text in extracted_data.get("paragraphs", []):

            if text:

                sections.append({
                    "text": text,
                    "page": None,
                    "slide": None,
                    "sheet": None,
                    "section": "DOCX Paragraph",
                    "visual": None
                })


        # Tables
        for table in extracted_data.get("tables", []):

            table_text = "\n".join(
                " | ".join(
                    str(cell)
                    for cell in row
                )
                for row in table.get("rows", [])
            )

            if table_text:

                sections.append({
                    "text": table_text,
                    "page": None,
                    "slide": None,
                    "sheet": None,
                    "section": "DOCX Table",
                    "visual": None
                })


        # Embedded images
        for image in extracted_data.get("images", []):

            image_text = image.get("text", "")

            if image_text:

                sections.append({
                    "text": image_text,
                    "page": None,
                    "slide": None,
                    "sheet": None,
                    "section": "DOCX Image",
                    "visual": image.get("visual")
                })


    # ========================================================
    # CSV
    # ========================================================

    elif document_type == "csv":

        columns = extracted_data.get(
            "columns",
            []
        )

        rows = extracted_data.get(
            "rows",
            []
        )

        csv_lines = []

        if columns:

            csv_lines.append(
                " | ".join(
                    map(str, columns)
                )
            )

        for row in rows:

            csv_lines.append(
                " | ".join(
                    str(row.get(column, ""))
                    for column in columns
                )
            )

        csv_text = "\n".join(csv_lines)

        sections.append({
            "text": csv_text,
            "page": None,
            "slide": None,
            "sheet": None,
            "section": "CSV",
            "visual": None
        })


    # ========================================================
    # XLSX
    # ========================================================

    elif document_type == "xlsx":

        sheets = extracted_data.get(
            "sheets",
            {}
        )


        # ----------------------------------------------------
        # Dictionary format
        # ----------------------------------------------------

        if isinstance(sheets, dict):

            for sheet_name, sheet in sheets.items():

                columns = sheet.get(
                    "columns",
                    []
                )

                rows = sheet.get(
                    "rows",
                    []
                )

                lines = []

                if columns:

                    lines.append(
                        " | ".join(
                            map(str, columns)
                        )
                    )

                for row in rows:

                    lines.append(
                        " | ".join(
                            str(row.get(column, ""))
                            for column in columns
                        )
                    )

                sheet_text = "\n".join(lines)

                sections.append({

                    "text": sheet_text,

                    "page": None,

                    "slide": None,

                    "sheet": sheet_name,

                    "section": "Excel Sheet",

                    "visual": sheet.get(
                        "visual"
                    )
                })


        # ----------------------------------------------------
        # List format
        # ----------------------------------------------------

        elif isinstance(sheets, list):

            for sheet in sheets:

                columns = sheet.get(
                    "columns",
                    []
                )

                rows = sheet.get(
                    "rows",
                    []
                )

                lines = []

                if columns:

                    lines.append(
                        " | ".join(
                            map(str, columns)
                        )
                    )

                for row in rows:

                    lines.append(
                        " | ".join(
                            str(row.get(column, ""))
                            for column in columns
                        )
                    )

                sheet_text = "\n".join(lines)

                sections.append({

                    "text": sheet_text,

                    "page": None,

                    "slide": None,

                    "sheet": sheet.get(
                        "sheet_name"
                    ),

                    "section": "Excel Sheet",

                    "visual": sheet.get(
                        "visual"
                    )
                })


    # ========================================================
    # UNSUPPORTED
    # ========================================================

    else:

        raise ValueError(
            f"Unsupported extracted document type: {document_type}"
        )


    # ========================================================
    # CREATE FINAL CHUNKS
    # ========================================================

    all_chunks = []

    chunk_id = 0


    for section in sections:

        text = section.get(
            "text",
            ""
        )

        if not text:
            continue

        chunks = create_chunks(
            text,
            chunk_size=500,
            overlap=50
        )


        for chunk in chunks:

            all_chunks.append({

                "id": chunk_id,

                "text": chunk,

                "document": document_name,

                "page": section.get(
                    "page"
                ),

                "slide": section.get(
                    "slide"
                ),

                "sheet": section.get(
                    "sheet"
                ),

                "section": section.get(
                    "section"
                ),

                "visual": section.get(
                    "visual"
                )

            })

            chunk_id += 1


    return all_chunks


# ============================================================
# SAVE CHUNKS
# ============================================================

def save_chunks(chunks):

    data_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "data"
        )
    )

    os.makedirs(
        data_folder,
        exist_ok=True
    )


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


    print(
        "Chunks saved to:",
        output_path
    )

    print(
        "Number of chunks:",
        len(chunks)
    )