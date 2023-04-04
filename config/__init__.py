import argparse
from pathlib import Path
import os
import pickle

class config:
    def __init__(self):
        self.config=self.get_config()
        self.check_config(self.config)
        print(self.config)
        if self.config['verbose']>0:
            print("-"*30)
            print("Running with the following configuration")
            for k in self.config.keys():
                print(k,self.config[k])
            print("-"*30)
    def check_config(self,config):
        # Must have a photo_directory
        test=config['photo_directory']
        if test==None:
            raise Exception("Cannot run without photo_directory specified")
        # Must have an api_key
        test=config['api_key']
        if test==None:
            raise Exception("Cannot run without api_key, use --api_key")
        #Must be logged in
        test=config['oath_secret']
        if test==None:
            raise Exception("No Oath Secret run login first")
        #Must be logged in
        test=config['access_token']
        if test==None:
            raise Exception("No access_token run login first")
        
            

    def get_config(self):

        home_dir=str(Path.home())
        config_dir=os.path.join(home_dir,".smug")
        config_file=os.path.join(config_dir,".config")
        if not os.path.exists(config_dir): os.makedirs(config_dir)
        try:
            config=pickle.load(open(config_file,"rb"))
            print("Loaded config from",config_file)
            print(config)
        except:
            config={}

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

        args=parser.parse_args()


        config['config_file']=config_file
        # Copy args keys into config dictionary
        for k in args.__dict__.keys():
            config[k]=args.__dict__[k]

        # If verbose 2 then print out config
        if config['verbose']>=1:
            for k in args.__dict__.keys():
                print("   ",k,args.__dict__[k])

        out_config={}
        for k in store_list:
            if k in config.keys(): out_config[k]=config[k]
            pickle.dump(out_config,open(config_file,"wb"))
        if config['verbose']>=1: print("Saved",config_file)
    
        return config
