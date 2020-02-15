import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import unidecode

class Senate(object):
    def __init__(self):
        self.url = 'http://senado.gob.bo/legislativa/brigadas'
        self.host = 'http://senado.gob.bo'

        self.page = None
        self.soup = None

        self.table = None
        self.data = None

    def Main(self):
        self.get_page()
        self.get_name()
        self.refine_table()
        self.clean_table()
        self.data.to_csv('Senate_new.csv')

    def get_page(self):
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content)

    def get_name(self):
        tmp = self.soup.find_all('div', class_='col col-lg-3')
        self.table = [[self.host+i.find_all('a')[1].get('href'), i.find_all('a')[1].getText(strip=True)] for i in tmp]

    def refine_table(self):
        self.data = pd.DataFrame(self.table, columns=['link', 'name'])
        self.data.to_csv('Senate.csv')

    def clean_table(self):
        def split(x):
            tmp = x.split(' ')
            if len(tmp) > 2:
                return ' '.join(tmp[-2:]), ' '.join(tmp[:-2])
            else:
                return tmp[1], tmp[0]
        self.data['name'] = self.data['name'].apply(lambda x: unidecode.unidecode(x))
        self.data['last_name'] = self.data['name'].apply(lambda x: split(x)[0])
        self.data['first_name'] = self.data['name'].apply(lambda x: split(x)[1])

##
class legisladores(object):

    def __init__(self):
        self.url = 'http://www.diputados.bo/legisladores'
        self.host = 'http://www.diputados.bo'
        self.page_num = 0
        self.table = None
        self.data = None

        self.dic = []

    def Main(self):
        for i in range(5):
            self.loop_page(i)
        tmp = pd.DataFrame(self.dic, columns=['link', 'name'])
        tmp.to_csv('legisladores.csv')
        self.clean_table(tmp).to_csv('legisladores_new.csv')

    def loop_page(self, num):
        self.page_num = num
        self.table = self.get_Page()
        self.get_Name()

        self.dic += self.data

    def get_Page(self):
        page = requests.get(self.url + '?page='+str(self.page_num))
        soup = BeautifulSoup(page.content)
        return soup.find('table')

    def get_Name(self):
        tmp = self.table.find_all('tr')
        Name = [i.find('td').find('a') for i in tmp[1:]]
        self.data = [[self.host + i.get('href'), i.getText(strip=True)] for i in Name]


    def clean_table(self, da):
        da['name'] = da['name'].apply(lambda x: re.search('[^\(]+', x).group().strip())
        def split(x):
            tmp = x.split(' ')
            if len(tmp) > 2:
                return ' '.join(tmp[-2:]), ' '.join(tmp[:-2])
            else:
                return tmp[1], tmp[0]

        da['name'] = da['name'].apply(lambda x: unidecode.unidecode(x))
        da['last_name'] = da['name'].apply(lambda x: split(x)[0])
        da['first_name'] = da['name'].apply(lambda x: split(x)[1])
        return da

class Cabinet(object):

    def __init__(self):
        self.url = 'http://www.mingobierno.gob.bo/index.php?r=page/detail&id=37'

        self.page = None
        self.table = None
        self.data = None

    def Main(self):
        self.get_page()
        da = pd.DataFrame(self.get_name(), columns=['name'])
        da.to_csv('Cabinet.csv')
        self.clean_table(da).to_csv('Cabinet_new.csv')

    def get_page(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content)
        self.table = soup.find('table')

    def get_name(self):
        tmp = [i.find_all('p')[-1].getText(strip=True) for i in self.table.find_all('td')[:-1]]
        tmp = [i.replace(re.search('[a-z]{1}([A-Z]+.*)', i).group(1), '') for i in tmp]
        return [re.sub('.*\.', '', i).strip() for i in tmp]

    def clean_table(self, da):
        def split(x):
            tmp = x.split(' ')
            if len(tmp) > 2:
                return ' '.join(tmp[-2:]), ' '.join(tmp[:-2])
            else:
                return tmp[1], tmp[0]

        da['name'] = da['name'].apply(lambda x: unidecode.unidecode(x))
        da['last_name'] = da['name'].apply(lambda x: split(x)[0])
        da['first_name'] = da['name'].apply(lambda x: split(x)[1])
        return da

# Senate
if __name__ == '__main__':
    Senate().Main()
    legisladores().Main()
    Cabinet().Main()
