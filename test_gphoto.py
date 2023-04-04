#!/usr/bin/env python3

import os
import sys

import creds
from config import get_config
from gphotospy.media import date_range,date,MediaItem

def main():
    config=get_config()
    a,m=creds.get_google_photo()
    #albums, media, utils
    return a,m

if __name__=="__main__":
    a,m=main()
    #smug.ls(user="4reil",path="",details=True)
#    album_list=a.list()
#    al=[]
#    for a in album_list:
#        try:
#            print(a['title'])
#        except:
#            continue
#        al.append(a)

    models={}
    total=0
    for i in m.list():
        total+=1
        if total%1000==0:
            print("total at",total)
            break
    count=0
    #help(m.list)
    combined_iterator = m.search(
        filter=[
            date_range(
                start_date=date(2019, 1, 1),
                end_date=date(2019, 12, 31)
            )
        ])
    
    for i in combined_iterator:
        count+=1
        try:
            ct=i['mimeType']
        except:
            continue
        photo=i['mediaMetadata']
        try:
            if photo['photo']=={}:
                continue
        except:
            continue
        #print(photo)
        try:
            models[photo['photo']['cameraModel']]+=1
        except:
            try:
                models[photo['photo']['cameraModel']]=1
            except:
                continue
        print(count,"of",total,models)
        image=MediaItem(i)
        if os.path.exists(image.filename()):
            print(image.filename(),"exists.")
            continue
        with open(image.filename(), 'wb') as output:
            output.write(image.raw_download())

