from pathlib import Path
import io
import zipfile

import pymupdf
from docx import Document
import pandas as pd
from pptx import Presentation
from PIL import Image, ImageOps
import pytesseract


# ============================================================
# PATHS
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parent

DATA_DIR = BACKEND_DIR.parent / "data"

VISUAL_DIR = DATA_DIR / "visuals"

VISUAL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

# Expected location:
#
# backend/
#     processor.py
#     Tesseract-OCR/
#         tesseract.exe
#

TESSERACT_PATH = (
    BACKEND_DIR
    
    / "tesseract.exe"
)


if TESSERACT_PATH.exists():

    pytesseract.pytesseract.tesseract_cmd = str(
        TESSERACT_PATH
    )

    print(
        "Tesseract found:",
        TESSERACT_PATH
    )

else:

    print(
        "WARNING: Tesseract not found at:",
        TESSERACT_PATH
    )

    print(
        "OCR for images/scanned PDFs may not work."
    )


# ============================================================
# SAVE VISUAL
# ============================================================

def save_visual(image, filename):

    output_path = VISUAL_DIR / filename

    image.save(
        output_path
    )

    return str(
        Path("data") / "visuals" / filename
    )


# ============================================================
# PDF PROCESSING
# ============================================================

def process_pdf(file_path):

    document = pymupdf.open(
        file_path
    )

    pages = []

    for page_number, page in enumerate(
        document
    ):

        # ----------------------------------------
        # Extract normal PDF text
        # ----------------------------------------

        text = page.get_text().strip()

        ocr_used = False

        # ----------------------------------------
        # Render PDF page as image
        # ----------------------------------------

        pix = page.get_pixmap(
            matrix=pymupdf.Matrix(
                1.5,
                1.5
            ),
            alpha=False
        )

        image = Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples
        )

        # ----------------------------------------
        # Save page image
        # ----------------------------------------

        visual = save_visual(
            image,
            f"pdf_page_{page_number + 1}.png"
        )

        # ----------------------------------------
        # OCR if PDF has little/no text
        # ----------------------------------------

        if len(text) < 20:

            if TESSERACT_PATH.exists():

                ocr_image = image.convert(
                    "L"
                )

                ocr_image = ImageOps.autocontrast(
                    ocr_image
                )

                text = pytesseract.image_to_string(
                    ocr_image,
                    config="--psm 6"
                ).strip()

                ocr_used = True

            else:

                print(
                    "Tesseract unavailable. "
                    f"Skipping OCR for PDF page {page_number + 1}."
                )

        pages.append({

            "page": page_number + 1,

            "text": text,

            "ocr_used": ocr_used,

            "visual": visual

        })

    document.close()

    return {

        "type": "pdf",

        "pages": pages,

        "page_count": len(pages)

    }


# ============================================================
# DOCX PROCESSING
# ============================================================

def process_docx(file_path):

    document = Document(
        file_path
    )

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:

            paragraphs.append(
                text
            )

    # ----------------------------------------
    # Tables
    # ----------------------------------------

    tables = []

    for table_number, table in enumerate(
        document.tables
    ):

        rows = []

        for row in table.rows:

            rows.append([

                cell.text.strip()

                for cell in row.cells

            ])

        tables.append({

            "table": table_number + 1,

            "rows": rows

        })

    # ----------------------------------------
    # Embedded images
    # ----------------------------------------

    images = []

    try:

        with zipfile.ZipFile(
            file_path,
            "r"
        ) as archive:

            image_files = [

                name

                for name in archive.namelist()

                if name.startswith(
                    "word/media/"
                )

            ]

            for number, image_file in enumerate(
                image_files
            ):

                image_bytes = archive.read(
                    image_file
                )

                image = Image.open(
                    io.BytesIO(
                        image_bytes
                    )
                ).convert(
                    "RGB"
                )

                visual = save_visual(
                    image,
                    f"docx_image_{number + 1}.png"
                )

                image_text = ""

                if TESSERACT_PATH.exists():

                    image_text = pytesseract.image_to_string(
                        image
                    ).strip()

                images.append({

                    "text": image_text,

                    "visual": visual

                })

    except Exception as error:

        print(
            "DOCX image extraction warning:",
            error
        )

    return {

        "type": "docx",

        "paragraphs": paragraphs,

        "tables": tables,

        "images": images

    }


# ============================================================
# TXT PROCESSING
# ============================================================

