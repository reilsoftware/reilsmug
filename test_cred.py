#!/usr/bin/env python3

import sys
import creds
import config

def main():
    sys.argv.append("--test")
    sys.argv.append("--login")
    try:
        c=config.config().get_config()
    except:
        raise("No config!!!")

    smug=creds.get_smug(c)
    google=creds.get_google()
    photos=creds.get_google_photo()
        
    
    return smug,google,photos

if __name__=="__main__":
    smug,google,photos=main()
    print("Smug",smug)
    print("Google",google)
    print("Gphotospy",photos)
    #smug.ls(user="4reil",path="",details=True)
