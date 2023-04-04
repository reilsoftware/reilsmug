import os
import pickle
from PIL import Image, ExifTags
from pathlib import Path
import shutil
import platform
#import ffmpeg
#import cv2
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
# pip3 install drive for Google Drive
#from drive import Client
from google.cloud import storage
import creds
import json
import requests
import hashlib

class imageList:
    def __init__(self,config_in={}):
        self.local=True
        self.imageList=[]
        self.test=False
        try:
            self.verbose=config_in['verbose']
        except:
            self.verbose=0
        self.exttuple=('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')
        self.dbname=".localDB"
        self.delete=True
        self.hostname=platform.node()
        self.root=config_in['photo_directory']
        self.homedir=str(Path.home())
        try:
            a,m=creds.get_google_photo()
            self.googlealbums = a
            self.googlemedia = m
            #self.googlerootdir=self.googleroot.get_or_create_folder("year")
        except:
            self.googlealbums=None
            self.googlemedia=None
            print("ERROR: Failed to get google client")

        try:
            self.smug=creds.get_smug(config_in)
            self.smuguser=self.smug.smugmug.get_auth_user() # Loads authorized user into the smugmug config variable
        except:
            print("ERROR: Failed to log in to smugmug")
            self.smug=None

    def print(self,l1,l2="",l3="",l4=""):
        if l3=="": l3=l2
        if l4=="": l4=l2
        if self.verbose==0: return
        if self.verbose==1:
            print(l1,end="",flush=True)
        elif self.verbose==2 and l2!="":
            print(l2)
        elif self.verbose==3:
            print(l3)
        elif self.verbose==4:
            print(l4)
        else:
            return
    
    def getSmug(self):
        return self.smug
    
    def getSmugUser(self):
        return self.smuguser
    def getSmugDirs(self,d1in="",d2in=""):
        print("Building SmugMug file list",os.path.join(d1in,d2in))
        rlist=[]
        d1list=self.smug.ls2(self.smuguser,"","")
        for d1 in d1list:
            if d1in!="" and d1.name!=d1in:continue
            if len(d1.name)!=4: continue
            if not d1.name[0]=='2': continue
            #print(d1.name)
            d2list=self.smug.ls2(self.smuguser,d1.name,"")
            for d2 in d2list:
                if d2in!="" and d2.name!=d2in: continue
                if len(d2.name)!=6: continue
                if not d2.name.startswith(d1.name): continue
                #print("   ",d2.name)
                d3list=self.smug.ls2(self.smuguser,os.path.join(d1.name,d2.name),"")
                for d3 in d3list:
                    if not d3.name.startswith(d2.name): continue
                    print("   ","   ",d3.__dict__)
                    print("")
                    rlist.append(os.path.join(d1.name,d2.name,d3.named))
        return rlist
    def setSmug(self,smugin):
        self.smug=smugin
    def getList(self):
        return self.imageList

    def getGoogleRoot(self):
        return self.googleclient.root()
    def listGoogle(self):
        cdir=self.googleroot
        for f in cdir.list():
            print(f)
    def changeDBName(self,dbname):
        self.dbname=dbname
    def changeExtTuple(self, tin):
        if tin=='images': self.exttuple=('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')
        elif tin=='movies': self.exttuple=('.mov', '.mpg', '.avi', '.mp4')
        else: self.exttuple=('.mov', '.mpg', '.avi', '.mp4')
    def loadDB(self):
        home=self.homedir
        dbdir=os.path.join(home,".smug")
        if not os.path.exists(dbdir): os.makedirs(dbdir)
        dbname=os.path.join(dbdir,self.dbname)
        if not os.path.exists(dbname): return
        self.imageList=pickle.load(open(dbname,"rb"))
        print("Loaded",dbname,len(self.imageList))

    def saveDB(self):
        home = str(Path.home())
        dbdir=os.path.join(home,".smug")
        if not os.path.exists(dbdir): os.makedirs(dbdir)
        dbname=os.path.join(dbdir,self.dbname)
        pickle.dump(self.imageList,open(dbname,"wb"))
        print("Saved",dbname)
    def addImage(self,newImage):
        if not 'rawName' in newImage.keys(): raise
        self.imageList.append(newImage)

    def get_exif(self,path):
        keeptags=('Make','Model','DateTime','ExifImageHeight','ExifImageWidth',
                  
                  )
        exifData = {}
        try:
            img = Image.open(path)
            exifDataRaw = img._getexif()
            if exifDataRaw==None: return {}
            for tag, value in exifDataRaw.items():
                decodedTag = ExifTags.TAGS.get(tag, tag)
                if not decodedTag in keeptags: continue
                exifData[decodedTag] = value
        except:
            #help(exifread)
            try:
                parser = createParser(path)
                metadata = extractMetadata(parser)
                exifData=metadata.exportDictionary()['Metadata']
                exifData['DateTime']=exifData['Creation date'].replace("-",":",2)
                print(path)
                print(exifData)
            except:
                print("Failed exif and video metadata")
            print("")
        return exifData

    def copyImage(self, old, new):
        return self.moveImage(old,new,movetype="copy")
    def moveImage(self, old, new, movetype="move",**kwargs):

        if new.startswith("SMUGMUG"):
            pass
        elif new.startswith("GOOGLE"):
            pass
        elif new.startswith("AMAZON"):
            pass
        else:
            if os.path.exists(new):
                if self.delete:
                    try:
                        os.remove(old)
                    except:
                        pass
                return
            newdir=os.path.dirname(new)
            if not os.path.exists(newdir):
                print("___Need to create",newdir)
                os.makedirs(newdir)
            if movetype=="move":
                shutil.move(old,new)
            elif movetype=="copy":
                shutil.copy(old,new)
        
    def checkExists(self,keyIn,valueIn):
        for image in self.imageList:
            if image[keyIn]==valueIn: return True
        return False
        
    def addImagesFromDirectory(self,directoryIn,**kwargs):
        
        exttuple=self.exttuple
        #kwargs godeep check all files, not just those with correct extensions
        for root, dirs, files in os.walk(directoryIn):
            for filename in files:
                #print(root,filename)
                if not filename.lower().endswith(exttuple): continue
                fullname=os.path.join(root,filename)
                if self.checkExists("FullName",fullname):
                    #print(filename,"already in DB")
                    continue
                exif=self.get_exif(fullname)
                if not "DateTime" in exif.keys():
                    #print(filename,"no DateTime")
                    continue
                exif['FullName']=fullname
                exif['FileName']=filename
                exif['host']=self.hostname
                self.imageList.append(exif)

    def addImagesFromSmug(self,directoryIn,depth=0,fullJSON=False,**kwargs):
        self.print("L","Listing "+directoryIn)
        exttuple=self.exttuple
        listin=self.smug.ls2(user=self.smuguser,
                             path=directoryIn,
                             details=False)
        for i in listin:
            if 'Image' in i._json['Uris'].keys():
                rdict={}
                rdict['host']="SmugMug"
                rdict['FileName']=i._json['FileName']
                rdict['FullName']=os.path.join(directoryIn,i._json['FileName'])
                rdict['DateTime']=i._json['DateTimeOriginal'].split("+")[0].replace("T"," ").replace("-",":",2)
                rdict['ArchivedMD5']=i._json['ArchivedMD5']
                rdict['ArchivedSize']=i._json['ArchivedSize']
                rdict['ArchivedUri']=i._json['ArchivedUri']
                if fullJSON:
                    rdict['json']=i._json
                self.imageList.append(rdict)
                self.print("+","","Loaded "+rdict['FileName']+" from SmugMug")
                continue
            else:
                dirname=os.path.join(directoryIn,i._json['Name'])
                listin2=self.addImagesFromSmug(dirname,depth+1)
            pass
        return self.imageList

    def download(self,fullpath,URI,size_expected=0,md5=0):

        if self.verbose>1:
            self.print("","Downloading "+fullpath)

        # Do not download if it exists
        # Add an overwrite existing option?
        if os.path.exists(fullpath):
            self.print("e","File already exists "+fullpath)
            return -1

        # Grab the data from the URI
        r=requests.get(URI)
        if not r.status_code==200:
            self.print("F","Failed to download "+fullpath)
            return -2

        # Chunk the download
        data=bytes()
        if not self.test:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    data+=chunk

        # Is the download the size we expect?
        size_downloaded=len(data)
        if size_expected>0:
            if not (size_downloaded==size_expected):
                print("Failed to download (size)",fullpath,
                      size_downloaded,size_expected)
                return -3
        if not md5==0:
            dl_md5=hashlib.md5(data)
            if not md5==dl_md5.hexdigest():                
                print("Failed to download (md5)",fullpath,
                      md5,dl_md5.hexdigest())
                return -4
        
        # Check if a directory is needed
        dname=os.path.dirname(fullpath)
        if not os.path.exists(dname):
            self.print("C","Creating "+dname)
            os.makedirs(dname)
        if not os.path.exists(dname):
            self.print("F","Failed to create "+dname)
            return -5
        if os.path.exists(dname):
            if not os.path.isdir(dname):
                self.print("D","Directory is not a directory "+dname)
                return -6

        try:
            if not self.test:
                f=open(fullpath,"wb")
                f.write(data)
                f.close()
                self.print("+","")
        except:
            self.print("F",fullpath+" failed on binary write")
            return -7
        return size_downloaded
    
    def buildNewNames(self,location="local",**kwargs):

        for image in self.imageList:
            if location=="local":
                root=self.root
            elif location=="smugmug":
                root=""
            else:
                continue
            ymd,hms=image['DateTime'].split(" ")
            y,m,d=ymd.split(":")
            H,M,S=hms.split(":")
            newname=y+m+d+"_"+H+M+S+"."+image['FileName'].lower().split(".")[-1]
            #image['NewName']=newname
            newdir=os.path.join(root,y,y+m)
            newfullname=os.path.join(newdir,newname)
            image['newFileName']=newname
            image['newFullName']=newfullname
            if self.verbose>=2 and image['FileName']!=image['newFileName']:
                print("   ","   ",image['FileName'],"-->",image['newFileName'])
    def count_files_to_move(self):
        count=0
        for image in self.imageList:
            if not 'newFileName' in image.keys(): continue
            if not 'newFullName' in image.keys(): continue
            if image['newFileName']==image['FileName'] and image['newFullName']==image['FullName']: continue
            if self.verbose>=2:
                print("   ","   ",image['FileName'],"-->",image['newFileName'])
            count+=1
        return count

    def moveFiles(self,**kwargs):
        if 'testrun' in kwargs.keys(): testmode=True
        else: testmode=False

        count=0
        for image in self.imageList:
            if not 'newFileName' in image.keys(): continue
            if not 'newFullName' in image.keys(): continue
                
            if image['newFileName']==image['FileName'] and image['newFullName']==image['FullName']: continue
            if self.verbose>=2:
                print("   ","   ",
                      image['FullName'],"-->",
                      image['newFullName'])
            if not testmode:
                self.moveImage(image['FullName'],image['newFullName'])

            
            image['FullName']=image['newFullName']
            image['FileName']=image['newFileName']
            count+=1
        return count
        



    """
    {'_smugmug': <smugcli.smugmug.SmugMug object at 0x108650e80>, '_json': {'Title': '', 'Caption': '', 'Keywords': '20021208; 120000; 100', 'KeywordArray': ['20021208', '120000', '100'], 'Watermark': 'No', 'Latitude': '0', 'Longitude': '0', 'Altitude': 0, 'Hidden': False, 'ThumbnailUrl': 'https://photos.smugmug.com/photos/i-Hhw89pn/0/Th/i-Hhw89pn-Th.jpg', 'FileName': '20021208_120000-100.jpg', 'Processing': False, 'UploadKey': '3833792058', 'Date': '2015-01-21T03:50:15+00:00', 'DateTimeUploaded': '2015-01-21T03:50:15+00:00', 'DateTimeOriginal': '2002-12-08T20:00:00+00:00', 'Format': 'JPG', 'OriginalHeight': 1600, 'OriginalWidth': 1200, 'OriginalSize': 543264, 'LastUpdated': '2015-01-21T03:50:17+00:00', 'Collectable': True, 'IsArchive': False, 'IsVideo': False, 'ComponentFileTypes': {'Image': ['jpg']}, 'CanEdit': True, 'CanBuy': True, 'Protected': False, 'EZProject': False, 'Watermarked': False, 'ImageKey': 'Hhw89pn', 'Serial': 0, 'ArchivedUri': 'https://photos.smugmug.com/2002/200212/i-Hhw89pn/0/4c7ea5a6/D/20021208_120000-100-D.jpg', 'ArchivedSize': 543264, 'ArchivedMD5': 'ea27a156e3e7dd75c5a65ab55ba87845', 'CanShare': True, 'Comments': True, 'ShowKeywords': True, 'FormattedValues': {'Caption': {'html': '', 'text': ''}, 'FileName': {'html': '20021208_120000-100.jpg', 'text': '20021208_120000-100.jpg'}}, 'PreferredDisplayFileExtension': 'JPG', 'Uri': '/api/v2/album/R5WP6X/image/Hhw89pn-0', 'WebUri': 'https://4reil.smugmug.com/2002/200212/i-Hhw89pn', 'UriDescription': 'Image from album', 'Uris': {'LargestImage': {'Uri': '/api/v2/image/Hhw89pn-0!largestimage', 'Locator': 'LargestImage', 'LocatorType': 'Object', 'UriDescription': 'Largest size available for image', 'EndpointType': 'LargestImage'}, 'ImageSizes': {'Uri': '/api/v2/image/Hhw89pn-0!sizes', 'Locator': 'ImageSizes', 'LocatorType': 'Object', 'UriDescription': 'Sizes available for image', 'EndpointType': 'ImageSizes'}, 'ImageSizeDetails': {'Uri': '/api/v2/image/Hhw89pn-0!sizedetails', 'Locator': 'ImageSizeDetails', 'LocatorType': 'Object', 'UriDescription': 'Detailed size information for image', 'EndpointType': 'ImageSizeDetails'}, 'PointOfInterest': {'Uri': '/api/v2/image/Hhw89pn-0!pointofinterest', 'Locator': 'PointOfInterest', 'LocatorType': 'Object', 'UriDescription': 'Point of interest for image', 'EndpointType': 'PointOfInterest'}, 'PointOfInterestCrops': {'Uri': '/api/v2/image/Hhw89pn-0!poicrops', 'Locator': 'PointOfInterestCrops', 'LocatorType': 'List', 'UriDescription': 'PointOfInterest Crops for image', 'EndpointType': 'PointOfInterestCrops'}, 'Regions': {'Uri': '/api/v2/image/Hhw89pn-0!regions', 'Locator': 'Region', 'LocatorType': 'Objects', 'UriDescription': 'Regions for image', 'EndpointType': 'Regions'}, 'ImageAlbum': {'Uri': '/api/v2/album/R5WP6X', 'Locator': 'Album', 'LocatorType': 'Object', 'UriDescription': 'Album by key', 'EndpointType': 'Album'}, 'ImageOwner': {'Uri': '/api/v2/user/4reil', 'Locator': 'User', 'LocatorType': 'Object', 'UriDescription': 'User By Nickname', 'EndpointType': 'User'}, 'ImageAlbums': {'Uri': '/api/v2/image/Hhw89pn-0!albums', 'Locator': 'Album', 'LocatorType': 'Objects', 'UriDescription': 'Albums the image is included in', 'EndpointType': 'ImageAlbums'}, 'ImageDownload': {'Uri': '/api/v2/image/Hhw89pn-0!download', 'Locator': 'ImageDownload', 'LocatorType': 'Object', 'UriDescription': 'Download image', 'EndpointType': 'ImageDownload'}, 'ImageComments': {'Uri': '/api/v2/image/Hhw89pn-0!comments', 'Locator': 'Comment', 'LocatorType': 'Objects', 'UriDescription': 'Comments on image', 'EndpointType': 'ImageComments'}, 'RotateImage': {'Uri': '/api/v2/image/Hhw89pn-0!rotate', 'UriDescription': 'Rotate an image', 'EndpointType': 'RotateImage'}, 'ColorImage': {'Uri': '/api/v2/image/Hhw89pn-0!color', 'Locator': 'ColorImage', 'LocatorType': 'Object', 'UriDescription': 'Color an image', 'EndpointType': 'ColorImage'}, 'CopyImage': {'Uri': '/api/v2/image/Hhw89pn-0!copy', 'UriDescription': 'Copy an image', 'EndpointType': 'CopyImage'}, 'CropImage': {'Uri': '/api/v2/image/Hhw89pn-0!crop', 'UriDescription': 'Crop an image', 'EndpointType': 'CropImage'}, 'ImageMetadata': {'Uri': '/api/v2/image/Hhw89pn-0!metadata', 'Locator': 'ImageMetadata', 'LocatorType': 'Object', 'UriDescription': 'Metadata for image', 'EndpointType': 'ImageMetadata'}, 'ImagePrices': {'Uri': '/api/v2/image/Hhw89pn-0!prices', 'Locator': 'CatalogSkuPrice', 'LocatorType': 'Objects', 'UriDescription': 'Purchasable Skus', 'EndpointType': 'ImagePrices'}, 'ImagePricelistExclusions': {'Uri': '/api/v2/image/Hhw89pn-0!pricelistexclusions', 'Locator': 'ImagePricelistExclusions', 'LocatorType': 'Object', 'UriDescription': 'Pricelist information for an image', 'EndpointType': 'ImagePricelistExclusions'}, 'Album': {'Uri': '/api/v2/album/R5WP6X', 'Locator': 'Album', 'LocatorType': 'Object', 'UriDescription': 'Album by key', 'EndpointType': 'Album'}, 'Image': {'Uri': '/api/v2/image/Hhw89pn-0', 'Locator': 'Image', 'LocatorType': 'Object', 'UriDescription': 'Image by key', 'EndpointType': 'Image'}, 'AlbumImagePricelistExclusions': {'Uri': '/api/v2/album/R5WP6X/image/Hhw89pn-0!pricelistexclusions', 'Locator': 'AlbumImagePricelistExclusions', 'LocatorType': 'Object', 'UriDescription': 'Pricelist information for an album image', 'EndpointType': 'AlbumImagePricelistExclusions'}, 'AlbumImageMetadata': {'Uri': '/api/v2/album/R5WP6X/image/Hhw89pn-0!metadata', 'Locator': 'AlbumImageMetadata', 'LocatorType': 'Object', 'UriDescription': 'Metadata for AlbumImage', 'EndpointType': 'AlbumImageMetadata'}, 'AlbumImageShareUris': {'Uri': '/api/v2/album/R5WP6X/image/Hhw89pn-0!shareuris', 'Locator': 'AlbumImageShareUris', 'LocatorType': 'Object', 'UriDescription': 'URIs that are useful for sharing', 'EndpointType': 'AlbumImageShareUris'}}, 'Movable': True, 'Origin': 'Album'}, '_parent': <smugcli.smugmug.Node object at 0x108708610>, '_child_nodes_by_name': None, '_lock': <unlocked _thread.lock object at 0x10d0fabd0>}

"""
