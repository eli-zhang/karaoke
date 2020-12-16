from spleeter.separator import Separator
from spleeter.audio.adapter import get_default_audio_adapter
from youtubesearchpython import SearchVideos
import youtube_dl
import json
import re 
import urllib.request 
import requests
from bs4 import BeautifulSoup 
from playsound import playsound


# https://www.quora.com/Whats-a-good-API-to-use-to-get-song-lyrics
def get_lyrics(song_title): 
    # remove all except alphanumeric characters from artist and song_title 
    title = re.sub(' ', "+", song_title)
    search_url = 'https://search.azlyrics.com/search.php?q={}'.format(title)
    print(search_url)
    page = requests.get(search_url)
    try:
        soup = BeautifulSoup(page.content, 'html.parser')
        url = soup.find('td').find('a')['href']

    except Exception as e: 
        return "Exception occurred \n" + str(e) 
     
    try: 
        content = urllib.request.urlopen(url).read() 
        soup = BeautifulSoup(content, 'html.parser') 
        lyrics = str(soup) 
        # lyrics lies between up_partition and down_partition 
        up_partition = '<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->' 
        down_partition = '<!-- MxM banner -->' 
        lyrics = lyrics.split(up_partition)[1] 
        lyrics = lyrics.split(down_partition)[0] 
        lyrics = lyrics.replace('<br>','').replace('</br>','').replace('<br/>','').replace('</div>','').replace('<i>','').replace('</i>','').strip() 
        return lyrics 
    except Exception as e: 
        return "Exception occurred \n" +str(e) 

while True:
    print('enter a song: ')
    name = input()
    print('searching...')
    search = SearchVideos(name, offset = 1, mode = "json", max_results = 1)
    result = json.loads(search.result())['search_result'][0]
    link = result['link']
    init_title = result['title']
    title = "".join([c for c in init_title if c.isalpha() or c.isdigit()]).rstrip()
    artist = result['channel']
    print('loading...')
    
    ydl_opts = {
        'outtmpl': './downloads/{}.%(ext)s'.format(title),
        'format': 'bestaudio/best',
        'keepvideo': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.download([link])

    separator = Separator('spleeter:2stems')
    separator.separate_to_file('./downloads/{}.mp3'.format(title), './downloads/')
    playsound('./downloads/{}/accompaniment.wav'.format(title), block=False)
    print(get_lyrics(name))