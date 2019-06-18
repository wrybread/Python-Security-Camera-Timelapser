# Python-Security-Camera-Image-Downloader-For-Timelapses
These are the scripts I wrote to build this timelapse:

https://vimeo.com/316945847

There's two Python scripts: 

**cam_downloader.py** downloads a static image (http://sinkingsensation.com/cam/saved.jpg) from any security camera that has a URL for static images as well as a timestamped version it places in a directory (http://sinkingsensation.com/cam/timelapse) for building a timelapse later. I run it on a webserver, pulling an image once a minute with this line:

* * * * *  ~/whatever.com/cam_downloader.py

**timelapser.py** builds a timelapse movie from the directory of saved images.

Note that timelapser.py could easily be used to build a movie from any directory of images, but you'll want to turn off the timestamp feature (change "add_timestamps = 1" at the top of the file to "add_timestamps = 0") since it tries to determine the timestamp from the filename of the pics. 

If you're adding timestamps, it expects the files to have this format: 2019-02-03_02-06-15.jpg

I included some sample pics in the /pics directory, and the Windows version of ffmpeg I'm using, so on Windows it should work out of the box. On other OS's you'll need to set the path to ffmpeg at the top of the script.

I'm using this ffmpeg command by the way, where imagepaths.txt is a text file containing a list of the pics:

ffmpeg.exe -y -r 80 -f concat -safe 0 -i imagepaths.txt -vcodec libx264 -s 1280x720 -crf 18 -preset slow -r 30 output.mp4

Not yet tested on Python 3 yet, I'm still using Python 2.7.



