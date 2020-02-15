import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

url = "http://www.acas.rs/acasPublic/izvestajDetails.htm?parent=pretragaFunkcionera&izvestajId="

class fetch_data(object):
    def __init__(self, id):
        self.url = url + str(id)
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content, "html.parser")
        self.tables = self.soup.find_all("table", class_="table1")

        self.record = self.getColumns()
        self.dataframe_record = {}
        self.dataframe_record["Income"] = self.reFormat("Income", ["period", "netIncome", "Unit"])
        self.dataframe_record["Property"] = self.reFormat("Property", ["type"])
        self.dataframe_record["Vehicle"] = self.reFormat("Vehicle", ["type", "brand", "year"])

        self.data = pd.concat([i for i in self.dataframe_record.values()], axis=1)
        self.data["Name"] = self.record["Name"]
        self.data["Date"] = self.record["Date"]
        self.data["IsDeposit"] = self.record["IsDeposit"]

    def getColumns(self):
        record = {}
        record["Name"] = self.tables[1].find("td", class_="tdCell").getText(strip=True)
        record["Date"] = self.tables[-1].find("td", class_="tdCell").getText(strip=True).split()[-1]

        record["IsDeposit"] = self.tables[5].find_all("td", class_="tdCell")[1].find("img") is None

        record["Income"] = [[col.getText(strip=True) for col in row.find_all("td", class_="tdCell")[3:6]]
                            for row in self.tables[2].find_all("tr")[1:]]

        record["Property"] = [[row.find_all("td", class_="tdCell")[0].getText(strip=True)]
                              for row in self.tables[3].find_all("tr")[1:]]

        record["Vehicle"] = [[col.getText(strip=True) for col in row.find_all("td", class_="tdCell")[:3]]
                             for row in self.tables[4].find_all("tr")[1:]]
        return record

    def reFormat(self, field, names):
        if not self.record[field]:
            return pd.DataFrame()
        data = self.record[field]
        colnames = []
        colvalues = []
        for i, row in enumerate(data):
            colnames += [field + "_" + j + "_{}".format(i+1) for j in names]
            colvalues += row
        return pd.DataFrame([colvalues], columns=colnames)

if __name__ == '__main__':
    test = fetch_data(2296)
    idList = []
    res = []
    file_path = "Parliament_nameList.csv"
    output_path = "Parliament_disclosure.csv"
    data = pd.read_csv(file_path)

    for id in data["Ids"]:
        print("Now work on:", id)
        test.__init__(id)
        res.append(test.data)

    res = pd.concat(res, axis=0)
    res.index = range(res.shape[0])

    final = pd.concat([data, res], axis=1)
    assert sum(final["Names"] == final["Name"])==final.shape[0]
    final.drop("Name", axis=1).to_csv(output_path)




