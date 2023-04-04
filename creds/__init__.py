from pathlib import Path
import os
homedir=str(Path.home())
import json

CREDDIR=os.path.join(homedir,".smug")
if not os.path.exists(CREDDIR):
    os.makedirs(CREDDIR)

# Google cloud
from google.cloud import storage

# google photos
from gphotospy import authorize
from gphotospy.album import Album
from gphotospy.media import Media

#smugmug command line interface
#from smugcli import smugmug_oauth
import smugcli
from smugcli import smugmug as smugmug_lib
from smugcli.smugmug_fs import SmugMugFS


def ls2(self, user, path, details):
    user = user or self._smugmug.get_auth_user()
    matched_nodes, unmatched_dirs = self.path_to_node(user, path)
    if unmatched_dirs:
        print('"%s" not found in "%s".' % (
            unmatched_dirs[0], os.sep.join(m.name for m in matched_nodes)))
        return

    node = matched_nodes[-1]
    nodes = ([(path, node)] if 'FileName' in node else
             [(child.name, child) for child in node.get_children()])

    rlist=[]
    for name, node in nodes:
        rlist.append(node)
    return rlist

SmugMugFS.ls2=ls2
    
def create_google():
    pass

def get_google_photo():
    CREDDIR=os.path.join(homedir,".smug","kevin.reil.photos.cred")
    service = authorize.init(CREDDIR)
    album_manager = Album(service)
    media_manager = Media(service)
    return album_manager,media_manager

def get_google():
    CREDDIR=os.path.join(homedir,".smug","google-service-account-key.json")
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']=CREDDIR
    googleclient = storage.Client()
    return googleclient

def create_smug(config):
    api_key=config['api_key']
    oauth_secret=config['oauth_secret']
    
    SMUGCREDDIR=os.path.join(homedir,".smug","smug.json")
    try:
        # Read in prior config
        with open(SMUGCREDDIR, "r") as infile:
            config=json.loads(infile.read())
        smugmug = smugmug_lib.SmugMug(config)
        fs = SmugMugFS(smugmug)
        print("Loaded prior smumug login")
    except:
        smugmug = smugmug_lib.SmugMug(config=dict())
        fs = SmugMugFS(smugmug)
        fs.smugmug.login((api_key, oauth_secret))
        with open(SMUGCREDDIR, "w") as outfile:
            outfile.write(json.dumps(fs.smugmug.config))
        print("Saved smumug login")
    finally:
        return fs

def get_smug(config):
    return create_smug(config)