def process_txt(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()

    return {

        "type": "txt",

        "text": text

    }


# ============================================================
# CSV PROCESSING
# ============================================================

def process_csv(file_path):

    dataframe = pd.read_csv(
        file_path
    )

    return {

        "type": "csv",

        "columns": dataframe.columns.tolist(),

        "rows": dataframe.fillna(
            ""
        ).to_dict(
            orient="records"
        ),

        "row_count": len(
            dataframe
        )

    }


# ============================================================
# XLSX PROCESSING
# ============================================================

def process_xlsx(file_path):

    excel_file = pd.ExcelFile(
        file_path
    )

    sheets = {}

    for sheet_name in excel_file.sheet_names:

        dataframe = pd.read_excel(
            file_path,
            sheet_name=sheet_name
        )

        sheets[sheet_name] = {

            "columns": dataframe.columns.tolist(),

            "rows": dataframe.fillna(
                ""
            ).to_dict(
                orient="records"
            )

        }

    return {

        "type": "xlsx",

        "sheets": sheets

    }


# ============================================================
# PPTX PROCESSING
# ============================================================

def process_pptx(file_path):

    presentation = Presentation(
        file_path
    )

    slides = []

    for slide_number, slide in enumerate(
        presentation.slides
    ):

        slide_text = []

        for shape in slide.shapes:

            if hasattr(
                shape,
                "text"
            ):

                text = shape.text.strip()

                if text:

                    slide_text.append(
                        text
                    )

        slides.append({

            "slide": slide_number + 1,

            "text": "\n".join(
                slide_text
            ),

            "visual": None

        })

    return {

        "type": "pptx",

        "slides": slides,

        "slide_count": len(
            slides
        )

    }


# ============================================================
# IMAGE PROCESSING
# ============================================================

def process_image(file_path):

    image = Image.open(
        file_path
    ).convert(
        "RGB"
    )

    text = ""

    # ----------------------------------------
    # OCR
    # ----------------------------------------

    if TESSERACT_PATH.exists():

        text = pytesseract.image_to_string(
            image
        ).strip()

    else:

        print(
            "Tesseract not available. "
            "Image OCR skipped."
        )

    # ----------------------------------------
    # Save image
    # ----------------------------------------

    filename = (
        f"uploaded_image_"
        f"{Path(file_path).stem}.png"
    )

    visual = save_visual(
        image,
        filename
    )

    return {

        "type": "image",

        "text": text,

        "visual": visual

    }


# ============================================================
# MAIN FILE PROCESSOR
# ============================================================

def process_file(file_path):

    extension = Path(
        file_path
    ).suffix.lower()

    print(
        f"Processing file: {file_path}"
    )

    print(
        f"File type: {extension}"
    )

    # ----------------------------------------
    # PDF
    # ----------------------------------------

    if extension == ".pdf":

        return process_pdf(
            file_path
        )

    # ----------------------------------------
    # DOCX
    # ----------------------------------------

    elif extension == ".docx":

        return process_docx(
            file_path
        )

    # ----------------------------------------
    # TXT
    # ----------------------------------------

    elif extension == ".txt":

        return process_txt(
            file_path
        )

    # ----------------------------------------
    # CSV
    # ----------------------------------------

    elif extension == ".csv":

        return process_csv(
            file_path
        )

    # ----------------------------------------
    # XLSX
    # ----------------------------------------

    elif extension == ".xlsx":

        return process_xlsx(
            file_path
        )

    # ----------------------------------------
    # PPTX
    # ----------------------------------------

    elif extension == ".pptx":

        return process_pptx(
            file_path
        )

    # ----------------------------------------
    # IMAGE
    # ----------------------------------------

    elif extension in [

        ".png",

        ".jpg",

        ".jpeg"

    ]:

        return process_image(
            file_path
        )

    # ----------------------------------------
    # Unsupported
    # ----------------------------------------

    else:

        return {

            "error":
            f"Unsupported file type: {extension}"

        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "======================================"
    )

    print(
        "DOCUMENT PROCESSOR"
    )

    print(
        "======================================"
    )

    print()

    if TESSERACT_PATH.exists():

        print(
            "✓ Tesseract is configured"
        )

        try:

            version = (
                pytesseract.get_tesseract_version()
            )

            print(
                "✓ Tesseract version:",
                version
            )

        except Exception as error:

            print(
                "✗ Tesseract test failed:",
                error
            )

    else:

        print(
            "✗ Tesseract executable not found"
        )

    print()