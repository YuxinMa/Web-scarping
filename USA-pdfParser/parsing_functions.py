from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer
import pandas as pd
import re


def extract_layout_by_page(fp):
    """
    Extracts LTPage objects from a pdf file.

    slightly modified from
    https://euske.github.io/pdfminer/programming.html
    """

    # Define layout of the page
    # char_margin: margin between characters to be grouped in one box
    # line_margin: margin between lines to be grouped in one box
    # word_margin: margin between characters to be grouped in one word
    #              (Whether a space should be inserted in two characters)
    laparams = LAParams(char_margin=0.5,
                        line_margin=0.2,
                        word_margin=20)

    # parser
    parser = PDFParser(fp)
    document = PDFDocument(parser)

    # if not document.is_extractable:
    #     raise PDFTextExtractionNotAllowed

    rsrcmgr = PDFResourceManager()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    layouts = []
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        layouts.append(device.get_result())

    return layouts


def extract_table_scheduleA(LT_elements):
    """
    Extract tables from Schedule A
    :param LT_elements:
    :return:
    """
    # column names:

    ASSET_, VALUE_, INCOME_, TYPE_, OWNER = None, None, None, None, None
    # define margin of columns
    for box in LT_elements:
        if 'asset' == box.get_text().strip().lower():
            ASSET_ = box.bbox[0] if not ASSET_ else ASSET_
        elif 'owner' == box.get_text().strip().lower():
            OWNER = box.bbox[0] if not OWNER else OWNER
        elif 'value' in box.get_text().lower():
            VALUE_ = box.bbox[0] if not VALUE_ else VALUE_
        elif box.get_text().lower().strip() == 'income' or \
            'current' in box.get_text().lower().strip():
            INCOME_ = box.bbox[0] if not INCOME_ else INCOME_
        elif 'type' in box.get_text().lower():
            TYPE_ = box.bbox[0] if not TYPE_ else TYPE_

    if not ASSET_:
        return []

    tables = [[[''] * 5, 1000]]
    # assign values to corresponding columns
    for box in LT_elements:
        if box.bbox[-1] < tables[-1][1]:
            tables.append([[''] * 5, box.bbox[1]])

        if box.bbox[0] == ASSET_:
            if box.width > OWNER - ASSET_:
                continue

            if ':' in box.get_text():
                continue

            if not box.get_text().strip().lower() == 'asset':
                if not re.match('^[A-Z0-9]', box.get_text().strip()):
                    continue

            tables[-1][0][0] = box.get_text().strip()
            tables[-1][1] = min(tables[-1][1], box.bbox[-1])
            # asset.append(box.get_text().strip())
        elif box.bbox[0] == OWNER:
            tables[-1][0][1] = box.get_text().strip()
            tables[-1][1] = min(tables[-1][1], box.bbox[-1])
        elif box.bbox[0] == VALUE_:
            # value.append(box.get_text().strip())
            tables[-1][0][2] = box.get_text().strip()
            tables[-1][1] = min(tables[-1][1], box.bbox[-1])
        elif box.bbox[0] == TYPE_:
            tables[-1][0][3] = box.get_text().strip()
            tables[-1][1] = min(tables[-1][1], box.bbox[-1])
            # income_type.append(box.get_text().strip())
        elif box.bbox[0] == INCOME_:
            tables[-1][0][4] = box.get_text().strip()
            tables[-1][1] = min(tables[-1][1], box.bbox[-1])
            # Income.append(box.get_text().strip())
    # return tables
    tables_res = [row[0] for row in tables if row[0][0] != '' or row[0][2] != '' or row[0][4] != '']
    try:
        header = [' '.join(i.split()) for i in tables_res[0]]
    except:
        print(tables_res)
        raise KeyboardInterrupt('end')
    # return pd.DataFrame(tables_res[1:], columns=header)
    return tables_res


"""
    # re-arrange values and fill empty entries (required for schedule A)
    new_asset = []
    new_type = []
    new_Income = []
    header = []

    for index, val in enumerate(asset):
        if index == 0:
            header.extend([asset[index], value.pop(0), income_type.pop(0), Income.pop(0)])
        else:
            # remove description lines
            if ":" in asset[index]:
                continue

            new_asset.append(val)
            try:
                new_type.append(income_type.pop(0))
            except:
                print(new_asset)
                print(new_Income)
                raise IndexError

            # fill empty entries
            if new_type[-1] == 'None':
                new_Income.append("None")
            elif Income:
                new_Income.append(Income.pop(0))
            else:
                new_Income.append("None")
    header = [' '.join(i.split()) for i in header]
    return pd.DataFrame(list(zip(new_asset, value, new_type, new_Income)), columns=header)
"""


