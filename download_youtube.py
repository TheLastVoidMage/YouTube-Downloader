# Written by Samuel Watson
# Created 8/16/21 - 8/17/21
# This program allows you to download videos and playlists from YouTube

# Written and tested with Python 3.8

# For this program to work you need to install
# Python
# Git
# Moviepy
# Pytube

from genericpath import isdir
from logging import currentframe
from pytube import *
from moviepy.editor import *
import os
from os.path import isfile
import requests
import math

tempFolder = "./temp/"
outFolder = "./out/"

checkURL="https://www.youtube.com/oembed?url="

def getFolderName(urls):
    # This method asks the user to use an automated name or a custom one
    # Returns - String containing the desired output folder name
    # urls - A string list containing valid Youtube urls
    doCustomName = True
    if (len(urls) == 1):
        if ("https://www.youtube.com/playlist?list=" in urls[0]):
            answer = ""
            while (answer != "n" and answer != "y"):
                answer = input("Would you like to use an auto-generated name: (Y/N) ").lower()
            doCustomName = answer == "n"
    if (doCustomName):
        folderName = input("What would you like the folder to be called: ")
        if (folderName != "" and folderName[-1:] != "/"):
            folderName = folderName + "/"
    else:
        myPlaylist = Playlist(urls[0])
        owner = myPlaylist.videos[0].author
        print("./" + owner + "/" + myPlaylist.title + "/")
        folderName = "./" + owner + "/" + myPlaylist.title + "/"
    return folderName

def getDataType():
    # This method ask the user what data type they would like to use
    # Returns - String of the answer
    answer = ""
    while (answer != "mp4" and answer != "mp3"):
        answer = input("What data type do you want your videos in? Video (MP4) | Audio (MP3): ").lower()
    return answer

def gatherURLS():
    # This method gathers a list of unvalidated urls from the user
    # Returns - String List containing unvalidated urls
    urlList = []
    answer = ""
    while (answer != "stop"):
        answer = input("URL/STOP: ")
        if answer.lower() == "stop":
            answer = answer.lower()
        if (answer != "stop"):
            urlList.append(answer)
    return urlList

def makeDirectories(folderName):
    # This method constructs the necessary folders needed by the program
    # Returns - None
    paths = (outFolder + folderName).split("/")
    currentPath = ""
    for path in paths:
        if (isdir(currentPath + path + "/") == False):
            os.mkdir(currentPath + path + "/")
        currentPath = currentPath + path + "/"

def validateURLS(urls):
    # This method takes in a list of strings and checks if they are either Youtube videos or playlists
    # Returns - List containing a list of urlTypes and a list of valid urls
    # urls - A string list 
    urlType = []
    goodRun = False
    while (goodRun == False):
        goodRun = True
        for url in urls:
            request = requests.get(checkURL + url)
            if (request.status_code != 200):
                goodRun = False
                print(url + " was removed due to bad url")
                urls.remove(url)
            else:
                if ("https://www.youtube.com/watch?v=" in url):
                    urlType.append(0)
                elif ("https://www.youtube.com/playlist?list=" in url):
                    urlType.append(1)
                else:
                    goodRun = False
                    urls.remove(url)
    return [urlType,urls]

def convertPlaylists(types, urls):
    # This method converts a list of Youtube videos and playlists to a list of Youtube videos
    # Returns - String List of validated Youtube Video URLs
    newURLS = []
    for x in range(len(urls)):
        if (types[x] == 0):
            newURLS.append(urls[x])
        elif (types[x] == 1):
            for url in Playlist(urls[x]).video_urls:
                newURLS.append(url)

    return newURLS

def cleanFolder(folder):
    # This method deletes all of the generated temporary files
    # Returns - None
    for file in os.listdir(folder):
        if (isfile(folder + file)):
            os.remove(folder + file)
        elif (isdir(folder + file)):
            cleanFolder(folder + file + "/")

        

def download_videos(urls, folderName, dataType):
    # This method impliments the corresponding method to the selected data type
    # Returns - None
    # urls - String List of validated urls
    # folderName - String of desired output folder
    # dataType - String of the desired data type
    if (dataType == "mp3"):
        download_mp3_videos(urls, folderName)
    elif (dataType == "mp4"):
        download_mp4_videos(urls, folderName)

def download_mp4_videos(urls, folderName):
    # This method downloads the given list of urls into mp4 video files
    # Returns - None
    # urls - String List of validated urls
    # folderName - String of desired output folder
    names = []
    answer = ""
    index = 1
    while (answer != "n" and answer != "y"):
        answer = input("Would you like to add indexes to keep these videos in order: (Y/N) ").lower()
    for url in urls:
        yt = YouTube(url)
        aStream = yt.streams.filter(only_audio=True, file_extension='mp4')[0]
        vStream = yt.streams.filter(only_video=True, file_extension='mp4')[0]
        names.append(aStream.default_filename)
        aStream.download(tempFolder + "a")
        vStream.download(tempFolder + "v")
    for name in names:
        if (answer == 'y'):
            name = str(index).zfill(math.ceil((len(names) + 1) / 10)) + "_" + name
            audioclip = AudioFileClip(tempFolder + "a/" + name[name.find('_') + 1:])
            videoClip = VideoFileClip(tempFolder + "v/" + name[name.find('_') + 1:])
            index = index + 1
        else:
            audioclip = AudioFileClip(tempFolder + "a/" + name)
            videoClip = VideoFileClip(tempFolder + "v/" + name)
        try:
            videoClip = videoClip.set_audio(audioclip)
            videoClip.write_videofile(outFolder + folderName + name[:len(name) - 1] + "4")
            print("Downloaded - " + name)
            audioclip.close()
            videoClip.close()
        except:
            print("Failed - " + name)
            audioclip.close()
            videoClip.close()


def download_mp3_videos(urls, folderName):
    # This method downloads the given list of urls into mp3 audio files
    # Returns - None
    # urls - String List of validated urls
    # folderName - String of desired output folder
    names = []
    answer = ""
    index = 1
    while (answer != "n" and answer != "y"):
        answer = input("Would you like to add indexes to keep these videos in order: (Y/N) ").lower()
    for url in urls:
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True, file_extension='mp4')[0]
            names.append(stream.default_filename)
            stream.download(tempFolder) 
        except:
            print(url + " couldn't download")
    for name in names:
        if (answer == 'y'):
            name = str(index).zfill(math.ceil(len(str(len(names) + 1)))) + "_" + name
            audioclip = AudioFileClip(tempFolder + name[name.find('_') + 1:])
            index = index + 1
        else:
            audioclip = AudioFileClip(tempFolder + name)
        try:
            audioclip.write_audiofile(outFolder + folderName + name[:len(name) - 1] + "3")
            print("Downloaded - " + name)
            audioclip.close()
        except:
            print("Failed - " + name)
            audioclip.close()

def start():
    # This method starts the download process
    # Returns - None
    print("Please enter one or more youtube videos or playlists. Enter (stop) to finish.")
    urls = gatherURLS()
    urls = [i for n, i in enumerate(urls) if i not in urls[:n]] # Clears duplicates
    urls = validateURLS(urls)
    dataType = getDataType()
    folderName = getFolderName(urls[1])
    urls = convertPlaylists(urls[0], urls[1])
    urls = [i for n, i in enumerate(urls) if i not in urls[:n]] # Clears duplicates
    makeDirectories(folderName)
    download_videos(urls, folderName, dataType)
    cleanFolder(tempFolder)

start()