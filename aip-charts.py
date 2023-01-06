import base64
from bs4 import BeautifulSoup
import requests
import os
import platform
import sys

def get_icao(ad_url):
    html_text = requests.get(ad_url).text
    soup = BeautifulSoup(html_text, 'html.parser')    
    icao = soup.find('div', class_='headlineText left').get_text().replace(" ", "_").rsplit('_', 1)[-1]

    return(icao)

def create_dir(icao):
    path = os.getcwd()
    if platform.system() == 'Windows':
        slash='\\'
    else:
        slash='/'

    newdir = path+slash+icao
    print(f'--------------------------------------------- {icao} ---------------------------------------------')
    print(f'Creating Directory {newdir} if necessary')
    os.makedirs(newdir, exist_ok=True)
    icao_dir = newdir+slash

    return(icao_dir)

def create_png(aip_url, icao_dir):
    html_text = requests.get(aip_url).text
    soup = BeautifulSoup(html_text, 'html.parser')

    filename = soup.find('div', class_='headlineText left').get_text().replace(" ", "_")
    print(f'Downloading Chart {filename}')

    link = soup.find('img', class_='pageImage')['src']

    linksplit = link.split(',')
    b64img = str.encode(linksplit[1])

    print(f'Saving Chart as {icao_dir}{filename}.png')

    with open(f"{icao_dir}{filename}.png", "wb") as fh:
        fh.write(base64.decodebytes(b64img))

url = 'https://aip.dfs.de/basicVFR/2022DEC15/f8b39000e696651bdd6398c1bb5828a2.html'

html_text = requests.get(url).text

soup = BeautifulSoup(html_text, 'html.parser')

icao = 'XXXX'
if len(sys.argv) > 1:
    search = sys.argv
    search.pop(0)
    print('Searching for aerodromes:')
    print(', '.join(search))
else:
    search = 'YYYY'

for links in soup.find_all('a', class_='folder-link', href=True):
    if links.text[0:3].strip() != 'AD':
        # print(f'Found the URL:, {links["href"]}')
        letter_url = f'https://aip.dfs.de/basicVFR/2022DEC15/{links["href"]}'
        letter_url_text = requests.get(letter_url).text
        
        letter_soup = BeautifulSoup(letter_url_text, 'html.parser')

        for ad_links in letter_soup.find_all('a', class_='folder-link', href=True):
            # print(f'https://aip.dfs.de/basicVFR/2022DEC15/{ad_links["href"]}')
            ad_url = f'https://aip.dfs.de/basicVFR/2022DEC15/{ad_links["href"]}'

            if icao in search and 'YYYY' not in search:
                search.remove(icao)
                if len(search) < 1:
                    sys.exit()

            icao = get_icao(ad_url)

            if icao not in search and 'YYYY' not in search:
                continue

            icao_dir = create_dir(icao)

            ad_url_text = requests.get(ad_url).text

            ad_soup = BeautifulSoup(ad_url_text, 'html.parser')

            for chart_links in ad_soup.find_all('a', class_='document-link', href=True):
                # print(f'https://aip.dfs.de/basicVFR/2022DEC15/{chart_links["href"]}')
                chart_url = f'https://aip.dfs.de/basicVFR/2022DEC15/{chart_links["href"]}'
                create_png(chart_url, icao_dir)
