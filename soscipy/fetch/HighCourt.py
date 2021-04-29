class delhi_hc_search:
    def __init__(self, case_type, case_year, case_no=None, headless=True, no_image=True, delay=1):
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
        self.elements['case_type'] = "//*[@id='InnerPageContent']/form[1]/select[1]"
        self.elements['case_type_elem'] = "//*[@id='InnerPageContent']/form[1]/select[1]"
        self.elements['case_no'] = "//*[@id='InnerPageContent']/form[1]/input[1]"
        self.elements['case_year_elem'] = "//*[@id='c_year']"
        self.elements['captcha_text_input'] = "//*[@id='inputdigit']"
        self.elements['captcha_text_value'] = "//*[@id='InnerPageContent']/form[1]/label[4]"
        self.elements['search_but'] = "//*[@id='InnerPageContent']/form[1]/button"

        # Keeping a global name for case_type_select element
        self.case_type_select = None
        self.delay = delay

        # Assertions
        if self.case_no:
            assert type(self.case_no) == int, "Case no. must be an integer"
        assert (type(case_year) == int) & (len(str(case_year)) == 4), "Case no. must be an year in YYYY format"

    def _delay(self):
        time.sleep(self.delay)

    def get_case_type_options(self):
        case_type_select = Select(self.driver.find_element_by_xpath(self.elements['case_type']))
        self.case_type_options = [(ind, opt.text) for ind, opt in enumerate(case_type_select.options)]

    def get_search_page(self):
        self.setup()
        self.driver.get(self.url)
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

        # find the number of pages

        # Parse the html page

        # Append the data in a file

        # Load the orders_judgements page

        # Parse the orders_judgements

        # Store the pdf files

        # Go back to the search page -> loop

    def start_scraping(self):
        pass

    def clean_text(self, text):
        text = text.replace(u'\xa0', u'').replace('\n', '')
        text = re.sub(' +', ' ', re.sub('\t+', '\t', text))
        text = text.lstrip().rstrip()
        return text

    def merge_alternate_list(self, lst1, lst2):
        return [sub[item] for item in range(len(lst2))
                for sub in [lst1, lst2]]

    def parse_status_html(self, html):
        soup = bs(html, 'html5lib')
        li_odd = soup.find_all('li', {"class": "clearfix odd"})
        li_even = soup.find_all('li', {"class": "clearfix even"})
        li = self.merge_alternate_list(li_odd, li_even)
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

            case_status_data[f'id_{i}'] = {}
            case_status_data[f'id_{i}']['sr_no'] = sr_no
            case_status_data[f'id_{i}']['diary_no'] = diary_no
            case_status_data[f'id_{i}']['case_status1'] = case_status1
            case_status_data[f'id_{i}']['petitioner'] = petitioner
            case_status_data[f'id_{i}']['respondent'] = respondent
            case_status_data[f'id_{i}']['advocate'] = advocate
            case_status_data[f'id_{i}']['court_no'] = court_no
            case_status_data[f'id_{i}']['case_status2'] = case_status2
            case_status_data[f'id_{i}']['judgement_date'] = judgement_date
        return case_status_data

    def parse_orders_judgements_html(self, url, diary_no):
        pass

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
