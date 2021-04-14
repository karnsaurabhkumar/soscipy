from soscipy.utilities import br


class world_bank_data:
    def __init__(self, URL):
        self.URL = URL

    def fetch_data(self):
        self.browser = br(self.URL)
        self.browser.setup()
        self.bro
