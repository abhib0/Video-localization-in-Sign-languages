import ssl 
ssl._create_default_https_context = ssl._create_unverified_context  

from pytube import YouTube
import sys


def Download(link):
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        youtubeObject.download()
    except:
        print("An error has occurred")
    print("Download is completed successfully")

link = sys.argv[1]
Download(link)

