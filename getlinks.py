import bs4 as bs
import urllib.request
import pickle
from torrequest import TorRequest
from fake_useragent import UserAgent
from datetime import datetime

linklist = []
pages = ""
timestamp = datetime.now()
timestamp = timestamp.strftime("%Y%m%d%H%M%S")

#creating a log
with open('logs/getlinks_log_{timestamp}.txt'.format(timestamp=timestamp), 'w') as f:
    f.write("Scraping at  {timestamp}\n".format(timestamp=timestamp))


# Scraping Links from immobilienscout24

source = urllib.request.urlopen(
    'https://www.immobilienscout24.de/Suche/S-T/P-1/Wohnung-Miete/Hamburg/Hamburg').read()
soup = bs.BeautifulSoup(source, 'lxml')

# Scraping the number of pages
for option in soup.find_all('option'):
    pages = option.get_text()
pages = int(pages)

#scraping links from the pages

for num_page in range(1, pages + 1):
    with open('logs/getlinks_log_{timestamp}.txt'.format(timestamp=timestamp), 'a') as f:
        f.write("Scraping Page {page} from immobilienscout24\n".format(page=num_page))
    source = urllib.request.urlopen(
        'https://www.immobilienscout24.de/Suche/S-T/P-{page}/Wohnung-Miete/Hamburg/Hamburg'.format(page=num_page)).read()
    soup = bs.BeautifulSoup(source, 'lxml')

    for url in soup.find_all('a', class_='result-list-entry__brand-title-container'):
        #       print(url.get('href'))
        if len(url.get('href')) < 20:
            linklist.append(
                "https://www.immobilienscout24.de" + url.get('href'))
        else:
            with open('logs/getlinks_log_{timestamp}.txt'.format(timestamp=timestamp), 'a') as f:
                f.write("Skipping " + url.get('href') + "\n")

# Scraping Links from wg-gesucht.de

ua = UserAgent()
header = {'User-Agent':str(ua.random)}

tr = TorRequest(password='12345qwert!')
tr.reset_identity()  # Reset Tor
source = tr.get('https://www.wg-gesucht.de/wohnungen-in-Hamburg.55.2.1.0.html?category=2&city_id=55&rent_type=2&noDeact=1&img=1', headers=header).text
soup = bs.BeautifulSoup(source, 'lxml')

# Scraping the number of pages
for option in soup.find_all("a", {"class": "a-pagination"}):
    pages = option.get_text()
pages = int(pages)

#scraping links from the pages

for i in range(0, pages+1):

    with open('logs/getlinks_log_{timestamp}.txt'.format(timestamp=timestamp), 'a') as f:
        f.write("Scraping Page {page} from wg-gesucht.de\n".format(page=i))
    
    ua = UserAgent()
    header = {'User-Agent':str(ua.random)}
    tr = TorRequest(password='12345qwert!')
    tr.reset_identity()
    source = tr.get("https://www.wg-gesucht.de/wohnungen-in-Hamburg.55.2.1.{num_page}.html?category=2&city_id=55&rent_type=2&noDeact=1&img=1".format(num_page=i), headers=header).text
    soup = bs.BeautifulSoup(source, 'lxml')

    for url in soup.find_all('a', class_='detailansicht'):
        if len(url.get('href')) < 60 and "https://www.wg-gesucht.de/" + url.get('href') not in linklist:
            linklist.append("https://www.wg-gesucht.de/" + url.get('href'))
        elif len(url.get('href')) < 60 and "https://www.wg-gesucht.de/" + url.get('href') in linklist:
            pass
        else:
            with open('logs/getlinks_log_{timestamp}.txt'.format(timestamp=timestamp), 'a') as f:
                f.write("Skipping " + url.get('href') + "\n")

#Summary and save

with open('logs/getlinks_log_{timestamp}.txt'.format(timestamp=timestamp), 'a') as f:
    f.write("There are " + str(len(linklist)) + " links in the list")

pickle_out = open("links.pickle", "wb")
pickle.dump(linklist, pickle_out)
pickle_out.close()
