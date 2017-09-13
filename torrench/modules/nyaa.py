"""nyaa.si module"""

import sys
import logging
from requests import get
from bs4 import BeautifulSoup, SoupStrainer
from torrench.utilities.Common import Common

class NyaaTracker(Common):
    """
    Nyaa.si class.

    This class fetches results from nyaa.si
    and displays in tabular form.
    Selected torrent is downloaded to hard-drive.

    Default download location is $HOME/Downloads/torrench
    """

    def __init__(self, title):
        """Class constructor"""
        Common.__init__(self)
        self.title = title
        self.logger = logging.getLogger('log1')
        self.output_headers = ['NAME', 'INDEX','SIZE', 'S', 'L']
        self.index = 0
        self.mylist = []
        self.category_mapper = []
        self.mapper = []
        self.url = "https://nyaa.si/?f=0&c=0_0&q={query}".format(query=self.title)
        self.request = get(self.url)
        self.soup = BeautifulSoup(self.request.text, 'html.parser', parse_only=SoupStrainer('div'))

    def display_categories(self):
        """
        Display the categories available in the website.
        The categories in this scraper have been hardcoded since they are dynamically generated
        in the website.

        @datafanatic:
        An easy way to solve this would be using PhantomJS or Selenium, but it would add unecessary
        overhead to the program. As such, I'll leave it up to future contributors the decision
        of whether to add it or keep using the following method.
        """
        self.logger.debug("Displaying categories in the nyaa module")
        categories = {'All categories': '0_0',
                      'Anime': '1_0',
                      'Audio': '2_0',
                      'Literature': '3_0',
                      'Live Action': '4_0',
                      'Pictures': '5_0',
                      'Software': '6_0'
                     }
        count = len(categories.keys())
        for idx, item in enumerate(categories):
            self.category_mapper.insert(idx, (idx, item, categories[item]))
            print("[{index}] {category}".format(index=idx, category=item))
        self.logger.debug("Total categories displayed: %d", count)

    def select_category(self):
        """
        Select a category from the list.

        Categories are associated with an index, and
        can be selected using that index. Each category has an unique index and url code.
        The URL code is mapped to the category index.
        """
        self.logger.debug("Prompting for category in the nyaa module")
        try:
            prompt = int(input("\nSelect category (0=none): "))
            self.logger.debug("Selected index `%d` in the nyaa module", prompt)
            if prompt == 0:
                print("cat mapper %s" % self.category_mapper[0][2])
                self.categ_url_code = self.category_mapper[0][2]
                print("Selected category: {category}".format(category=self.category_mapper[0][1]))
            else:
                selected_category, self.categ_url_code = self.category_mapper[prompt], self.category_mapper[prompt][2]
                
                print("Selected [{idx}]: {category} ".format(idx=prompt,
                                                             category=selected_category[1]))
                self.logger.debug("Selected category %s with index %d", selected_category[1], prompt)
                self.logger.debug("Category URL code: `%s`", selected_category[2])
        except (ValueError, IndexError, KeyError) as killed:
            self.logger.exception(killed)
            print("Input needs to be an integer number.")
            sys.exit(2)
    
    def parse_name(self):
        """
        Parse torrent name
        """
        t_names = []
        for name in self.soup.find_all('td', {'colspan': '2'}):
            t_names.append(name.get_text().replace('\n', ''))
        assert t_names
        return t_names

    def parse_urls(self):
        urls = []
        for url in self.soup.find_all('a'):
            try:
                if url.get('href').startswith('/download/'):
                    urls.append('https://nyaa.si'+url['href'])
            except AttributeError:
                pass
        assert urls
        return urls

    def parse_sizes(self):
        t_size = []
        for size in self.soup.find_all('td', {'class': 'text-center'}):
            if size.get_text().endswith(("GiB", "MiB")):
                t_size.append(size.get_text())
            else:
                pass
        assert t_size
        return t_size

    def parse_seeds(self):
        t_seeds = []
        for seed in self.soup.find_all('td', {'style': 'color: green;'}):
            t_seeds.append(seed.get_text())
        assert t_seeds
        return t_seeds


    def parse_leeches(self):
        t_leeches = []
        for leech in self.soup.find_all('td', {'style': 'color: red;'}):
            t_leeches.append(leech.get_text())
        assert t_leeches
        return t_leeches

    def fetch_results(self):
        """
        Fetch results for a given query.

        @datafanatic:
        Work in progress
        """
        print("Fetching results")
        self.logger.debug("Fetching...")
        self.logger.debug("URL: %s", self.url)
        try:
            name = self.parse_name()
            urls = self.parse_urls()
            sizes = self.parse_sizes()
            seeds = self.parse_seeds()
            leeches = self.parse_leeches()
            self.index = len(urls)
        except (KeyError, AttributeError) as e:
            print("Something went wrong. Logging and terminating.")
            self.logger.exception(e)
            print("OK. Terminating.")
        if self.index == 0:
            print("No results were found for the given query. Terminating")
            self.logger.debug("No results were found for `%s`.", self.title)
            return -1
        self.logger.debug("Results fetched. Showing table.")
        self.mapper.insert(self.index, (name, urls))
        return list(zip(name, ["--"+str(idx)+"--" for idx in range(self.index)], sizes, seeds, leeches))

    def select_torrent(self):
        """
        Select torrent from table using index.
        """
        while True:
            try:
                prompt = int(input("(0 = exit) Index> "))
                if prompt == 9:
                    print("Bye!")
                    break
                else:
                    selected_index, download_url = self.mapper[0][0][prompt], self.mapper[0][1][prompt]
                    print("Downloading: \n" + selected_index)
                    self.get_torrent(download_url, selected_index)
            except IndexError as e:
                self.logger.exception(e)
                print("Invalid index.")

    def get_torrent(self, url, name):
        """
        Download the .torrent file to the computer.
        """
        self.download(url, name+'.torrent')

def main(title):
    """
    Execution will begin here.
    """
    try:
        print("[Nyaa.si]")
        nyaa = NyaaTracker(title)
        results = nyaa.fetch_results()
        nyaa.show_output([result for result in results], nyaa.output_headers)
        nyaa.select_torrent()
    except KeyboardInterrupt:
        nyaa.logger.debug("Interrupt detected. Terminating.")
        print("Terminated")

if __name__ == "__main__":
    print("Modules are not supposed to be run standalone.")