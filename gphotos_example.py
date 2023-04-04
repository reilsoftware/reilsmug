import json
import tkinter
from gphotospy import authorize
from gphotospy.media import *
# the following file is available as a gist here:
# https://gist.github.com/davidedelpapa/2c9a0d2a3e0eada5782aeda93a90c0fa
from video_show import ImgVideoCapture, VideoApp

# Select secrets file
CLIENT_SECRET_FILE = "gphoto_oauth.json"

# Get authorization and return a service object
service = authorize.init(CLIENT_SECRET_FILE)

# Construct the media manager
media_manager = Media(service)

# Get iterator over the list of media
media_iterator = media_manager.list()

# Let's get the first media in the list
first_media = next(media_iterator)

# Let's pretty print first_media
print(json.dumps(first_media, indent=4))

# FILTERS

# Lets get a date; without specifying the year it is a recurrent date
# That is, every years's December 25 is gotten as result

xmas = date(month=12, day=25)

# Let's get also today (for example May 26th, 2020)

today = date(2020, 5, 26)

# Let's search
xmas_iterator = media_manager.search(xmas)
print(next(xmas_iterator))

today_iterator = media_manager.search(today)
today_media = list(today_iterator)
print(len(today_media))  # how many media today?

# Date ranges

festivities = date_range(xmas, date(0, 12, 31))
festivities_iterator = media_manager.search(festivities)
print(next(festivities_iterator))

# Media type

photo_iterator = media_manager.search(MEDIAFILTER.PHOTO)
print(next(photo_iterator))

# Map to MediaItem and get type

a_media = MediaItem(today_media[0])
print(a_media)  # pretty-printed
print(a_media.is_photo())  # Ture or False accordingly
print(a_media.metadata())  # metadata object

# Back to filters, we have also feature filters

favourite_iterator = media_manager.search(FEATUREFILTER.FAVORITES)
try:
    print(next(favourite_iterator))
except (StopIteration, TypeError) as e:
    print("No featured media.")

# Content filter

houses_iterator = media_manager.search(CONTENTFILTER.HOUSES)
print(next(houses_iterator).get("filename"))

# Combined search, exclusions, putting all together

combined_search_iterator = media_manager.search(
    [CONTENTFILTER.HOUSES, CONTENTFILTER.SPORT])

exclude_some_iterator = media_manager.search(
    filter=[CONTENTFILTER.ARTS],
    exclude=[CONTENTFILTER.CRAFTS])

combined_iterator = media_manager.search(
    filter=[
        FEATUREFILTER.NONE,
        CONTENTFILTER.TRAVEL,
        CONTENTFILTER.SELFIES,
        MEDIAFILTER.PHOTO,
        date(2020, 4, 24),
        date_range(
            start_date=date(2020, 4, 19),
            end_date=date(2020, 4, 21)
        )
    ],
    exclude=[
        CONTENTFILTER.PEOPLE,
        CONTENTFILTER.GARDENS])

combined_iterator = media_manager.search(
    filter=[
        FEATUREFILTER.NONE,
        MEDIAFILTER.VIDEO,
        date(2020, 4, 24),
        date_range(
            start_date=date(2020, 4, 19),
            end_date=date(2020, 4, 21)
        )
    ])

# Download a picture

photo_iterator = media_manager.search(MEDIAFILTER.PHOTO)
media = MediaItem(next(photo_iterator))
with open(media.filename(), 'wb') as output:
    output.write(media.raw_download())

# search for a video

video_iterator = media_manager.search(MEDIAFILTER.VIDEO)
media = MediaItem(next(video_iterator))

# Create a new VideoApp
root = tkinter.Tk()
VideoApp(root, media)

# Fetch again for a video
media2 = MediaItem(next(video_iterator))

# Create a second VideoApp anew
root = tkinter.Tk()
VideoApp(root, media2, "Second media")
