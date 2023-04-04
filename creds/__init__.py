from pathlib import Path
import os
homedir=str(Path.home())
import json

CREDDIR=os.path.join(homedir,".smug")
if not os.path.exists(CREDDIR):
    os.makedirs(CREDDIR)

# Google cloud
try:
    from google.cloud import storage
except:
    if 1==1:
        print("Google cloud will not work")
    else:
        raise Exception("Google cloud library needed")


# google photos
try:
    from gphotospy import authorize
    from gphotospy.album import Album
    from gphotospy.media import Media
except:
    if 1==1:
        print("gphotospy will not work")
    else:
        raise Exception("gphotospy needed")

try:
    import smugcli
    from smugcli import smugmug as smugmug_lib
    from smugcli.smugmug_fs import SmugMugFS
except:
    if 1==1:
        print("smugcli will not work")
    else:
        raise Exception("smugcli needed")


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
    #https://developers.google.com/photos/library/guides/get-started#configure-app
    CREDDIR=os.path.join(homedir,".smug","google_credentials.json")
    print("Go to https://developers.google.com/photos/library/guides/get-started#configure-app and save to",CREDDIR)
    return None

def get_google_photo():
    try:
        CREDDIR=os.path.join(homedir,".smug","google_credentials.json")
        service = authorize.init(CREDDIR)
        album_manager = Album(service)
        media_manager = Media(service)
        return album_manager,media_manager
    except:
        return create_google()

def get_google():
    try:
        CREDDIR=os.path.join(homedir,".smug","google-service-account-key.json")
        if not os.path.exists(CREDDIR):
            create_google()
            raise Exception("Need to create creddir")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS']=CREDDIR
        googleclient = storage.Client()
        return googleclient
    except:
        return None
    
def create_smug(configin):
    api_key=configin['api_key']
    oauth_secret=configin['oauth_secret']    
    auth_file=os.path.join(homedir,".smug","smuglogin.json")
    try:
        # Read in prior config
        with open(auth_file, "r") as infile:
            config=json.loads(infile.read())
        smugmug = smugmug_lib.SmugMug(config)
        fs = SmugMugFS(smugmug)
        print("Loaded prior smumug login")
    except:
        # Generate credentials by logging in
        print("Creating and saving smugmug login. Need only one time.")
        smugmug = smugmug_lib.SmugMug(config=dict())
        fs = SmugMugFS(smugmug)
        fs.smugmug.login(api_key)
        print("JSON",json.dumps(fs.smugmug.config))
        with open(auth_file, "w") as outfile:
            outfile.write(json.dumps(fs.smugmug.config))
        print("Saved smumug login for later use.")
    finally:
        return fs

def get_smug(configin):
    return create_smug(configin)
