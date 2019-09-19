import bs4 as bs
import urllib.request
import pickle
from geopy.geocoders import Bing
from torrequest import TorRequest
from fake_useragent import UserAgent
from datetime import datetime

pickle_in = open("links.pickle", "rb")
linklist = pickle.load(pickle_in)

geolocator = Bing(api_key="AvBAPo5JOlFEEXybd-kmWdAsiQD4zVnCZUpxHMFcXuj-4e0Nm854mI7WVHG5Qopp")
FLATSSKIPPED = 0
FLATSERROR = 0
flats_nostreet_counter = 0
DEACTIVATED_FLATS = 0
timestamp = datetime.now()
timestamp = timestamp.strftime("%Y%m%d%H%M%S")

with open('logs/immoscrapy_log_{timestamp}.txt'.format(timestamp=timestamp), 'w') as f:
    f.write("Flats to scrape: " + str(len(linklist)) + "\n")

flat_list = []

# scraping flat data on immobilienscout24

for link in linklist:

    if "immobilienscout24" in link:

        flat_info = []

        try:
            source = urllib.request.urlopen(link).read()
        except Exception as e:
            with open('logs/immoscrapy_log_{timestamp}.txt'.format(timestamp=timestamp), 'a') as f:
                f.write("link broken:", e + "\n")
            continue

        soup = bs.BeautifulSoup(source, 'lxml')

        # full link
        flat_info.append(link)
        # name
        flat_info.append(soup.title.get_text())
        # price without nebenkosten
        try:
            flat_info.append(soup.find("div", {"class": "is24qa-kaltmiete is24-value font-semibold"}).get_text())
        except Exception as e:
            print("exception", e)
            continue
        # nebenkosten
        flat_info.append(soup.find(
            "dd", {"class": "is24qa-nebenkosten grid-item three-fifths"}).get_text())
        # number of rooms
        flat_info.append(
            soup.find("div", {"class": "is24qa-zi is24-value font-semibold"}).get_text())
        # size in sqm
        flat_info.append(soup.find(
            "div", {"class": "is24qa-flaeche is24-value font-semibold"}).get_text())
        # street
        try:
            flat_info.append(soup.find("span", {"class": "block font-nowrap print-hide"}).get_text())
        except Exception as e:
            flat_info.append("")
            print("exception while scraping the street: ", e)
            flats_nostreet_counter += 1
        # district and index
        flat_info.append(soup.find("span", {"class": "zip-region-and-country"}).get_text())

        #fetching lat and long from bing
        try:
            if len(flat_info[-2]) < 1:
                flat_info.append("")
                flat_info.append("")
                flat_list.append(flat_info)
                continue
            location = geolocator.geocode(flat_info[-2] + " " + flat_info[-1])
            flat_info.append(location.latitude)
            flat_info.append(location.longitude)
        except Exception as e:
            FLATSERROR += 1
            print("exception while locating an adress:", e)
            flat_info.append("")
            flat_info.append("")
        flat_list.append(flat_info)
        with open('logs/immoscrapy_log_{timestamp}.txt'.format(timestamp=timestamp), 'a') as f:
            f.write("Done scraping " + link + "\n")

# scraping flat data on wg-gesucht.de

    if "wg-gesucht.de" in link:

        flat_info = []

        ua = UserAgent()
        header = {'User-Agent':str(ua.random)}

        # using tor to scrape anonymously
        tr = TorRequest(password='12345qwert!')
        tr.reset_identity()  # Reset Tor
        source = tr.get(link, headers=header).text
        soup = bs.BeautifulSoup(source, 'lxml')

        #check if the flat is deactivated
        try:
            if "Diese Anzeige ist momentan deaktiviert" in soup.find_all("h4", {"class": "headline alert-primary-headline"})[2].get_text():
                DEACTIVATED_FLATS += 1
                with open('logs/immoscrapy_log_{timestamp}.txt'.format(timestamp=timestamp), 'a') as f:
                    f.write("The flat is deactivated: " + link + "\n")
                continue
        except:
            pass

        # full link
        flat_info.append(link)
        # name
        flat_info.append(soup.title.get_text())
        
        # scraping a table with prices from the flat page 
        table = soup.find('table')
        table_rows = table.find_all('tr')
        list_of_prices = []
        for tr in table_rows:
            td = tr.find_all('td')
            row = [i.text for i in td]
            # using try/except because the last row in the table doesn't have collumns therefore row[1] is out of range
            try:
                list_of_prices.append(row[1])
            except:
                continue    
        # price without nebenkosten
        flat_info.append(list_of_prices[0])
        # nebenkosten
        flat_info.append(list_of_prices[1])
        
        # scraping key facts from the flat page
        flat_key_facts = soup.find_all('h2')
        # number of rooms
        flat_info.append(flat_key_facts[2].text.replace(' ', ''))
        # size in sqm
        flat_info.append(flat_key_facts[0].text.replace(' ', ''))

        # scraping the whole adress
        flat_adress = soup.find("a", {"onclick": "$('#map_tab').trigger('click');"})
        flat_adress = flat_adress.get_text().split("\n")
        # street
        flat_info.append(flat_adress[1].replace('                            ', ''))
        # district and index
        flat_info.append(flat_adress[4].replace('            ', ''))

        #fetching lat and long from bing
        try:
            if len(flat_info[-2]) < 1:
                flat_info.append("")
                flat_info.append("")
                flat_list.append(flat_info)
                continue
            location = geolocator.geocode(flat_info[-2] + " " + flat_info[-1])
            flat_info.append(location.latitude)
            flat_info.append(location.longitude)
        except Exception as e:
            FLATSERROR += 1
            print("exception while locating an adress:", e)
            flat_info.append("")
            flat_info.append("")
        flat_list.append(flat_info)
        with open('logs/immoscrapy_log_{timestamp}.txt'.format(timestamp=timestamp), 'a') as f:
            f.write("Done scraping " + link + "\n")


pickle_out = open("flats.pickle","wb")
pickle.dump(flat_list, pickle_out)
pickle_out.close()

with open('logs/immoscrapy_log_{timestamp}.txt'.format(timestamp=timestamp), 'a') as f:
    f.write("Flats without a street: " + str(flats_nostreet_counter) + "\n")
    f.write("Skipped because there was an error: " + str(FLATSERROR) + "\n")
    f.write("Deactivated flats: " + str(DEACTIVATED_FLATS) + "\n")
    f.write("New list contains " + str(len(flat_list)) + " flats\n")
