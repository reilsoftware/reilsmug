#!/usr/bin/env python3

from images import imageList
from config import get_config
import os
from pprint import pprint

def main():
    config=get_config()
    ilist=imageList(config)

    return ilist


    
    for i in ilist.getList():
        if not i['host']==ilist.hostname:
            #print(i['host'])
            continue
        if not any(i2['FileName']==i['FileName'] and i2['host']=='SmugMug' for i2 in ilist.getList()):
            print("Local",i['FileName'],"Not Matched on SmugMug")
        else:
            #print("   Matched")
            continue

    for i in ilist.getList():
        if not i['host']=="SmugMug":
            #print(i['host'])
            continue
        if not any(i2['FileName']==i['FileName'] and i2['host']==ilist.hostname for i2 in ilist.getList()):
            print("SmugMug",i['FileName'],"Not Matched Locally")
            yy=i['FileName'][0:4]
            yymm=i['FileName'][0:6]
            try:
                newFullName=i['newFullName']
            except:
                continue
            print("   ",newFullName)
            print(i)
            break
        else:
            #print("   Matched")
            continue


    return ilist

if __name__=="__main__":
    ilist=main()
    ilist.loadDB()
    #ilist.addImagesFromSmug("2002/200212")
    #ilist.saveDB()
    for f in ilist.getList():
        if not f['host']=='SmugMug': continue
        pprint(f)
        fullpath=os.path.join(ilist.root,f['FullName'])
        print(fullpath)
