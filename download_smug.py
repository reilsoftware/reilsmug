#!/usr/bin/env python3

from images import imageList
from config import get_config
import os
from pprint import pprint
import requests
#import taskmanager
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed


def main():
    config=get_config()
    ilist=imageList(config)
    return ilist

if __name__=="__main__":
    ilist=main()
    ilist.loadDB()
    ilist.addImagesFromSmug("2002",fullJSON=False)
    if ilist.verbose==0:print()
    ilist.saveDB()
    
    ndown=0
    for f in ilist.getList():
        if not f['host']=='SmugMug': continue
        ndown+=1

    pool = ThreadPoolExecutor(max_workers=3)

    futures=[]
    print("Downloading",ndown,"images")
    for f in ilist.getList():
        if not f['host']=='SmugMug': continue
        fullpath=os.path.join(ilist.root,f['FullName'])
        if 1==1:
            futures.append(pool.submit(ilist.download,
                                       fullpath,f['ArchivedUri'],
                                       int(f['ArchivedSize']),
                                       f['ArchivedMD5']))
        else:
            ilist.download(
                fullpath,f['ArchivedUri'],
                int(f['ArchivedSize']),
                f['ArchivedMD5'])
    if ilist.verbose==0: print()
    for future in as_completed(futures):
	# get the result
        result = future.result()
        print(result," ",end="",flush=True)
	# do something with the result...
    if ilist.verbose==0: print()
    pool.shutdown()
