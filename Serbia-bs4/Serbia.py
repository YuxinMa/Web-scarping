import requests
import re
import pandas as pd

action = "http://www.acas.rs/acasPublic/funkcionerSearch.htm"

class Serbia(object):
    def __init__(self, params):
        action = "http://www.acas.rs/acasPublic/funkcionerSearch.htm"
        self.params = {'iDisplayStart': 0, 'iDisplayLength': 1}
        self.params.update(params)

        # post the first post
        self.page = requests.get(action, params=self.params)
        self.jsons = self.page.json()

        # retrieve the number of records
        TotalNumber = self.jsons['iTotalRecords']

        # rePost requests
        self.params['iDisplayStart'] = 0
        self.params['iDisplayLength'] = TotalNumber
        self.page = requests.get(action, params=self.params)
        self.Data = self.page.json()['aaData']

class Serbia_getData(Serbia):
    def __init__(self, params=[("funkcija.id", "3")]):
        """
        :param params: params to send requests:
                       parliament: [("funkcija.id", "3")]
                       cabinet: [("organizacija.id", "5676")]
        """
        Serbia.__init__(self, params=dict(params))
        # build data table
        new_data = []
        for i in self.Data:
            ids = self.find_all_id(i[-1])
            dates = self.find_all_date(i[-1])
            for j in range(len(ids)):
                new_data.append(i[:-1] + [ids[j], dates[j]])
        self.table = pd.DataFrame(new_data, columns=["Names", "Position", "Active", "Organization", "Ids", "Dates"])

    def find_all_id(self, query):
        return re.findall('prikazIzvestaja\(([0-9]+)\)', query)

    def find_all_date(self, query):
        return re.findall('[0-9]{2}\.[0-9]{2}\.[0-9]{4}', query)



if __name__ == '__main__':
    test_parliament = Serbia_getData(params=[("funkcija.id", "3")])
    test_cabinet = Serbia_getData(params=[("organizacija.id", "5676")])

    # output data
    test_parliament.table.to_csv("Parliament_nameList.csv", index=False)
    test_cabinet.table.to_csv("Cabinet_nameList.csv", index=False)


