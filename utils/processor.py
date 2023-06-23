#!/usr/bin/python3

"""Modules for utility functions"""

import fitz
import os
import subprocess
import pytesseract
from PIL import Image
from pprint import pprint

# If you don't have tesseract executable in your PATH, include the following:
pytesseract.pytesseract.tesseract_cmd = os.path.realpath('/usr/bin/tesseract')

KEYWORDS = {
    'Invoice no.',
    'Payment date:',
    'SPECIAL DISCOUNT',
    'Discount',
    'Total CHF'
}


def merge_files(file1_name: str, file2_name: str) -> str:
    """Merges two files and saves the resulting merged file"""
    file1 = fitz.open(file1_name)
    file2 = fitz.open(file2_name)
    # Merge the two files
    file1.insert_file(file2)
    # Save the merged file with a new filename
    merged_file: str = f'merged_{file1_name}_{file2_name}.pdf'
    file1.save(merged_file)
    return merged_file


def extract_data(files: list) -> list:
    """Extracts data from a list of files and returns key/value pairs of the data"""
    result_data: dict = {}
    for file in files:
        file_name, file_type, full_path = file
        # Convert to image for OCR processing
        if file_type == 'pdf':
            file = convert_to_image_ocr(file)
        text_data: list = get_data_from_image_ocr(file)
        # Extract key/value pairs using predefined keywords
        extract = get_key_values_from_data(text_data)
        # Update the dictionary data
        if extract:
            result_data.update(extract)

    # pprint(result_data)
    return result_data


def get_key_values_from_data(words: list, keywords: set = KEYWORDS) -> dict:
    """Gets all key/value pairs from predefined keywords"""
    result_data: dict = {}
    # Retrieve the information needed to extract data from the prefix keywords
    for index, key in enumerate(words):
        # Match the keyword
        if key in keywords:
            # Extract the value
            value = words[index + 1]
            result_data[key] = value
    # pprint(result_data)
    return result_data


def convert_to_pdf_ocr(pdf_file):
    """Convert file to pdf ocr format"""
    data_results: list = []
    file_name, file_type, file_path = pdf_file
    pdf = os.path.realpath(file_path)
    document = fitz.open(pdf)
    for page in document:
        text_results = get_pdf_ocr_content(page)
        data_results.append(text_results)
    return data_results


def convert_to_image_ocr(file, block_box=[0, 0, 500, 700]):
    """Convert file to image ocr format"""
    file_name, file_type, full_path = file

    document = fitz.open(full_path)
    page = document[0]
    mat = fitz.Matrix(5, 5)  # high resolution matrix
    pix = page.get_pixmap(
        colorspace=fitz.csGRAY,  # we need no color
        matrix=mat,
        clip=block_box,
    )

    img_bytes = pix.tobytes("png")  # make a PNG image
    output = fitz.open()
    img = fitz.open('png', img_bytes)  # output Image
    output.insert_file(img)  # append the image page to output
    output_name = f"{file_name.split('.')[0]}.png"
    output_path = os.path.join(os.path.dirname(full_path), output_name)
    output.ez_save(output_name)  # save output
    return (output_name, 'png', output_path)


def convert_image_to_pdf_ocr(image_file):
    """Converts normal image to pdf ocr"""
    document = fitz.open()  # output PDF
    img_name, img_type, img_path = image_file
    image = os.path.realpath(img_path)
    pix = fitz.Pixmap(image)  # make a pixmap form the image file
    # 1-page PDF with the OCRed image
    pdfbytes = pix.pdfocr_tobytes(language="eng")
    imgpdf = fitz.open("pdf", pdfbytes)  # open it as a PDF
    document.insert_pdf(imgpdf)  # append the image page to output
    # document.ez_save("ocr-pdf.pdf")  # save output
    return document


def get_pdf_ocr_content(page, block_box=[0, 0, 500, 700]):
    """Return OCR-ed span text using Tesseract.

    Args:
        page: fitz.Page
        block_box: fitz.Rect or its tuple
    Returns:
        The OCR-ed text of the block_box.
    """
    mat = fitz.Matrix(5, 5)  # high resolution matrix
    pix = page.get_pixmap(
        colorspace=fitz.csGRAY,  # we need no color
        # matrix=mat,
        # clip=block_box,
    )
    ocrpdf = fitz.open("pdf", pix.pdfocr_tobytes())
    ocrpage = ocrpdf[0]
    text = ocrpage.get_text()
    if text.endswith("\n"):
        text = text[:-1]
    return text


def get_image_ocr_content(page, block_box=[0, 0, 500, 700]):
    """Return OCR-ed span text using Tesseract.

    Args:
        page: fitz.Page
        block_box: fitz.Rect or its tuple
    Returns:
        The OCR-ed text of the block_box.
    """
    mat = fitz.Matrix(5, 5)  # high resolution matrix
    tess = "tesseract stdin stdout --psm 7 -l eng"
    pix = page.get_pixmap(
        colorspace=fitz.csGRAY,  # we need no color
        matrix=mat,
        clip=block_box,
    )

    image = pix.tobytes("png")  # make a PNG image
    # Step 2: Invoke Tesseract to OCR the image. Text is stored in stdout.
    rc = subprocess.run(
        tess,  # the command
        input=image,  # the pixmap image
        stdout=subprocess.PIPE,  # find the text here
        shell=True,
    )

    # because we told Tesseract to interpret the image as one line, we now need
    # to strip off the line break characters from the tail.
    text = rc.stdout.decode()  # convert to string
    text = text[:-3]  # remove line end characters
    return text


def get_data_from_image_ocr(file) -> list:
    """Use pytesseract to get image ocr data"""
    file_name, file_type, file_path = file
    image = Image.open(file_path)
    result_data = pytesseract.image_to_data(
        image, lang='eng', nice=0, output_type=pytesseract.Output.DICT)
    return result_data.get('text', [])
