import bs4 as bs
import re
import random
import requests
import string
from torrent_class import Torrent_Link 

def choose_torrent_website():
    accepted_links = ['nyaa', 'piratebay']
    choice = input('Torrent Site: ')
    if(choice in accepted_links):
        if(choice == 'nyaa'):
            link = 'https://nyaa.si/?f=0&c=0_0&q='
            sortbyseeders = '&s=seeders&o=desc'
        if(choice == 'piratebay'):
            link = 'https://www.pirate-bay.net/search?q='
            sortbyseeders = ''
    elif(choice.lower() == 'a'):
        link = 'https://nyaa.si/?f=0&c=0_0&q='
        sortbyseeders = '&s=seeders&o=desc'
        sortbyseeders = '&s=seeders&o=desc'
    elif(choice.lower() == 'm' or choice.lower() == 'tv'):
        link = 'https://www.pirate-bay.net/search?q='
        sortbyseeders = ''
    
    return link, sortbyseeders



def main():
    link, sortbyseeders = choose_torrent_website()
    original_query = input('Enter torrent name: ')
    search_query = re.sub(r"\s+", "+", original_query)
    link = ''.join([link, search_query, sortbyseeders]) 
    data = requests.get(link).text
    soup = bs.BeautifulSoup(data, "lxml")
    top_torrents = []
    for torrent in soup.find_all('tr')[:10]: 
        currentTorrent = Torrent_Link()
        for link in torrent.find_all('a'):
            if(link.get('title') != None):
                if(all((word.lower() in link.get('title').lower() for word in original_query.split()))):
                    currentTorrent.name(link.get('title'))
                    top_torrents.append(currentTorrent)
            if('magnet' in link['href'].lower()):
                currentTorrent.magnetlink(link['href'])
        for info in torrent.find_all('td', {'class': 'text-center'})[:4]:
            if(not '-' in info.text):
                if('B' in info.text):
                    currentTorrent.size(info.text)
                else:
                    currentTorrent.seeders = info.text
    for num, t in enumerate(top_torrents, 1):
        print(f'{num} {t.name}     Size: {t.size}     S: {t.seeders}')
    
    selected = input('Torrent num?: ')
    print(top_torrents[int(selected)-1].magnet)


if __name__ == '__main__':
    main()
