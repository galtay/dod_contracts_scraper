"""
We want to scrape information about DOD contracts from the page,

https://www.defense.gov/Newsroom/Contracts
"""

from datetime import datetime
import requests
from bs4 import BeautifulSoup


class ContractsPage:

    def __init__(self, url):
        self.url = url

    def get_contract_day_metas(self):
        response = requests.get(self.url)
        # todo: add some response checking
        soup = BeautifulSoup(response.text, features="html.parser")
        data_url_divs = soup.find_all('div', attrs={"data-url": True})

        contract_days = []
        for data_url_div in data_url_divs:
            link = data_url_div.find("a", attrs={"class":"title"})
            link_text_pieces = link.text.split()
            date_str = " ".join(link_text_pieces[2:])
            date = datetime.strptime(date_str, "%b. %d, %Y")
            contract_days.append({
                "url": link["href"],
                "anchor": link.text,
                "date": date,
            })
        return contract_days

    def __str__(self):
        return self.url

    def __repr__(self):
        return self.__str__()


class ContractDayPage:

    def __init__(self, url, date):
        self.url = url
        self.date = date

    def get_contracts(self):
        response = requests.get(self.url)
        # todo: add some response checking
        soup = BeautifulSoup(response.text, features="html.parser")

        group = None
        groups = []
        footnotes = []
        paragraphs = soup.find_all("p")
        for paragraph in paragraphs:

            # top paragraph is a skip
            if paragraph.get("id") == "skip-target-holder":
                continue

            # we found a new heading
            elif paragraph.find("strong") or paragraph.find("b"):
                if group:
                    groups.append(group)
                heading = paragraph.text
                group = {
                    "heading": heading,
                    "contract_texts": [],
                }

            # ad at bottom of page
            elif paragraph.text.startswith("Choose which Defense.gov products"):
                continue

            # foot notes
            elif paragraph.text.startswith("*"):
                footnotes.append(paragraph.text)

            # we have some contract text
            else:
                group["contract_texts"].append(paragraph.text)

        # append final group
        if group:
            groups.append(group)

        return groups, footnotes


    def __str__(self):
        return "{} - {}".format(self.url, self.date)

    def __repr__(self):
        return self.__str__()



contracts_url = "https://www.defense.gov/Newsroom/Contracts"
contracts_page = ContractsPage(contracts_url)

contract_day_metas = contracts_page.get_contract_day_metas()
contract_day_meta = contract_day_metas[0]

contract_day_page = ContractDayPage(
    contract_day_meta["url"],
    contract_day_meta["date"],
)
