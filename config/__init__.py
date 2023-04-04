import argparse
from pathlib import Path
import os
import json
import pickle

class config:
    def __init__(self):
        self.config=self.get_config()
        self.check_config(self.config)

    def check_config(self,config):
        # Must have a photo_directory
        test=config['photo_directory']
        if test==None:
            raise Exception("Cannot run without photo_directory specified")
        # Must have an api_key
        test=config['api_key']
        if test==None:
            raise Exception("Cannot run without api_key, use --api_key")

        if config['login']: return True
        #Must be logged in
        try:
            test=config['oath_secret']
        except:
            raise Exception("No Oath Secret run login first")
        if test==None:
            raise Exception("No Oath Secret run login first")
        #Must be logged in
        try:
            test=config['access_token']
        except:
            raise Exception("No access_token run login first")
        if test==None:
            raise Exception("No access_token run login first")


    def load_config(self,name=".config"):
        # Make directory configurable?
        home_dir=str(Path.home())
        config_dir=os.path.join(home_dir,".smug")
        config_file=os.path.join(config_dir,name)

        if not os.path.exists(config_dir): os.makedirs(config_dir)
        try:
            self.config=pickle.load(open(config_file,"rb"))
        except:
            print("Failed to load",config_file)
            self.config={}
        self.config['config_file']=config_file

        return self.config
        
    def save_config(self,configin,name=".config"):
        # Make directory configurable?
        home_dir=str(Path.home())
        config_dir=os.path.join(home_dir,".smug")
        config_file=os.path.join(config_dir,name)

        # Create the config directory if needed
        if not os.path.exists(config_dir): os.makedirs(config_dir)
        pickle.dump(configin,open(config_file,"wb"))
        
    def print_config(self):
        for k in self.config.keys():
            print("   ",k,self.config[k])

    def add(self,k,kw):
        self.config[k]=kw

    def get_config(self):
        config=self.load_config()

        store_list=[]
        store_list.append("api_key")
        store_list.append("oauth_secret")
        store_list.append("access_token")
        store_list.append("photo_directory")

            
        parser = argparse.ArgumentParser(description='REIL command line')
        for k in store_list:
            if k in config.keys():
                parser.add_argument('--'+k,default=config[k])
            else:
                parser.add_argument('--'+k,default=None)
        parser.add_argument("-v", "--verbose",
                            action="count", default=0,
                            help="increase output verbosity")

        home_dir=str(Path.home())
        parser.add_argument("--search_directory",
                            default=os.path.join(home_dir,
                                                 "Pictures","sort"),
                            help="the directory to search for photos"
                            )
        parser.add_argument("--shallow", dest="deep_search",
                            action="store_false",
                            default=True,
                            help="Do not recurse dirs")
        parser.add_argument("--test", dest="testrun",
                            action="store_true",
                            default=False,
                            help="Testmode - do not move/copy/etc")
        parser.add_argument("--login",
                            action="store_true",
                            default=False,
                            help="Needs to be run once on first execution")

        args=parser.parse_args()

        if args.__dict__['verbose']>=1:
            print("Config file contents were",config['config_file'])
            self.print_config()

        # Copy args keys into config dictionary
        for k in args.__dict__.keys():
            config[k]=args.__dict__[k]

        # If verbose 2 then print out config
        if config['verbose']>=1:
            print("Update config are")
            self.print_config()

        #Only specified keys will be stored
        out_config={}
        for k in store_list:
            if k in config.keys(): out_config[k]=config[k]
        self.save_config(out_config)
    
        return config
