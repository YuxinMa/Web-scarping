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

sample_path = "/home/yikang/Dropbox/disclosures-data/Yikang-Yang/United_States/data_2019/2019_Amash,Hon.Justin_MI03_PTR Original.pdf"
sample_path2 = "/home/yikang/Dropbox/disclosures-data/Yikang-Yang/United_States/data_2017/2017_Beatty,Hon.Joyce_OH03_FD Original.pdf"
sample_path3 = "/home/yikang/Dropbox/disclosures-data/Yikang-Yang/United_States/data_2017/2017_Boyle,Hon.BrendanF._PA13_FD Original.pdf"

def extract_layout_by_page(pdf_path):
    """
    Extracts LTPage objects from a pdf file.

    slightly modified from
    https://euske.github.io/pdfminer/programming.html
    """
    laparams = LAParams(char_margin=0.5,
                        line_margin=0.05,
                        word_margin=20)

    fp = open(pdf_path, 'rb')
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

TEXT_ELEMENTS = [
    pdfminer.layout.LTTextBox,
    pdfminer.layout.LTTextBoxHorizontal,
    pdfminer.layout.LTTextLine,
    pdfminer.layout.LTTextLineHorizontal
]


def flatten(lst):
    """Flattens a list of lists"""
    return [subelem for elem in lst for subelem in elem]


def extract_characters(element):
    """
    Recursively extracts individual characters from
    text elements.
    """
    if isinstance(element, pdfminer.layout.LTChar):
        return [element]

    if any(isinstance(element, i) for i in TEXT_ELEMENTS):
        return flatten([extract_characters(e) for e in element])

    if isinstance(element, list):
        return flatten([extract_characters(l) for l in element])

    return []


pagelayout = extract_layout_by_page(sample_path2)


import pandas as pd


def extract_table_scheduleA(LT_elements):
    """
    Extract tables from Schedule A
    :param LT_elements:
    :return:
    """
    asset = []
    value = []
    income_type = []
    Income = []

    # define margin of columns
    for box in LT_elements:
        if 'asset' == box.get_text().strip().lower():
            ASSET_ = box.bbox[0]
        elif 'value' in box.get_text().lower():
            VALUE_ = box.bbox[0]
        elif box.get_text().lower().strip() == 'income':
            INCOME_ = box.bbox[0]
        elif 'income' in box.get_text().lower():
            TYPE_ = box.bbox[0]

    # assign values to corresponding columns
    for box in LT_elements:
        if box.bbox[0] == ASSET_:
            asset.append(box.get_text().strip())
        elif box.bbox[0] == VALUE_:
            value.append(box.get_text().strip())
        elif box.bbox[0] == TYPE_:
            income_type.append(box.get_text().strip())
        elif box.bbox[0] == INCOME_:
            Income.append(box.get_text().strip())

    # arrange values
    new_asset = []
    new_type = []
    new_Income = []
    header = []

    for index, val in enumerate(asset):
        if index == 0:
            header.extend([asset[index], value.pop(0), income_type.pop(0), Income.pop(0)])
        else:
            if ":" in asset[index]:
                continue
            new_asset.append(val)

            new_type.append(income_type.pop(0))

            if new_type[-1] == 'None':
                new_Income.append("None")
            elif Income:
                new_Income.append(Income.pop(0))
            else:
                new_Income.append("None")
    header = [' '.join(i.split()) for i in header]
    return pd.DataFrame(list(zip(new_asset, value, new_type, new_Income)), columns=header)


def extract_table_scheduleD(LT_elements):
    creditor = []
    date = []
    type_ = []
    amount = []

    # define margin of columns
    for box in LT_elements:
        if 'creditor' == box.get_text().strip().lower():
            CREDITOR = box.bbox[0]
        elif 'date' in box.get_text().lower():
            DATE = box.bbox[0]
        elif 'type' in box.get_text().lower():
            TYPE_ = box.bbox[0]
        elif 'amount' in box.get_text().lower():
            AMOUNT = box.bbox[0]

    # assign values to corresponding columns
    for box in LT_elements:
        if box.bbox[0] == CREDITOR:
            creditor.append(box.get_text().strip())
        elif box.bbox[0] == DATE:
            date.append(box.get_text().strip())
        elif box.bbox[0] == TYPE_:
            type_.append(box.get_text().strip())
        elif box.bbox[0] == AMOUNT:
            amount.append(box.get_text().strip())

    values = list(zip(creditor, date, type_, amount))
    headers = [' '.join(i.split()) for i in values[0]]
    # arrange values
    return pd.DataFrame(values[1:], columns=headers)


def table_index(current_page):
    global yes_no
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

        if 'yes' in text and 'no' in text:
            yes_no.append(text)
            continue

        if 'schedule' in text:
            name = text.split(':')[0]
            print(name, index)
            if index_table:
                index_table[-1][1].append(index-1)
            index_table.append([name, [index + 1]])

    if index_table:
        index_table[-1][1].append(-1)
    return index_table, texts

funct = {
    # "schedule a": extract_table_scheduleA,
    "schedule b": lambda x: x,
    "schedule c": lambda x: x,
    "schedule d": extract_table_scheduleD
}

previous = []
yes_no = []
for page in pagelayout:
    current = []
    index_table, texts = table_index(page)

    if previous:
        item = previous[-1][0]
        if index_table:
            span = [0, index_table[0][1][0]-2]
        else:
            span = [0, -1]
        index_table = [[item, span]] + index_table

    for item, span in index_table:
        values = texts[span[0]: span[1]+1] if span[1] != -1 else texts[span[0]:]
        if item in funct:
            values = funct[item](values)
        previous.append([item, values])

# pick schedule A and schedule D
scheduleA = []
scheduleD = []

for item, values in previous:
    if item == 'schedule a':
        scheduleA.append(values)
    elif item == 'schedule d':
        scheduleD.append(values)

scheduleA = pd.concat(scheduleA, axis=0)
scheduleD = pd.concat(scheduleD, axis=0)
yes_no = [i.split().index('nmlkji') == 0 for i in yes_no]

