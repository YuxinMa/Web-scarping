import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://otvoreniparlament.rs/poslanik/7949"
party_link = 'https://otvoreniparlament.rs/saziv/60'
names_link = 'https://otvoreniparlament.rs/poslanicki-klub/308'


class people:
    def __init__(self, link_person):
        self.link = link_person
        self.page = requests.get(self.link)
        self.soup = BeautifulSoup(self.page.content, "html.parser")

        # parse fields
        self.sections = self.getSections()
        self.all_sections = self.arrangeSections(self.sections)

        # concate fields
        self.data = pd.concat([value for value in self.all_sections.values()], axis=1)

    def getSections(self, tag='col-xs-12'):
        div = self.soup.find_all('div', class_='row')[1]
        section = div.find('div', class_=tag)
        return section.find_all('div', class_=tag)

    def arrangeSections(self, sections):
        all_sections = {}
        all_sections['profile'] = pd.DataFrame(['<sep>'.join([line.strip() for line in sections[0].getText().split('\n')
                                                if line.strip()])], columns=['profile'])
        all_sections['basic_info'] = self.basic_infor(sections[1])
        all_sections['statistics'] = self.statistics(sections[2])
        all_sections['membership'] = self.membership(sections[3])
        return all_sections

    def basic_infor(self, section):
        ul = section.find('ul').find_all('li')
        labels, values = zip(*[[val.label.getText(strip=True)[:-1], val.label.next_sibling.strip()]
                               for val in ul])
        # YOB: year of birth, DOB: date of birth
        mapping = {
            "Poslanički klub": "party_parliamentary_group",
            "Mesto prebivališta": "Place_of_residence",
            "Mesto rođenja": "Place_of_Birth",   ##
            "Godina rođenja": "Year_of_Birth",
            "Datum rođenja": "Date_of_Birth",    ##
            "Zanimanje": "Occupation"
        }

        colnames = [mapping[col] for col in labels]
        return pd.DataFrame([values], columns=colnames)

    def statistics(self, section, names=None):
        ul = section.find('ul').find_all('li')
        labels, values = zip(*[[val.label.getText(strip=True)[:-1], val.label.next_sibling.strip()]
                               for val in ul])
        mapping = {
            "Broj govora": "number_speeches",
            "Broj predloženih zakona": "num_proposed_law",
            "Broj podnetih amandmana": "num_proposed_amendments",
            "Broj usvojenih amandmana": "num_accepted_amendments",
            "Pitanja građana": "questions from citizens" ##
        }
        colnames = [mapping[col] for col in labels]
        return pd.DataFrame([values], columns=colnames)

    def membership(self, section):
        ul = section.find('div', class_='js-eq-limit').find_all('p')
        values = [val.getText(strip=True) for val in ul]
        colnames = ['mem' + str(i+1) for i in range(len(values))]
        return pd.DataFrame([values], columns=colnames)


class names(object):
    def __init__(self, names_link):
        self.link = names_link
        self.page = requests.get(self.link)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')

    def getLinks(self):
        contents = self.soup.find('div', class_='card-content').findNext('div', class_='card-content')
        name_tags = contents.find_all('h4', class_='media-heading')
        return pd.DataFrame([[i.getText(strip=True), i.find('a').get('href')] for i in name_tags],
                            columns=['names', 'profile_urls'])


class party(object):
    def __init__(self, party_link):
        self.link = party_link
        self.page = requests.get(self.link)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')

    def getLinks(self):
        ul = self.soup.find('div', class_='card-content').find_next('div', class_='card-content').ul
        name_tags = ul.find_all('li')
        return pd.DataFrame([[i.getText(strip=True), i.find('a').get('href')] for i in name_tags],
                            columns=['party_names', 'party_urls'])

if __name__ == '__main__':
    # test = people(url)
    # test_party = party(party_link)
    # test_archive = names(names_link)

    # function: assign a `col` of `val` to `data`
    def fun1(data, cols, vals):
        if not isinstance(cols, list):
            data[cols] = vals
        for col, val in zip(cols, vals):
            data[col] = val
        return data

    party_links = {"2008_2012": "http://otvoreniparlament.rs/saziv/59",
                   "2012_2014": "http://otvoreniparlament.rs/saziv/60",
                   "2014_2016": "http://otvoreniparlament.rs/saziv/61"}
    da_year_links = pd.DataFrame(list(party_links.items()), columns=['time_range', 'urls'])

    # fetch party list from each time_range
    data_1 = da_year_links.apply(lambda x: fun1(party(x[1]).getLinks(), 'time_range', x[0]), axis=1)
    da_party_links = pd.concat(list(data_1), axis=0)
    da_party_links.index = range(da_party_links.shape[0])

    # fetch name_list from each party
    data_2 = da_party_links.apply(lambda x: fun1(names(x['party_urls']).getLinks(), ['party_names', 'time_range'],
                                                 x[['party_names', 'time_range']]), axis=1)
    da_name_links = pd.concat(list(data_2), axis=0)
    da_name_links.index = range(da_name_links.shape[0])

    # fetch profiles from each name_urls
    data_3 = da_name_links.apply(lambda x: fun1(people(x['profile_urls']).data, ['time_range', 'party_names', 'names'],
                                                x[['time_range', 'party_names', 'names']]), axis=1)
    da_profile = pd.concat(list(data_3), axis=0, sort=False)
    da_profile.index = range(da_profile.shape[0])

    # output
    da_profile.drop(["Place_of_Birth", "Date_of_Birth", "questions from citizens"], axis=1).\
        to_csv("parliament_profiles.csv", index=False)
