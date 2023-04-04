#!/usr/bin/env python3

import sys
import creds
from config import get_config

def main():
    sys.argv.append("--test")
    config=get_config()
    smug=creds.create_smug(config)
    google=creds.get_google()
    photos=creds.get_google_photo()
    
    return smug,google,photos

if __name__=="__main__":
    smug,google,photos=main()
    smug.ls(user="4reil",path="",details=True)
