import bs4 as bs
import re
import random
import requests
import string
import os
from subprocess import call
from prettytable import PrettyTable
from pathlib import Path
from configparser import ConfigParser
import platform

config = ConfigParser()
config.read('config.ini')

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
    type_of_media = input('Movie or Series? (M / S): ')
    original_query = input('Enter torrent name: ')
    if(choice == 'a' or choice == 'nyaa'):
        search_query = re.sub(r"\s+", "+", original_query)
    elif(choice == 'm' or choice == 'tv' or choice =='piratebay'):
        search_query = re.sub(r"\s+", "%20", original_query) +'/1/99/0'
    link = ''.join([link, search_query, sortbyseeders]) 
    data = requests.get(link).text
    soup = bs.BeautifulSoup(data, "lxml")
    top_torrents = []
    directory = None
    if(choice == 'a' or choice == 'nyaa'):
        if(type_of_media.lower() == 's' or type_of_media.lower() == 'series'):
            series_status = input('On-Going or Finished Series? (O / F): ')
            if(series_status.lower() == 'o'):
                show_list = open('ongoing_directories.txt', 'a+')
                new_show = input('New Folder? (Y/N): ')
                if new_show.lower() == 'y':
                    new_show_name = input('Enter Name of New Folder: ')
                    show_list.write(new_show_name +'\n')
                    show_directory_name = new_show_name
                    show_list.close()
                    if(platform.system().lower() == 'windows'):
                        directory = Path(config['directories']['anime'] + show_directory_name)
                    else:
                        directory = Path(config['directories']['anime'] + re.sub(r"\s+", "\\ ", show_directory_name))
                else:
                    with open('ongoing_directories.txt', 'r') as f:
                        all_ongoing_shows = f.read().splitlines()
                    for num, show in enumerate(all_ongoing_shows):
                        print(f'({num+1}) {show}')
                    show_choice = input('Choose which show to add too (1-#): ')
                    show_directory_name = all_ongoing_shows[int(show_choice)-1]
                    if(platform.system().lower() == 'windows'):
                        directory = Path(config['directories']['anime'] + show_directory_name)
                    else:
                        directory = Path(config['directories']['anime'] + re.sub(r"\s+", "\\ ", show_directory_name))
            else:
                directory = Path(config['directories']['anime'])
        elif(type_of_media.lower() == 'm' or type_of_media.lower() == 'movie'):
            directory = Path(config['directories']['movies'])
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

        if(type_of_media.lower() == 's' or type_of_media.lower() == 'series'):
            directory = Path(config['directories']['tvshows'])
        elif(type_of_media.lower() == 'm' or type_of_media.lower() == 'movie'):
            directory = Path(config['directories']['movies'])
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
        t.magnet = t.magnet.split('&tr=', 1)[0]

    print(x)
    close = False
    selected = input('Torrent num(s)? (n for next 10): ')
    if(selected.lower() == 'n'):
        for num, t in enumerate(top_torrents[10:], 11):
            x.add_row([num, t.name, t.size, t.seeders])
            t.magnet = t.magnet.split('&tr=', 1)[0]
        print(x)
    else:
        for num in selected.split():
            if(config['autodownload']['status'].lower() == 'true'):
                try:
                    if(platform.system().lower() == 'windows'):
                        call(['aria2c', '-d', f'{Path.home().joinpath(directory)}', '--seed-time=0', f'{top_torrents[int(num) - 1].magnet}'])
                        close = True
                    else:
                        call(['sudo', 'deluge-console', 'add', '-p', f'~/{directory}', top_torrents[int(num) - 1].magnet])
                        close = True
                except:
                    print("Error downloading torrent")
                    print(top_torrents[int(num)-1].magnet)
                    close=True
            else:
                print(top_torrents[int(num)-1].magnet)
                close=True
    if(close == True):
        quit()

    selected = input('Torrent num(s)? (ex: 1 5 4): ')
    for num in selected.split():
        if(config['autodownload']['status'].lower() == 'true'):
            try:
                if(platform.system().lower() == 'windows'):
                    call(['aria2c', '-d', f'{Path.home().joinpath(directory)}', '--seed-time=0', f'{top_torrents[int(num) - 1].magnet}'])
                else:
                    call(['sudo', 'deluge-console', 'add', '-p', f'~/{directory}', top_torrents[int(num) - 1].magnet])
            except:
                print("Error downloading torrent")
                print(top_torrents[int(num)-1].magnet)
        else:
            print(top_torrents[int(num)-1].magnet)
            close=True



if __name__ == '__main__':
    main()
