from spleeter.separator import Separator
from spleeter.audio.adapter import get_default_audio_adapter
from youtubesearchpython import SearchVideos
import youtube_dl
import json
import re 
import urllib.request 
from bs4 import BeautifulSoup 
from playsound import playsound

# https://www.quora.com/Whats-a-good-API-to-use-to-get-song-lyrics
def get_lyrics(artist, song_title): 
    artist = artist.lower() 
    song_title = song_title.lower() 
    # remove all except alphanumeric characters from artist and song_title 
    artist = re.sub('[^A-Za-z0-9]+', "", artist).replace('Official','').replace('Music','').replace('VEVO','')
    song_title = re.sub('[^A-Za-z0-9]+', "", song_title) 
    song_title = re.sub(artist, "", song_title)
    if artist.startswith("the"):    # remove starting 'the' from artist e.g. the who -> who 
        artist = artist[3:] 
    url = "http://azlyrics.com/lyrics/"+artist+"/"+song_title+".html" 
    print(url)
     
    try: 
        content = urllib.request.urlopen(url).read() 
        soup = BeautifulSoup(content, 'html.parser') 
        lyrics = str(soup) 
        # lyrics lies between up_partition and down_partition 
        up_partition = '<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->' 
        down_partition = '<!-- MxM banner -->' 
        lyrics = lyrics.split(up_partition)[1] 
        lyrics = lyrics.split(down_partition)[0] 
        lyrics = lyrics.replace('<br>','').replace('</br>','').replace('<br/>','').replace('</div>','').strip() 
        return lyrics 
    except Exception as e: 
        return "Exception occurred \n" +str(e) 

while True:
    print('enter a song: ')
    name = input()
    print('searching...')
    search = SearchVideos(name, offset = 1, mode = "json", max_results = 1)
    result = json.loads(search.result())['search_result'][0]
    print(result)
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
    separator.separate_to_file('./downloads/{}.mp3'.format(title), './'.format(title))
    playsound('./{}/accompaniment.wav'.format(title), block=False)
    print(get_lyrics(artist, title)) 