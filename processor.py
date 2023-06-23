#!/usr/bin/python3

"""Modules for operating on different file types"""

import fitz
import os
import subprocess
import pytesseract
from PIL import Image
from pprint import pprint
from models.data_file import DataFile
import csv

# If you don't have tesseract executable in your PATH, include the following:
pytesseract.pytesseract.tesseract_cmd = os.path.realpath('/usr/bin/tesseract')

KEYWORDS = {
    'Invoice no.',
    'Payment date:',
    'SPECIAL DISCOUNT',
    'Discount',
    'Total CHF'
}


def merge_files(file1: DataFile, file2: DataFile) -> DataFile:
    """Merges two files and saves the resulting merged file"""
    _file1 = fitz.open(file1.path)
    _file2 = fitz.open(file2.path)
    # Merge the two files
    _file1.insert_file(_file2)
    # Save the merged file with a new filename
    merged_file_name: str = f'merged_{file1.name}_{file2.name}.pdf'
    merged_file_path: str = os.path.join(
        os.path.dirname(file1), merged_file_name)
    _file1.save(merged_file_path)
    return DataFile(merged_file_name, 'pdf', merged_file_path)


def extract_data(data_file: DataFile) -> list:
    """Extracts data from a list of files and returns key/value pairs of the data"""
    # Convert to image for OCR processing
    if data_file.type == 'pdf':
        data_file = convert_to_image_ocr(data_file)
    text_data: list = get_data_from_image_ocr(data_file)
    # Extract key/value pairs using predefined keywords
    extract: dict = get_key_values_from_data(text_data)
    return extract


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
    return result_data


def convert_to_pdf_ocr(pdf_file: DataFile) -> list:
    """Convert file to pdf ocr format"""
    data_results: list = []
    pdf = os.path.realpath(pdf_file.path)
    document = fitz.open(pdf)
    for page in document:
        text_results = get_pdf_ocr_content(page)
        data_results.append(text_results)
    return data_results


def convert_to_image_ocr(file: DataFile, block_box=[
                         0, 0, 500, 700]) -> DataFile:
    """Convert file to image ocr format"""
    document = fitz.open(file.path)
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
    output_path = os.path.join(os.path.dirname(file.path), f"{file.name}.png")
    output.ez_save(output_path)  # save output
    return DataFile(file.name, 'png', output_path)


def convert_image_to_pdf_ocr(image_file: DataFile):
    """Converts normal image to pdf ocr"""
    document = fitz.open()  # output PDF
    image = os.path.realpath(image_file.path)
    pix = fitz.Pixmap(image)  # make a pixmap form the image file
    # 1-page PDF with the OCRed image
    pdfbytes = pix.pdfocr_tobytes(language="eng")
    imgpdf = fitz.open("pdf", pdfbytes)  # open it as a PDF
    document.insert_pdf(imgpdf)  # append the image page to output
    # document.ez_save("ocr-pdf.pdf")  # save output
    return document


def get_pdf_ocr_content(page, block_box=[0, 0, 500, 700]) -> str:
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
        matrix=mat,
        clip=block_box,
    )
    ocrpdf = fitz.open("pdf", pix.pdfocr_tobytes())
    ocrpage = ocrpdf[0]
    text = ocrpage.get_text()
    if text.endswith("\n"):
        text = text[:-1]
    return text


def get_image_ocr_content(page, block_box=[0, 0, 500, 700]) -> str:
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


def get_data_from_image_ocr(file: DataFile) -> list:
    """Use pytesseract to get image ocr data"""
    image = Image.open(file.path)
    result_data = pytesseract.image_to_data(
        image, lang='eng', nice=0, output_type=pytesseract.Output.DICT)
    return result_data.get('text', [])


def write_data_to_csv(data: dict, file: DataFile) -> DataFile:
    """Writes data into a csv file"""
    csv_file_name = f"{file.name}.csv"
    csv_file_path = os.path.join(os.path.dirname(file.path), csv_file_name)
    with open(csv_file_path, mode='w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Extracted File Data'])
        [writer.writerow(data_extract) for data_extract in data.items()]
    return DataFile(file.name, 'csv', csv_file_path)


def read_csv_data(csv_file: DataFile) -> list:
    """Reads and returns csv file data contents"""
    result_data: dict = {}
    with open(csv_file.path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for index, row in enumerate(reader):
            if index == 0:
                result_data.update({row[0]: ''})
            else:
                result_data.update({row[0]: row[1]})
    return result_data
