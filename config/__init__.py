import argparse
from pathlib import Path
import os
import pickle

def get_config():
    """
    store_list is the parameters that should be saved in the .config file
    all store_list keys are automatically added to the parser with defaults of
    None if not already in .config or default of the currently stored value
    """
    store_list=[]
    store_list.append("api_key")
    store_list.append("oauth_secret")
    store_list.append("photo_directory")

    home_dir=str(Path.home())
    config_dir=os.path.join(home_dir,".smug")
    config_file=os.path.join(config_dir,".config")
    if not os.path.exists(config_dir): os.makedirs(config_dir)
    try:
        config=pickle.load(open(config_file,"rb"))
    except:
        config={}

    
    parser = argparse.ArgumentParser(description='ReilSmug command line')
    for k in store_list:
        if k in config.keys():
            parser.add_argument('--'+k,default=config[k])
        else:
            parser.add_argument('--'+k,default=None)
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="increase output verbosity")
    parser.add_argument("--search_directory",
                        default=os.path.join(home_dir,"Pictures","sort"),
                        help="the directory to search for photos"
                        )
    parser.add_argument("--shallow", dest="deep_search", action="store_false",
                        default=True,
                        help="Do not recurse dirs below search_directory")
    parser.add_argument("--test", dest="testrun", action="store_true",
                        default=False,
                        help="Testmode - do not move/copy/etc just determine what would happened")
    

    args=parser.parse_args()

    # Copy args keys into config dictionary
    for k in args.__dict__.keys():
        config[k]=args.__dict__[k]

    # If verbose 2 then print out config
    if config['verbose']>=2:
        for k in args.__dict__.keys():
            print("   ",k,args.__dict__[k])

    out_config={}
    for k in store_list:
        if k in config.keys(): out_config[k]=config[k]
    pickle.dump(out_config,open(config_file,"wb"))
    if config['verbose']>=1: print("Saved",config_file)
    
    return config
