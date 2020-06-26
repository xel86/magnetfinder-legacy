import bs4 as bs
import re
import random
import requests
import string
import os
from subprocess import call
from prettytable import PrettyTable

class Torrent_Link():

    def name(self, name):
        self.name = name

    def magnetlink(self, link):
        self.magnet = link

    def size(self, size):
        self.size = size

    def seeders(self, seeders):
        self.seeders = seeders


def choose_torrent_website():
    accepted_links = ['nyaa', 'piratebay']
    choice = input('Torrent Site: ')
    choice = choice.lower()
    if(choice in accepted_links):
        if(choice == 'nyaa'):
            link = 'https://nyaa.si/?f=0&c=0_0&q='
            sortbyseeders = '&s=seeders&o=desc'
        if(choice == 'piratebay'):
            link = 'https://www.tpb.party/search/'
            sortbyseeders = ''
    elif(choice.lower() == 'a'):
        link = 'https://nyaa.si/?f=0&c=0_0&q='
        sortbyseeders = '&s=seeders&o=desc'
        sortbyseeders = '&s=seeders&o=desc'
    elif(choice.lower() == 'm' or choice.lower() == 'tv'):
        link = 'https://www.tpb.party/search/'
        sortbyseeders = ''
    
    
    return link, sortbyseeders, choice



def main():
    link, sortbyseeders, choice = choose_torrent_website()
    original_query = input('Enter torrent name: ')
    search_query = re.sub(r"\s+", "+", original_query)
    link = ''.join([link, search_query, sortbyseeders]) 
    data = requests.get(link).text
    soup = bs.BeautifulSoup(data, "lxml")
    top_torrents = []
    directory = None
    if(choice == 'a' or choice == 'nyaa'):
        directory = '/media/ntfsdrive/PLEX/Anime'
        for torrent in soup.find_all('tr')[:21]: 
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
    if(choice == 'm' or choice == 'tv' or choice =='piratebay'):
        if(choice == 'tv'):
            directory = '/media/ntfsdrive/PLEX/TV\\ Shows/'
        else:
            directory = '/media/ntfsdrive/PLEX/Movies'
        for row in soup.find_all('tr')[:21]:
            currentTorrent = Torrent_Link()
            for torrent in row.find_all('div', {'class': 'detName'}):
                currentTorrent.name((torrent.find('a', {'class': 'detLink'})['title'])[11:])
                top_torrents.append(currentTorrent)
            for mag in row.find_all('a', href=True):
                if('magnet' in mag['href'].lower()):
                    currentTorrent.magnetlink((mag['href']))
            if(row.find('font', {'class': 'detDesc'}) is not None):
                desc = row.find('font', {'class': 'detDesc'}).text
                try:
                    size = re.search('Size(.+?),', desc)
                    currentTorrent.size(size.group(1))
                except:
                    currentTorrent.size('#')
            if(row.find('td', {'align': 'right'}) is not None):
                currentTorrent.seeders = row.find('td', {'align': 'right'}).text
            else:
                currentTorrent.seeders = '#'

    x = PrettyTable()
    x.field_names = ["#", "Name", "Size", "Seeders"]
    x.align['Name'] = 'l'
    x.align['Size'] = 'l'
    x.align['Seeders'] = 'l'
    for num, t in enumerate(top_torrents[:10], 1):
        x.add_row([num, t.name, t.size, t.seeders])

    print(x)
    close = False
    selected = input('Torrent num? (n for next 10): ')
    if(selected.lower() == 'n'):
        for num, t in enumerate(top_torrents[10:], 11):
            x.add_row([num, t.name, t.size, t.seeders])
        print(x)
    else:
        try:
            call(['sudo', 'deluge-console', 'add', '-p', directory, top_torrents[int(selected) - 1].magnet])
            close = True
        except:
            print("Error running deluge-console")
            print(top_torrents[int(selected)-1].magnet)
            close=True
    if(close == True):
        quit()

    selected = input('Torrent num? (1-20): ')
    try:
        call(['sudo', 'deluge-console', 'add', '-p', directory, top_torrents[int(selected) - 1].magnet])
        
    except:
        print("Error running deluge-console")
        print(top_torrents[int(selected)-1].magnet)
        


if __name__ == '__main__':
    main()
