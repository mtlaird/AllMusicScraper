from bs4 import BeautifulSoup
import requests


class AllMusicSearchPage:

    def __init__(self, search_term, search_type='all'):

        self.url = 'http://www.allmusic.com/search/{}/{}'.format(search_type, search_term)
        self.dom = None
        self.result_soup = None
        self.request = None

    def get_dom(self):

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/47.0.2526.80 Safari/537.36'}
        self.request = requests.get(self.url, headers=headers)
        self.dom = BeautifulSoup(self.request.text, 'html.parser')

    def get_results(self):
        results = self.dom.find(class_='search-results')
        self.result_soup = BeautifulSoup(str(results), 'html.parser')

    def get_first_result(self):
        if not self.result_soup:
            self.full_initialize()
        first_result_soup = BeautifulSoup(str(self.result_soup.find_all('li')[0]), 'html.parser')
        result = {'Type': first_result_soup.find('h4').text.strip()}
        try:
            result['Name'] = first_result_soup.find_all('a')[1].text
            result['URL'] = first_result_soup.find_all('a')[1].attrs['href']
        except IndexError:
            result['Name'] = first_result_soup.find_all('a')[0].text
            result['URL'] = first_result_soup.find_all('a')[0].attrs['href']
        return result

    def full_initialize(self):
        self.get_dom()
        self.get_results()


class AllMusicDiscographyPage:

    def __init__(self, artist_name='Billy Joel'):

        self.artist_name = artist_name
        search_result = AllMusicSearchPage(search_term=artist_name, search_type='artists').get_first_result()
        self.url = '{}/discography'.format(search_result['URL'])
        self.dom = None
        self.albums = []

    def get_dom(self):

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/47.0.2526.80 Safari/537.36'}
        r = requests.get(self.url, headers=headers)
        self.dom = BeautifulSoup(r.text, 'html.parser')

    def get_albums(self):

        rows = self.dom.find_all('tr')
        for r in rows[1:]:
            row_soup = BeautifulSoup(str(r), 'html.parser')
            album = {'Label': row_soup.find(class_='label').text.strip(),
                     'Year': row_soup.find(class_='year').text.strip(),
                     'URL': 'http://www.allmusic.com'+row_soup.find('a').attrs['href'],
                     'Artist': self.artist_name}
            try:
                album['Title'] = row_soup.find('a').attrs['title']
            except KeyError:
                album['Title'] = row_soup.find('a').text.strip()
            self.albums.append(album)

    def full_initialize(self):

        self.get_dom()
        self.get_albums()

    def print_albums(self):

        for a in self.albums:
            print a


class AllMusicAlbumPage:

    def __init__(self, album_name=None, album_def=None):
        if album_def:
            self.url = album_def['URL']
            self.artist_name = album_def['Artist']
            self.label = album_def['Label']
            self.year = album_def['Year']
            self.title = album_def['Title']
        elif album_name:
            self.title = album_name
            search_result = AllMusicSearchPage(search_term=album_name, search_type='albums').get_first_result()
            self.url = search_result['URL']
        self.dom = None
        self.songs = []
        self.release_date = None
        self.duration = None
        self.genre = None
        self.styles = []
        self.moods = []
        self.themes = []

    def get_dom(self):

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/47.0.2526.80 Safari/537.36'}
        r = requests.get(self.url, headers=headers)
        self.dom = BeautifulSoup(r.text, 'html.parser')

    def parse_dom(self):

        for track in self.dom.find('section', class_='track-listing').findChild('tbody').findChildren('tr'):
            track_info = {'tracknum': track.findChild('td', class_='tracknum').text.strip(),
                          'title': track.findChild('div', class_='title').text.strip(),
                          'composer': track.findChild('div', class_='composer').text.strip(),
                          'performer': track.findChild('td', class_='performer').text.strip(),
                          'time': track.findChild('td', class_='time').text.strip()}
            self.songs.append(track_info)

        self.release_date = self.dom.find('div', class_='release-date').find('span').text.strip()
        self.duration = self.dom.find('div', class_='duration').find('span').text.strip()
        self.genre = self.dom.find('div', class_='genre').find('div').text.strip()

        for style in self.dom.find('div', class_='styles').findChildren('a'):
            self.styles.append(style.text.strip())

        for mood in self.dom.find('section', class_='moods').findChildren('a'):
            self.moods.append(mood.text.strip())

        for theme in self.dom.find('section', class_='themes').findChildren('a'):
            self.themes.append(theme.text.strip())

    def full_initialize(self):

        self.get_dom()
        self.parse_dom()

    def print_songs(self):

        for s in self.songs:
            print s
