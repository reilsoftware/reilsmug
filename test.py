#!/usr/bin/env python3

import os
import sys
from config import get_config
from images import imageList

def main():
    sys.argv.append("--test")
    config=get_config()

    print("Searching of files in",config['search_directory'])
    ilist=imageList(config)
    ilist.loadDB()
    ilist.addImagesFromDirectory(config['search_directory'])
    ilist.buildNewNames(**config)
    print("Need to move",ilist.count_files_to_move())
    nmoved=ilist.moveFiles()
    print("Moved",nmoved,"files")
    ilist.saveDB()


    return
    vlist=imageList()
    vlist.changeDBName(".videos")
    vlist.changeExtTuple('movies')
    vlist.changeRootDir("/Users/reil/Pictures/video_year")
    vlist.addImagesFromDirectory("/Users/reil/Pictures/")
    vlist.buildNewNames()
    print("Need to move",vlist.count_files_to_move())
    vlist.moveFiles()
    vlist.saveDB()
    return


if __name__=="__main__":
    main()