def extract_table_scheduleD(LT_elements):
    """
    extract schedule D from pdf
    :param LT_elements:
    :return:
    """
    creditor = []
    date = []
    type_ = []
    amount = []

    CREDITOR, DATE, TYPE_, AMOUNT, OWNER = None, None, None, None, None

    # define margin of columns
    for box in LT_elements:
        if 'owner' == box.get_text().strip().lower():
            OWNER = box.bbox[0] if not OWNER else OWNER
        elif 'creditor' == box.get_text().strip().lower():
            CREDITOR = box.bbox[0] if not CREDITOR else CREDITOR
        elif 'date' in box.get_text().lower():
            DATE = box.bbox[0] if not DATE else DATE
        elif 'type' in box.get_text().lower():
            TYPE_ = box.bbox[0] if not TYPE_ else TYPE_
        elif 'amount' in box.get_text().lower():
            AMOUNT = box.bbox[0] if not AMOUNT else AMOUNT

    if not CREDITOR:
        return []
        # return pd.DataFrame()

    tables = [[[''] * 5, 1000]]
    # assign values to corresponding columns
    for box in LT_elements:
        if box.bbox[-1] < tables[-1][1]:
            tables.append([[''] * 5, box.bbox[1]])

        if box.bbox[0] == CREDITOR:
            if box.width > DATE - CREDITOR:
                continue

            if ':' in box.get_text():
                continue

            if not box.get_text().strip().lower() == 'creditor':
                if not re.match('^[A-Z0-9]', box.get_text().strip()):
                    continue
            tables[-1][0][1] = box.get_text().strip()
            tables[-1][1] = min(tables[-1][1], box.bbox[-1])
            # asset.append(box.get_text().strip())
        elif box.bbox[0] == OWNER:
            tables[-1][0][0] = box.get_text().strip()
            tables[-1][1] = min(tables[-1][1], box.bbox[-1])
        elif box.bbox[0] == DATE:
            # value.append(box.get_text().strip())
            tables[-1][0][2] = box.get_text().strip()
            tables[-1][1] = min(tables[-1][1], box.bbox[-1])
        elif box.bbox[0] == TYPE_:
            tables[-1][0][3] = box.get_text().strip()
            tables[-1][1] = min(tables[-1][1], box.bbox[-1])
            # income_type.append(box.get_text().strip())
        elif box.bbox[0] == AMOUNT:
            tables[-1][0][4] = box.get_text().strip()
            tables[-1][1] = min(tables[-1][1], box.bbox[-1])

    # assign values to corresponding columns
    """
    for box in LT_elements:
        if box.bbox[0] == CREDITOR:
            creditor.append(box.get_text().strip())
        elif box.bbox[0] == DATE:
            date.append(box.get_text().strip())
        elif box.bbox[0] == TYPE_:
            type_.append(box.get_text().strip())
        elif box.bbox[0] == AMOUNT:
            amount.append(box.get_text().strip())
    """

    # re-arrange values
    values = [row[0] for row in tables if row[0][-1]]
    try:
        headers = [' '.join(i.split()) for i in values[0]]
    except:
        print(values)
        print(LT_elements)
        raise KeyboardInterrupt ('end')
    # arrange values
    # return pd.DataFrame(values[1:], columns=headers)
    return values


def table_index(current_page, yes_no):
    """
    Split schedules into individual tables
    :param current_page:
    :return:
    """
    texts = []
    rects = []
    # seperate text and rectangle elements
    for e in current_page:
        if isinstance(e, pdfminer.layout.LTTextBoxHorizontal):
            texts.append(e)
        elif isinstance(e, pdfminer.layout.LTRect):
            rects.append(e)

    texts = sorted(texts, key=lambda x: -x.bbox[1])
    index_table = []

    for index, box in enumerate(texts):
        text = box.get_text().lower()

        if index < len(texts)-1 and \
                'yes' in texts[index+1].get_text().lower() and \
                'no' in texts[index+1].get_text().lower():
            yes_no.append([text.split(':')[0], texts[index+1].get_text().lower()])
            continue

        if 'schedule' in text:
            name = text.split(':')[0]
            if index_table:
                index_table[-1][1].append(index-1)
            index_table.append([name, [index + 1]])
            # print(index_table[-2:])

    if index_table:
        index_table[-1][1].append(-1)
    return index_table, texts

