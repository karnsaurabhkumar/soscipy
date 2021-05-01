import time
import re
import unicodedata
import urllib.request

import pandas as pd
from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select


def remove_none(L):
    return [x for x in L if x is not None]


def delhi_HC_scraper():
    return delhi_hc_search()


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

class delhi_hc_search:
    def __init__(self, case_type, case_year, case_no=None, headless=True, no_image=True, delay=1, ret=False):
        """
        The Delhi High court website provides three ways to look for case data:
        1. Using Case type
        2. Using petitioner and respondents information
        3. Using Advocate information
        4. Using diary no. information

        This object provides a way to look for the bulk data using case type. Hence, to initialise we require
        three parameters

        case_type: string, an element in the list of options provided by the high court website that categorises a case
        case_no: int, case no. registered in the high court
        case_year: int, Year of registering the case in yyyy
        """

        self.url = "http://delhihighcourt.nic.in/case.asp"
        self.case_type = case_type
        self.case_no = case_no
        self.case_year = str(case_year)

        """
        Browser configuration
        Certain optimisations have been done to reduce the chrome overload which anyways is much higher. 
        Parameters i.e. headless, no_image
        """
        self.headless = headless
        self.no_image = no_image
        self.elements = {}

        """
        This is the meat of the scraper which tells the code where a specific piece of content can be found
        on the webpage.
        """
        self.elements['case_type'] = "//*[@id='InnerPageContent']/form[1]/select[1]"
        self.elements['case_type_elem'] = "//*[@id='InnerPageContent']/form[1]/select[1]"
        self.elements['case_no'] = "//*[@id='InnerPageContent']/form[1]/input[1]"
        self.elements['case_year_elem'] = "//*[@id='c_year']"
        self.elements['captcha_text_input'] = "//*[@id='inputdigit']"
        self.elements['captcha_text_value'] = "//*[@id='InnerPageContent']/form[1]/label[4]"
        self.elements['search_but'] = "//*[@id='InnerPageContent']/form[1]/button"

        # Keeping a global name for case_type_select element
        self.case_type_select = None
        self.case_type_options = None
        self.delay = delay
        self.ret = ret
        self.order_subpage_data = []

        # Assertions
        if self.case_no:
            assert type(self.case_no) == int, "Case no. must be an integer"
        assert (type(case_year) == int) & (len(str(case_year)) == 4), "Case no. must be an year in YYYY format"

    def _delay(self):
        # Spleep function that delays page load. Usually to avoid overloading the server
        time.sleep(self.delay)

    def get_case_type_options(self):
        # Fetches the case type options from the dropdown menue
        case_type_select = Select(self.driver.find_element_by_xpath(self.elements['case_type']))
        self.case_type_options = [(ind, opt.text) for ind, opt in enumerate(case_type_select.options)]
        # print(self.case_type_options)

    def get_search_page(self):
        # Calls the setup method to create a browser driver
        self.setup()
        # Fetch the URL for the delhi highcourt
        self.driver.get(self.url)
        # Fetch all the case type options from the
        self.get_case_type_options()

    def get_captcha_text(self):
        self.captcha_text_val = self.driver.find_element_by_xpath(self.elements['captcha_text_value'])
        self.captcha_text_val = self.captcha_text_val.text.split(" ")[2]

    def set_case_type(self):
        case_type_select = Select(self.driver.find_element_by_xpath(self.elements['case_type']))
        case_type_select.select_by_index(self.case_type)
        print(f'Selecting case type {self.case_type_options[self.case_type][1]}')

    def set_case_no(self):
        if self.case_no:
            case_type_select = self.driver.find_element_by_xpath(self.elements['case_no'])
            case_type_select.send_keys(self.case_no)
            print(f'Selecting case no {self.case_no}')

    def set_case_year(self):
        case_year_select = Select(self.driver.find_element_by_xpath(self.elements['case_year_elem']))
        case_year_select.select_by_value(self.case_year)

    def set_captcha_text(self):
        captcha_text = self.driver.find_element_by_xpath(self.elements['captcha_text_input'])
        captcha_text.send_keys(self.captcha_text_val)

    def set_param(self):
        self.get_search_page()
        self._delay()
        self.set_case_type()
        self._delay()
        self.set_case_no()
        self._delay()
        self.set_case_year()
        self._delay()
        self.get_captcha_text()
        self.set_captcha_text()

    def get_search_results(self):
        # Set search parameters
        self.set_param()

        # find search button and click on it
        search_but = self.driver.find_element_by_xpath(self.elements['search_but'])
        search_but.click()
        self.get_search_count()

    def start_scraping(self, order_links=[], pdf_links=[]):
        self.get_search_results()
        print(f'Total search results: {self.search_count}')
        self.page_visited = []
        self.page_not_visited = []
        # seed page no visited
        nav_links_curr_page = [element.get_attribute('href')
                               for element in
                               self.driver.find_elements_by_class_name('archivelink')]

        for link in nav_links_curr_page:
            self.page_not_visited.append(link)

        self.valid_links = remove_none(list(set(self.page_not_visited) - set(self.page_visited)))
        page_counter = 0
        data = []
        while self.valid_links:
            print(f'No. of pages_visited: {page_counter}', end='\r')
            self.driver.get(self.valid_links[0])
            self.page_visited.append(self.valid_links[0])
            current_page = self.driver.page_source
            # Get case status data parsed
            dat = self.parse_status_html(current_page)
            data.append(dat)
            soup = bs(current_page, 'html.parser')
            oj_details_elem = soup.find_all('button', {'class': 'button pull-right'})
            self.oj_details = [
                str(elem.get('onclick')).replace(str(elem.get('onclick'))[-1], '').replace('location.href=',
                                                                                           'http://delhihighcourt.nic.in/')
                for elem in oj_details_elem]

            main_window = self.driver.current_window_handle

            for i, oj in enumerate(self.oj_details):
                order_prefix = slugify(
                    dat['n_{}'.format(i)]['diary_no'])  # This will later be used to name all judgement files

                self.driver.execute_script("window.open('{}')".format(oj))

                # Assigning oj_window the current window tab put the main window in the variable. Trying to assign
                # correct value
                oj_window = list((set(self.driver.window_handles) - set([main_window])))[0]

                self.driver.switch_to.window(oj_window)
                order_subpage = self.driver.page_source
                soup = bs(order_subpage, 'html.parser')
                self.order_subpage_data.append(self.parse_orders_page(order_subpage))
                oj_subp_elem = soup.find_all('button', {'class': 'LongCaseNoBtn'})
                oj_subp_details = [str(elem.get('onclick')) for elem in oj_subp_elem]

                # Clean string and create a list
                for string in oj_subp_details:
                    string = string.replace('location.href=', '')
                    if string.startswith('\'') and string.endswith('\''):
                        string = string[1:-1]
                    order_links.append(string)

                # get link to pdf_pages
                for order in order_links:
                    pdf_links.append(order)

                self.download_pdfs(pdf_links, order_prefix, oj_window, main_window)

                self.driver.close()
                self.driver.switch_to.window(main_window)

            nav_links_curr_page = [element.get_attribute('href')
                                   for element in
                                   self.driver.find_elements_by_class_name('archivelink')]
            for link in nav_links_curr_page:
                if link not in self.page_visited:
                    self.page_not_visited.append(link)

            self.valid_links = remove_none(list(set(self.page_not_visited) - set(self.page_visited)))
            page_counter += 1

        self.scraped_data = pd.concat([pd.DataFrame(d).T for d in data])
        if not self.ret:
            return None
        else:
            return data

    def download_pdfs(self, pdf_links, order_prefix, oj_window, main_window):
        order_count = 0
        for link in pdf_links:
            self.driver.execute_script("window.open('{}')".format(link))
            pdf_win_handle = list(set(self.driver.window_handles) - set([oj_window]) - set([main_window]))[0]
            self.driver.switch_to.window(pdf_win_handle)

            url = self.driver.find_element_by_xpath("/html/body/iframe").get_attribute('src')
            urllib.request.urlretrieve(url, f"{order_prefix}_{order_count}.pdf")
            order_count += 1
            self.driver.close()
            self.driver.switch_to.window(oj_window)

    def clean_text(self, text):
        text = text.replace(u'\xa0', u'').replace('\n', '')
        text = re.sub(' +', ' ', re.sub('\t+', '\t', text))
        text = text.lstrip().rstrip()
        return text

    def merge_alternate_list(self, lst1, lst2):
        return [sub[item] for item in range(len(lst2))
                for sub in [lst1, lst2]]

    def parse_status_html(self, html):
        soup = bs(html, 'html.parser')
        li_odd = soup.find_all('li', {"class": "clearfix odd"})
        li_even = soup.find_all('li', {"class": "clearfix even"})
        li = self.merge_alternate_list(li_odd, li_even)
        case_status_data = {}
        for i in range(len(li)):
            s0 = self.clean_text(li[i].select('span', attrs={'class': re.compile('^title*')})[0].get_text())
            sr_no = s0.replace(".", "")

            s1 = self.clean_text(li[i].select('span', attrs={'class': re.compile('^title*')})[1].get_text())
            case_status1 = re.findall(r'\[.*?\]', s1)[0]
            diary_no = s1.split(case_status1)[0].replace('\t', '')

            s2 = self.clean_text(li[i].select('span', attrs={'class': re.compile('^title*')})[2].get_text())
            advocate = s2.split('Advocate :')[-1]
            petitioner, respondent = s2.split('Advocate :')[0].split('Vs.')

            s3 = self.clean_text(li[i].select('span', attrs={'class': re.compile('^title*')})[3].get_text())
            try:
                court_no, case_status2, judgement_date = re.findall('^\D*(\d)\s(\D*)\s(\d+/\d+/\d+)', s3)[0]
            except:
                court_no, case_status2, judgement_date = "", "", ""

            case_status_data[f'n_{i}'] = {}
            case_status_data[f'n_{i}']['sr_no'] = sr_no
            case_status_data[f'n_{i}']['diary_no'] = diary_no
            case_status_data[f'n_{i}']['case_status1'] = case_status1
            case_status_data[f'n_{i}']['petitioner'] = petitioner
            case_status_data[f'n_{i}']['respondent'] = respondent
            case_status_data[f'n_{i}']['advocate'] = advocate
            case_status_data[f'n_{i}']['court_no'] = court_no
            case_status_data[f'n_{i}']['case_status2'] = case_status2
            case_status_data[f'n_{i}']['judgement_date'] = judgement_date
        return case_status_data

    def get_order_page_links(self, html):
        soup = bs(html, 'html.parser')
        oj_details_elem = soup.find_all('button', {'class': 'button pull-right'})
        oj_details = [str(elem.get('onclick')).replace(str(elem.get('onclick'))[-1], '').replace('location.href=',
                                                                                                 'http://delhihighcourt.nic.in/')
                      for elem in oj_details_elem]

    def get_search_count(self):
        self.search_count = self.driver.find_element_by_xpath("//*[@id='InnerPageContent']/span").text
        self.search_count = int(self.search_count.split(":")[-1].lstrip().rstrip())

    def parse_orders_page(self, html):
        soup = bs(html, 'html.parser')
        li = soup.find_all('li', {"class": "clearfix odd"})

        orders = {}
        for i in range(len(li)):
            """
            The Delhi High court website essentially has a a case status page and a button
            which gives details of all the orders related to that case. This function
            parses the page to provide structured data from the page. Variables include
            serial no, date of order, corrigendum text

            """
            s0 = self.clean_text(li[i].select('span', attrs={'class': re.compile('^title*')})[0].get_text())
            sr_no = s0.replace(".", "")

            s1 = self.clean_text(li[i].select('span', attrs={'class': re.compile('^title*')})[1].get_text())
            case_no = s1

            s2 = self.clean_text(li[i].select('span', attrs={'class': re.compile('^title*')})[2].get_text())
            date_of_order = s2

            s3 = self.clean_text(li[i].select('span', attrs={'class': re.compile('^title*')})[3].get_text())
            corrigendum = s3

            orders[f'n_{i + 1}'] = {}
            orders[f'n_{i + 1}']['sr_no'] = sr_no
            orders[f'n_{i + 1}']['case_no'] = case_no
            orders[f'n_{i + 1}']['date_of_order'] = date_of_order
            orders[f'n_{i + 1}']['corrigendum'] = corrigendum
        return orders

    def setup(self):
        options = Options()
        if self.headless:
            options.add_argument('--headless')

        options.add_argument("--disable-xss-auditor")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-webgl")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-popup-blocking")
        profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
                   # Disable Chrome's PDF Viewer
                   "download.extensions_to_open": "applications/pdf"}
        options.add_experimental_option("prefs", profile)

        if self.no_image:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        elif not options:
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
        print('Browser setup complete')

    def close(self):
        self.driver.quit()


HC_list = [
    "Allahabad",
    "Andhra Pradesh",
    "Bombay",
    "Calcutta",
    "Chhattisgarh",
    "Delhi",
    "Gauhati",
    "Gujarat",
    "Himachal Pradesh",
    "Jammu & Kashmir",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Madras",
    "Manipur",
    "Meghalaya",
    "Orissa",
    "Patna",
    "Punjab & Haryana",
    "Rajasthan",
    "Sikkim",
    "Telangana",
    "Tripura",
    "Uttarakhand"
]
