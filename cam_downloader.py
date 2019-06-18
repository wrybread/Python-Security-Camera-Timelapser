#!/usr/bin/python




'''

Python script to save a static image from a security camera for timelapses.

Saves a single static image (sinkingsensation.com/cam/saved.jpg) and a
timestamped file to a directory of pics (sinkingsensation.com/cam/timelapse)

I'm running it on a webserver, but it could be triggered on any computer.
Here's my crontab line to run it once a minute:

* * * * *  ~/sinkingsensation.com/cam/cam_downloader.py

By wrybread@gmail.com

'''


import os, urllib, time, shutil






# URL to get a static image from the camera
camera_image_url = "https://nexusapi-us1.dropcam.com/get_image?uuid=d62aa97fdae445af8ebea9328d5fcb06&width=1000"

# filename (path) to save a static image
saved_image_path = os.path.expanduser("~") + "/sinkingsensation.com/cam/saved.jpg"

# directory to store all the timestamped images 
timelapse_directory = os.path.expanduser("~") + "/sinkingsensation.com/cam/timelapse/"





# create the target directory if it doesn't exist
try: os.makedirs( os.path.dirname(saved_image_path) )
except: pass

# download an image from the camera a temp file so people aren't trying to load an incomplete image
urllib.urlretrieve(camera_image_url, "temp.jpg")

# copy it to our final path after downloaded
shutil.copyfile("temp.jpg", saved_image_path)



# save a timestamped file to the timelapse directory
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
timelapse_fname = os.path.abspath(timelapse_directory + "/" + timestamp + ".jpg")

try: os.makedirs(timelapse_directory)
except: pass

shutil.copyfile("temp.jpg", timelapse_fname)

