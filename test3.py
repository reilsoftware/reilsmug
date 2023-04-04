#!/usr/bin/env python3

from images import imageList

def main():
    ilist=imageList()
    ilist.loadDB()
    l=ilist.addImagesFromSmug("2012/201203")
    ilist.buildNewNames()
    ilist.saveDB()
    return ilist

if __name__=="__main__":
    ilist=main()
    
