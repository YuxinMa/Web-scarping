from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Show_image import Image_pro
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import requests
import time
import pandas as pd
import sys

class Bolivia(object):

    def __init__(self):
        '''
            initialize objects that will be used in next
        '''

        # define the configuration of Chrome.webdriver
        driver_option = webdriver.ChromeOptions()
        driver_option.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        self.driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver',
                                  chrome_options=driver_option)

        #self.driver = webdriver.PhantomJS(executable_path='/Users/kayleyang/Desktop/Bolivia/phantomjs-2.1.1-macosx/bin/phantomjs')
        self.driver.get('https://djbr.contraloria.gob.bo/')

        # last name and first name and their corresponding selenium elements
        self.last_name, self.first_name = None, None
        self.LastName, self.FirstName = "Morales", "Evo"

        # selenium element for captcha
        self.captcha = None

        # captcha link
        self.link = None

        # temporary captcha
        self.img = None

        #
        self.table = None

        self.ind = []

    def Main(self, *args):
        self.table = None
        if args:
            self.LastName = args[1]
            self.FirstName = args[0]

        self.redirect()
        self.send_params(self.LastName, self.FirstName)

        i = 1
        while True:
            #txt = self.get_captcha()
            #self.__save_image()
            #self.send_captcha(txt)
            #time.sleep(1)

            if i >= 1:
                #self.captcha.clear()
                txt = input("captcha: ")
                if len(txt) == 4:
                    self.send_captcha(txt)
                    time.sleep(2)

            if not self.__captcha_error():
                self.get_table(s=5)
                break
            self.reload()
            i += 1


        if self.table:
            return self.get_entry()
        return [None] * 4

    # reloading captcha
    def reload(self):
        try:
            self.driver.find_element_by_xpath('//*[@id="FormBusquedaPublicaCaptcha"]/div/table[2]/tbody/tr[2]/td[2]/span[2]').click()
            time.sleep(1)
        except:
            pass

    # redirect to form where last_name and first name are input
    def redirect(self):
        self.driver.get('https://djbr.contraloria.gob.bo/')
        self.driver.find_element_by_xpath("//*[@id='tblOpcionesGenerales']/tbody/tr[1]/td[3]/a").click()
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'apellidos'))
            )
        finally:
            self.last_name = self.driver.find_element_by_id("apellidos")
            self.first_name = self.driver.find_element_by_id("nombres")

    # send params of names to the form
    def send_params(self, last_name, first_name):
        self.last_name.send_keys(last_name)
        self.first_name.send_keys(first_name)
        self.first_name.submit()

    # get captcha link and print it out then ask user to input the text of this captcha
    def get_captcha(self):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'imgCaptchaBusqueda'))
            )
        finally:
            self.link = self.driver.find_element_by_xpath('//*[@id="imgCaptchaBusqueda"]/img').get_attribute('src')
            self.__save_image()
            print(self.link)
            txt = Image_pro().main(self.img)
            return txt

    # send the text of captcha to server
    def send_captcha(self, txt):
        self.captcha = self.driver.find_element_by_id('imagen')
        self.captcha.send_keys(txt)
        self.captcha.submit()


    # get table in the pop-up part
    def get_table(self, s=2):
        try:
            element = WebDriverWait(self.driver, s).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'tablaresultados'))
            )
        finally:
            # get entry list
            table = self.driver.find_elements_by_class_name('tablaresultados')[-1]
            tr = table.find_elements_by_tag_name('tr')

            # choose entry when # > 1
            if len(tr) > 1:
                self.ind.append(' '.join([self.FirstName, self.LastName]))
                tmp = [i.find_elements_by_tag_name('td')[-1].find_element_by_tag_name('a') for i in tr
                            if i.find_elements_by_tag_name('td')[1].text == " ".join([self.FirstName, self.LastName]).upper()]
                if not tmp:
                    tmp = [i.find_elements_by_tag_name('td')[-1].find_element_by_tag_name('a') for i in tr
                            if i.find_elements_by_tag_name('td')[1].text.split(' ')[0] == self.FirstName.split(" ")[0].upper()]
                tmp[0].click()
            else:
                try:    # one entry
                    tr[0].find_element_by_xpath('//td[6]/a').click()
                except:     # no entry
                    return
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'divImpresion'))
                )
            finally:
                page = self.driver.page_source
                soup = BeautifulSoup(page)
                try:
                    self.table = soup.find('table', class_='tablaresultados tablaresultadosform')
                except:
                    self.table = None

    # get table contents
    def get_entry(self):
        tmp = self.table.find_all('tr', class_='FilaBlanca')[-4:]
        return [i.find_all('td')[2].getText(strip=True) for i in tmp]


    # test whether there is a error raised when sending captcha
    def __captcha_error(self):
        try:
            self.driver.find_element_by_id('divError_linkContinuar_Nuevo')
            self.captcha.clear()
            return True
        except:
            return False

    # save image of captcha to local file
    def __save_image(self):
        response = requests.get(self.link)
        self.img = Image.open(BytesIO(response.content))

if __name__ == '__main__':
    test = Bolivia()
    name = 'Cabinet_new.csv'
    da = pd.read_csv(name)

    # iterate over names
    dic = {}
    j = 0
    for i in range(j, da.shape[0]):
        print(i)
        table = test.Main(da['first_name'][i], da['last_name'][i])
        dic[i] = table

    def table(dic):
        tmp = [dic[i] for i in range(len(dic))]
        da = pd.DataFrame(tmp, columns=['Total "BIENES" (Activos)',
                                           'Total "DEUDAS" (Pasivos)',
                                           'PATRIMONIO NETO (Total "BIENES" menos Total "DEUDAS")',
                                           'Total "RENTAS" (Pasivos)'])

        # remove duplicates
        #lis1, lis2 = [], []
        #for i, j in enumerate(name):
        #   R if not j in lis2:
        #        lis2.append(j)
        #        lis1.append(i)
        return da

    # convert dictionary to data table
    da2 = table(dic)

    # concate
    da_final = pd.concat([da.drop(['first_name', 'last_name'], axis=1), da2], axis=1)
    da_final.to_csv(name.replace('_new.csv', '_disclosures.csv'))
