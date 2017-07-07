import json
import os
import sys
from lxml import html
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from pymongo import MongoClient
from time import sleep

class Dates:
    def __init__(self):
        self.format = '%m/%d/%Y'
        self._today = datetime.now()
        self.next = 0
        self._end = self._today - relativedelta(months=1)
        self._start = self._end + relativedelta(months=1)
        self.Date = namedtuple('Date', ['end', 'start'])
        self.begin = self.Date(self._start.strftime(self.format),
                               self._end.strftime(self.format))

    def __iter__(self):
        return self

    def __next__(self):
        if self.next == 0:
            self.next += 1
            return self.begin
        if self._end >= self._today:
            raise StopIteration
        else:
            self._start += relativedelta(months=1)
            self._end += relativedelta(months=1)
            date = self.Date(self._start.strftime(self.format)
                             , self._end.strftime(self.format))
            return date

class Spider():
    position = ''
    collection_name = ''
    def __init__(self):
        self.credentials = {}
        conn_string = ''
        mongodb_uri_exists = 'MONGODB_URI' in os.environ
        if mongodb_uri_exists:
            conn_string = os.environ['MONGODB_URI']
            self.credentials = {'website_username' : os.environ['WEBSITE_USERNAME'], 'website_password' : os.environ['WEBSITE_PASSWORD']}
        elif os.path.isfile('credentials.json'):
            self.credentials = json.loads(open('credentials.json').read())
            conn_string = 'mongodb://%s:%s@%s:%s/%s'
            conn_string = conn_string % (self.credentials['user'],
                                         self.credentials['password'],
                                         self.credentials['host'],
                                         self.credentials['port'],
                                         self.credentials['db'])
        client = MongoClient(conn_string)
        db = client['data']
        self.collection = db[self.collection_name]
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36 Edge/12.0")
        #wd = webdriver.PhantomJS(os.path.join(os.path.dirname(__file__), 'phantomjs'), desired_capabilities=dcap)
        wd = webdriver.PhantomJS('/app/phantomjs', desired_capabilities=dcap)
        self.wd = wd
        self.main_page()

    def main_page(self):
        print(' - - - Starting scraping')
        self.wd.get('https://www.basinlandrecords.com/hflogin.html')
        self.wd.find_element_by_name('FormUser').send_keys(self.credentials['website_username'])
        self.wd.find_element_by_name('FormPassword').send_keys(self.credentials['website_password'])
        self.wd.find_element_by_xpath(".//input[@type='submit']").click()
        self.wd.find_element_by_xpath(".//a[@href='/scripts/hfweb.asp']").click()
        self.wd.find_element_by_xpath(".//select/option[position()=%s]" % self.position).click()
        self.wd.find_element_by_xpath(".//input[@type='image']").click()

    def scraping_callback(self, date):
        pass

    def scrape(self):
        dates = Dates()
        for date in dates:
            for i in range(0, 3):
                try:
                    self.wd.find_element_by_name('detailsearch').click()
                    self.wd.find_element_by_name('ViewReferences').click()
                    self.wd.find_element_by_name('FIELD15').send_keys(date.start)
                    self.wd.find_element_by_name('FIELD15B').send_keys(date.end)
                    self.wd.find_elements_by_name('DataAction')[0].click()
                    break
                except NoSuchElementException:
                    sleep(60 * 5)
                    print('No such element exception')
                    self.main_page()
            self.scraping_callback(date)


class EddyScraper(Spider):
    def __init__(self):
        self.position = 1
        self.collection_name = 'basinland_eddy'
        super().__init__()

    def scraping_callback(self, date):
        document = html.fromstring(self.wd.page_source)
        items = []
        for tr in document.xpath(".//table[@cellpadding='4']//tr[not(@align='LEFT') and @valign='TOP']"):
            item = {}
            tds = tr.xpath('.//td')
            view_exists = True if 'VIEW' in ''.join(tds[1].xpath('.//text()')) else False
            item['reception_no'] = tds[2].text
            item['book_vol'] = tds[3].text
            item['page'] = tds[4].text
            item['clerk_instr_type'] = tds[5].text
            item['file_date'] = tds[6].text
            item['grantor'] = tds[7].text
            item['grantee'] = tds[8].text
            item['sub_blk_lot'] = tds[9].text
            item['sec_twp_rng'] = tds[10].text
            item['brief_legal'] = tds[11].text
            item['prior_reference'] = tds[12].text
            item['remarks'] = tds[13].text
            if view_exists:
                items.append(item)
            else:
                for key in item:
                    if item[key]:
                        items[-1][key] += '|' + item[key]

        self.collection.insert_many(items)
        print('Scraped ' + date.start + ' - ' + date.end + '. Items length: ' + str(len(items)))
        sleep(5)
        self.wd.find_element_by_xpath(".//a[@href='/scripts/hfweb.asp?Application=DAL&Database=EC']").click()


class LeaScraper(Spider):
    def __init__(self):
        self.position = 2
        self.collection_name = 'basinland_lea'
        super().__init__()

    def scraping_callback(self, date):
        document = html.fromstring(self.wd.page_source)
        items = []
        for tr in document.xpath(".//table[@cellpadding='4']//tr[not(@align='LEFT') and @valign='TOP']"):
            item = {}
            tds = tr.xpath('.//td')
            view_exists = True if 'VIEW' in ''.join(tds[1].xpath('.//text()')) else False
            item['reception_no'] = tds[2].text
            item['book_vol'] = tds[3].text
            item['page'] = tds[4].text
            item['clerk_instr_type'] = tds[5].text
            item['instr_date'] = tds[6].text
            item['file_date'] = tds[7].text
            item['grantor'] = tds[8].text
            item['grantee'] = tds[9].text
            item['sub_blk_lot'] = tds[10].text
            item['sec_twp_rng'] = tds[11].text
            item['brief_legal'] = tds[12].text
            item['prior_reference'] = tds[13].text
            item['remarks'] = tds[14].text
            if view_exists:
                items.append(item)
            else:
                for key in item:
                    if item[key]:
                        items[-1][key] += '|' + item[key]

        self.collection.insert_many(items)
        print('Scraped ' + date.start + ' - ' + date.end + '. Items length: ' + str(len(items)))
        sleep(5)
        self.wd.find_element_by_xpath(".//a[@href='/scripts/hfweb.asp?Application=DAL&Database=LC']").click()


if __name__ == '__main__':
    today = datetime.today()
    if today.day == 1:
        spider = None
        if sys.argv[1] == 'eddy':
            spider = EddyScraper()
        if sys.argv[1] == 'lea':
            spider = LeaScraper()
        spider.scrape()
