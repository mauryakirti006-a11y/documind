from pathlib import Path

import pymupdf
from docx import Document
import pandas as pd
from pptx import Presentation
from PIL import Image
import pytesseract


# Tell pytesseract where Tesseract OCR is installed
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# --------------------------------------------------
# PDF PROCESSING
# --------------------------------------------------

def process_pdf(file_path):

    document = pymupdf.open(file_path)

    pages = []

    for page_number, page in enumerate(document):

        # ------------------------------------------
        # STEP 1: Try normal PDF text extraction
        # ------------------------------------------

        text = page.get_text().strip()

        ocr_used = False

        # ------------------------------------------
        # STEP 2: Use OCR if PDF has little/no text
        # ------------------------------------------

        if len(text) < 20:

            # Render page as an image
            pix = page.get_pixmap(
                matrix=pymupdf.Matrix(1.7, 1.7),
                alpha=False
            )

            image = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            # --------------------------------------
            # STEP 3: Image preprocessing
            # --------------------------------------

            # Convert to grayscale
            image = image.convert("L")

            # Increase contrast
            from PIL import ImageOps

            image = ImageOps.autocontrast(image)

            # Resize slightly for better OCR
            new_width = int(image.width * 1.3)
            new_height = int(image.height * 1.3)

            image = image.resize(
                (new_width, new_height)
            )

            # --------------------------------------
            # STEP 4: OCR
            # --------------------------------------

            text = pytesseract.image_to_string(
                image,
                config="--psm 6"
            ).strip()

            ocr_used = True

        # ------------------------------------------
        # STEP 5: Store page result
        # ------------------------------------------

        pages.append({
            "page": page_number + 1,
            "text": text,
            "ocr_used": ocr_used
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

    for table in document.tables:

        rows = []

        for row in table.rows:

            rows.append([
                cell.text.strip()
                for cell in row.cells
            ])

        tables.append(rows)

    return {
        "type": "docx",
        "paragraphs": paragraphs,
        "tables": tables
    }


# --------------------------------------------------
# TXT PROCESSING
# --------------------------------------------------

def process_txt(file_path):

    with open(file_path, "r", encoding="utf-8") as file:

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
        "rows": dataframe.fillna("").to_dict(orient="records"),
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
            "rows": dataframe.fillna("").to_dict(orient="records")
        }

    return {
        "type": "xlsx",
        "sheets": sheets
    }


# --------------------------------------------------
# PPTX PROCESSING
# --------------------------------------------------

def process_pptx(file_path):

    presentation = Presentation(file_path)

    slides = []

    for slide_number, slide in enumerate(presentation.slides):

        slide_text = []

        for shape in slide.shapes:

            if hasattr(shape, "text"):

                text = shape.text.strip()

                if text:
                    slide_text.append(text)

        slides.append({
            "slide": slide_number + 1,
            "text": slide_text
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

    image = Image.open(file_path)

    text = pytesseract.image_to_string(image)

    return {
        "type": "image",
        "text": text.strip()
    }


# --------------------------------------------------
# MAIN FILE PROCESSOR
# --------------------------------------------------

def process_file(file_path):

    extension = Path(file_path).suffix.lower()

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

    elif extension in [".png", ".jpg", ".jpeg"]:

        return process_image(file_path)

    else:

        return {
            "error": f"Unsupported file type: {extension}"
        }