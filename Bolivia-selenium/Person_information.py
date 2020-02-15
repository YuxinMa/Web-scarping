import requests, re, os
from bs4 import BeautifulSoup
import json, unidecode
import pandas as pd

class Senate_json(object):

    def __init__(self):
        self.url = None

        self.page = None
        self.soup = None
        self.info = {}
        if os.path.exists('Senate.json'):
            os.remove('Senate.json')

    def loop(self, url_list):
        for i in url_list:
            self.Main(i)

    def Main(self, url):
        self.url = url
        self.get_page()
        self.get_info()
        self.to_json()

    def get_page(self):
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content)

    def get_info(self):
        info = self.soup.find('div', class_='col-sm-10')
        tmp = [i for i in
                     info.find_all('div', class_=re.compile('field field-name-field-.* field-type-.* field-label-.*'))]
        self.info = {i.find('div', class_='field-label').getText(strip=True)[:-1]:
                         i.find('div', class_='field-items').getText().strip().split('\n') for i in tmp}

    def to_json(self):
        self.info['name'] = unidecode.unidecode(self.soup.find('h1', class_='page-header').getText(strip=True)).upper()
        if os.path.exists('Senate.json'):
            with open('Senate.json', 'a') as f:
                json.dump(self.info, f)
                f.write('\n')
        else:
            with open('Senate.json', 'w') as f:
                json.dump(self.info, f)
                f.write('\n')

class legisladores_json(object):

    def __init__(self):
        self.url = None
        self.page = None
        self.soup = None
        self.info = {}
        if os.path.exists('legisladores.json'):
            os.remove('legisladores.json')


    def loop(self, url_list):
        for i in url_list:
            self.Main(i)

    def Main(self, url):
        self.url = url
        self.get_page()
        self.get_info()
        self.to_json()

    def get_page(self):
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content)

    def get_info(self):
        info = self.soup.find('div', class_='col-xs-9 col-sm-9 ')
        tmp = [i for i in
                     info.find_all('div', class_=re.compile('field field-name-.* field-type-.* field-label-.*'))]
        self.info = {i.find('div', class_='field-label').getText(strip=True)[:-1]:
                         i.find('div', class_='field-items').getText().strip().split('\n') for i in tmp}

    def to_json(self):
        #self.info['name'] = unidecode.unidecode(self.soup.find('h1', class_='page-header').getText(strip=True)).upper()
        if os.path.exists('legisladores.json'):
            with open('legisladores.json', 'a') as f:
                json.dump(self.info, f)
                f.write('\n')
        else:
            with open('legisladores.json', 'w') as f:
                json.dump(self.info, f)
                f.write('\n')


if __name__ == '__main__':
    da1 = pd.read_csv('Senate_new.csv')
    test = Senate_json()
    test.loop(da1['link'])

    da2 = pd.read_csv("legisladores_new.csv")
    test2 = legisladores_json()
    test2.loop(da2['link'])

    # manipulate json - Senate
    with open('Senate.json', 'r') as f:
        tmp = f.readlines()
        json_senate = [json.loads(i) for i in tmp]

    # manipulate json - Legislative
    with open('legisladores.json', 'rb') as f:
        tmp = f.readlines()
        json_legis = [json.loads(i) for i in tmp]

    # construct data - Senate
    def extrac_value_Senate(dic):
        lis = ['Fecha de Nacimiento', 'Brigada', 'Bancada', 'Estudios', 'Comité']
        lis2 = ['Birthday', 'Brigade', 'Party', 'Education', 'Committee']
        col = []
        value = []
        for _, i in enumerate(lis):

            if not i in dic:
                dic[i] = dic.get(i, [None])
            elif not dic[i]:
                dic[i] = [None]

            if len(dic[i]) > 1:
                col += [lis2[_] + str(j + 1) for j in range(len(dic[i]))]
            else:
                col += [lis2[_]]
            value += dic[i]
        return pd.DataFrame([value], columns=col)

    tmp_da = pd.concat([extrac_value_Senate(i) for i in json_senate])
    tmp_da.index = range(tmp_da.shape[0])

    # load disclosures
    da_senate = pd.read_csv('Senate_disclosures.csv')

    # combine both
    Senate = pd.concat([da_senate, tmp_da], axis=1)
    Senate['Birthday'] = Senate['Birthday'].apply(lambda x: re.search('\d+.*\d+', x).group())
    Senate.to_csv('Senate_final.csv')

    # construct data - Legislative
    def extrac_value(dic):
        lis = ['Fecha de nacimiento', 'Brigada', 'Bancada', 'Diputación', 'Comisión']
        lis2 = ['Birthday', 'Brigade', 'Party', 'Diputation', 'Commission/Committee']

        col = []
        value = []
        for _, i in enumerate(lis):

            if not i in dic:
                dic[i] = dic.get(i, [None])
            elif not dic[i]:
                dic[i] = [None]

            if len(dic[i]) > 1:
                col += [lis2[_] + str(j+1) for j in range(len(dic[i]))]
            else:
                col += [lis2[_]]
            value += dic[i]
        return pd.DataFrame([value], columns=col)
    tmp_da = pd.concat([extrac_value(i) for i in json_legis])
    tmp_da.index = range(tmp_da.shape[0])

    # load disclosures
    da_legis = pd.read_csv('legisladores_disclosures.csv')

    # combine both
    legislative = pd.concat([da_legis, tmp_da], axis=1)
    legislative['Birthday'] = legislative['Birthday'].apply(lambda x: re.search('\d+.*\d+', x).group())
    legislative.to_csv('Legisladores_final.csv')