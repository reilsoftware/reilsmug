#!/usr/bin/env python3

import os
import sys
from config import get_config
from images import imageList

def main():
    sys.argv.append("--test")
    config=get_config()

    ilist=imageList(config)
    ilist.loadDB()
    root=ilist.getGoogleRoot()
    return root

if __name__=="__main__":
    root=main()
