#!/usr/bin/python3

""""""

import fitz
from pprint import pprint

KEYWORDS=['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.']

def merge_file(file1_name, file2_name):
    """"""
    file1 = fitz.open(file1_name)
    file2 = fitz.open(file2_name)
    # Merge the two files
    file1.insert_file(file2)
    # Save the merged file with a new filename
    file1.save(f'merged_{file1_name}_{file2_name}.pdf')

def extract_data(files):
    """"""
    result_data: dict = {}
    for file_name, file_type in files:
        file = fitz.open(file_name)

        # Iterate the pages
        for page in range(len(file)):
            words = file[page].get_text('words', sort=False)
            extract = extract_keywords(words)
            if extract:
                result_data.update(extract)
    pprint(result_data)
    return list(map(tuple, extract.items()))

def extract_keywords(words, keywords=KEYWORDS) -> dict:
    """"""
    result_data: dict = {}
    # Retrieve the information needed to extract data from the prefix keywords
    for index, word in enumerate(words):
        key = word[4]
        if key in keywords:
            value = words[index + 1][4]
            result_data[key] = value
    pprint(result_data)
    return result_data
