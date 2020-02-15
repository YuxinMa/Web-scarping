"""
PDFMiner:
`PDFParser`: fetches data from a file
`PDFDocument`: stored the data fetched by parser

Others:
`PDFPageInterpreter`: process the page contents
`PDFDevice`: translate it to whatever you need.
`PDFSourceManager`: store shared resources such as fonts or images

target schedules:
     Schedule A
     Schedule D

Target Categories:
     IPO
     TRUSTS
     EXEMPTION
"""
from .parsing_functions import extract_table_scheduleA
from .parsing_functions import extract_layout_by_page
from .parsing_functions import extract_table_scheduleD
from .parsing_functions import table_index
import pandas as pd
import io
import requests


class ScheduleParsing(object):

    def __init__(self, fp, url=True):
        """
        :param fp: file stream or file path
        """
        if type(fp) == str:
            if url:
                fp = io.BytesIO(requests.get(fp).content)
            else:
                fp = open(fp, 'rb')

        self.pagelayout = extract_layout_by_page(fp)
        self.previous = []
        self.data = {}
        self.var = None

    def main(self):
        funct = {
            "schedule a": extract_table_scheduleA,
            "schedule d": extract_table_scheduleD
        }

        previous = []
        yes_no = []
        for page in self.pagelayout:
            index_table, texts = table_index(page, yes_no)

            if previous:
                item = previous[-1][0]
                if index_table and index_table[0][1][0] == 1:
                    pass
                elif index_table:
                    span = [0, index_table[0][1][0] - 2]
                    index_table = [[item, span]] + index_table
                else:
                    span = [0, -1]
                    index_table = [[item, span]] + index_table

            for item, span in index_table:
                values = texts[span[0]: span[1] + 1] if span[1] != -1 else texts[span[0]:]
                self.previous.append([item, values])
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

        def categories(string):
            return string.split().index('nmlkji') == 0
        yes_no = {i: categories(j) for i, j in yes_no}

        # self.data['ScheduleA'] = pd.concat(scheduleA, axis=0)
        # self.data['ScheduleD'] = pd.concat(scheduleD, axis=0)
        def remove_page_block(tables):
            new_table = []
            for table in tables:
                if not new_table:
                    new_table += table
                else:
                    do_merge = False
                    for i in new_table[-1]:
                        if i.strip() and i.strip()[-1] == '-':
                            do_merge = True
                    if do_merge:
                        pre = new_table[-1]
                        cur = table[1]
                        new_table[-1] = [i + ' ' + j for i, j in zip(pre, cur)]
                        new_table += table[2:]
                    else:
                        new_table += table[1:]
            return new_table
        scheduleA = remove_page_block(scheduleA)
        scheduleD = remove_page_block(scheduleD)

        self.data['ScheduleA'] = pd.DataFrame(scheduleA[1:], columns=[' '.join(var.split()) for var in scheduleA[0]]) \
            if scheduleA else pd.DataFrame()
        self.data['ScheduleD'] = pd.DataFrame(scheduleD[1:], columns=[' '.join(var.split()) for var in scheduleD[0]]) \
            if scheduleD else pd.DataFrame()

        for i, j in yes_no.items():
            self.data[i] = j
        return



