from pathlib import Path
import os
import io
import zipfile

import pymupdf
from docx import Document
import pandas as pd
from pptx import Presentation
from PIL import Image
import pytesseract


# --------------------------------------------------
# VISUAL STORAGE
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
VISUAL_DIR = BASE_DIR / "data" / "visuals"

VISUAL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def save_visual(image, filename):
    """
    Save an image and return its relative path.
    """

    output_path = VISUAL_DIR / filename

    image.save(output_path)

    return str(
        Path("data") / "visuals" / filename
    )


# --------------------------------------------------
# PDF PROCESSING
# --------------------------------------------------

def process_pdf(file_path):

    document = pymupdf.open(file_path)

    pages = []

    for page_number, page in enumerate(document):

        text = page.get_text().strip()

        ocr_used = False
        visual = None

        # ------------------------------------------
        # Render page
        # ------------------------------------------

        pix = page.get_pixmap(
            matrix=pymupdf.Matrix(1.5, 1.5),
            alpha=False
        )

        image = Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples
        )

        # Save page image
        visual = save_visual(
            image,
            f"pdf_page_{page_number + 1}.png"
        )

        # ------------------------------------------
        # OCR if necessary
        # ------------------------------------------

        if len(text) < 20:

            ocr_image = image.convert("L")

            from PIL import ImageOps

            ocr_image = ImageOps.autocontrast(
                ocr_image
            )

            text = pytesseract.image_to_string(
                ocr_image,
                config="--psm 6"
            ).strip()

            ocr_used = True

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


# --------------------------------------------------
# DOCX PROCESSING
# --------------------------------------------------

def process_docx(file_path):

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:

            paragraphs.append(text)

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

    # ------------------------------------------
    # Extract embedded images
    # ------------------------------------------

    images = []

    with zipfile.ZipFile(file_path, "r") as archive:

        image_files = [
            name
            for name in archive.namelist()
            if name.startswith("word/media/")
        ]

        for number, image_file in enumerate(
            image_files
        ):

            image_bytes = archive.read(
                image_file
            )

            image = Image.open(
                io.BytesIO(image_bytes)
            ).convert("RGB")

            visual = save_visual(
                image,
                f"docx_image_{number + 1}.png"
            )

            # OCR image so it can also be retrieved
            image_text = pytesseract.image_to_string(
                image
            ).strip()

            images.append({

                "text": image_text,

                "visual": visual
            })

    return {

        "type": "docx",

        "paragraphs": paragraphs,

        "tables": tables,

        "images": images
    }


# --------------------------------------------------
# TXT PROCESSING
# --------------------------------------------------

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


# --------------------------------------------------
# CSV PROCESSING
# --------------------------------------------------

def process_csv(file_path):

    dataframe = pd.read_csv(file_path)

    return {

        "type": "csv",

        "columns": dataframe.columns.tolist(),

        "rows": dataframe.fillna(
            ""
        ).to_dict(
            orient="records"
        ),

        "row_count": len(dataframe)
    }


# --------------------------------------------------
# XLSX PROCESSING
# --------------------------------------------------

def process_xlsx(file_path):

    excel_file = pd.ExcelFile(file_path)

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


# --------------------------------------------------
# PPTX PROCESSING
# --------------------------------------------------

def process_pptx(file_path):

    presentation = Presentation(
        file_path
    )

    slides = []

    for slide_number, slide in enumerate(
        presentation.slides
    ):

        slide_text = []

        visual = None

        # ------------------------------------------
        # Extract slide text
        # ------------------------------------------

        for shape in slide.shapes:

            if hasattr(shape, "text"):

                text = shape.text.strip()

                if text:

                    slide_text.append(text)

        # ------------------------------------------
        # Render complete slide as image
        # ------------------------------------------

        # python-pptx does not directly render slides.
        # Keep visual as None here; frontend can still
        # use slide metadata.

        slides.append({

            "slide": slide_number + 1,

            "text": slide_text,

            "visual": visual
        })

    return {

        "type": "pptx",

        "slides": slides,

        "slide_count": len(slides)
    }


# --------------------------------------------------
# IMAGE OCR PROCESSING
# --------------------------------------------------

def process_image(file_path):

    image = Image.open(
        file_path
    ).convert("RGB")

    text = pytesseract.image_to_string(
        image
    ).strip()

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


# --------------------------------------------------
# MAIN FILE PROCESSOR
# --------------------------------------------------

def process_file(file_path):

    extension = Path(
        file_path
    ).suffix.lower()

    if extension == ".pdf":

        return process_pdf(file_path)

    elif extension == ".docx":

        return process_docx(file_path)

    elif extension == ".txt":

        return process_txt(file_path)

    elif extension == ".csv":

        return process_csv(file_path)

    elif extension == ".xlsx":

        return process_xlsx(file_path)

    elif extension == ".pptx":

        return process_pptx(file_path)

    elif extension in [
        ".png",
        ".jpg",
        ".jpeg"
    ]:

        return process_image(file_path)

    else:

        return {

            "error":
            f"Unsupported file type: {extension}"
        }