#!/usr/bin/python
# -*- coding: cp1252 -*-



'''

Takes a directory of pics and makes a timelapse using ffmpeg.

Here's a sample of the output: vimeo.com/316945847

Can also add a timestamp to the pictures. It gets the timestamp from the filename, which it expects to be in this format:

_________________

Can disable timestamps if your filenames don't have that format.

Build to be used with cam_downloader.py, but should work with any directory of images.

Uses this ffmpeg command, but can modify it to taste below:

ffmpeg.exe -y -r 80 -f concat -safe 0 -i imagepaths.txt -vcodec libx264 -s 1280x720 -crf 18 -preset slow -r 30 output.mp4

Untested on Python 3 (tested using Python 2.7).



'''



import sys, os, subprocess, time
from datetime import datetime



# figure out the current directory
if getattr(sys, 'frozen', False): current_directory = os.path.dirname(sys.executable)
else: current_directory = os.path.dirname( os.path.abspath(sys.argv[0]) )






###########################
# SET A FEW PARAMTERS HERE
###########################

# what's the directory with all the pics?
pics_dname = os.path.abspath(current_directory + "/pics")

# the output filename (will add a number to it if it exists)
output_fname = current_directory + "/output/output.mp4"

# path to FFMPEG
ffmpeg = os.path.abspath(current_directory + "/ffmpeg.exe")

# add timestamps to the pics?
# Note that it uses the filename to build the timestamp. Edit the format inside overlay_timestamp() as needed
# Disable this if not adding timelapses
add_timestamps = 1

# if using timestamps, setting this to True will use the existing timestamp file if it already exists
reuse_timestamped_pics = 0

# if there's a limit (used for troubleshooting)
# 0 for no limit
number_of_pics_limit = 0

# can skip rebuilding the pic list (for troubleshooting)
rebuild_pic_list = 1

# set FFMPEG params directly in the command building section below










if add_timestamps:
    # import PIL only if adding timestamps
    from PIL import Image
    from PIL import ImageFont
    from PIL import ImageDraw
    





# Add a timestamp to the pic based on it's filename.
# from https://www.amphioxus.org/content/timelapse-time-stamp-overlay
def overlay_timestamp(pic_fname):

    basename = os.path.basename(pic_fname)
    basename_no_ext = os.path.splitext(basename)[0]

    new_filename = os.path.abspath( os.path.dirname(pic_fname) + "/resized/" + basename )
    
    if reuse_timestamped_pics and os.path.exists(new_filename): return new_filename

    print ( "Adding a timestamp to %s" % os.path.basename(pic_fname) )
     
    font = ImageFont.truetype(current_directory + "/fonts/HelveticaNeue-Black.otf", 25)
    fontsmall = ImageFont.truetype(current_directory + "/fonts/HelveticaNeue-Black.otf", 20)
    fontcolor = (238,161,6)

    img = Image.open(pic_fname)

    #widthtarget = 1920
    #heighttarget = 1080

    widthtarget = img.size[0]
    heighttarget = img.size[1]



    # Make a datetime object from the file's timestamp (currently for example 2017-12-29_21-42-19.jpg)    
    dt = datetime.strptime(basename_no_ext, '%Y-%m-%d_%H-%M-%S')

    # format each line    
    date = dt.strftime("%Y-%m-%d")
    hour = dt.strftime("%I:%M%p").lower().lstrip("0")

    # get a drawing context
    draw = ImageDraw.Draw(img)

    # fine tune the position of the timestamps
    voffset = 20
    hoffset = 15

    # line 1 (the hour)
    #draw.text((widthtarget-160+hoffset, heighttarget-90+voffset), hour, fontcolor, font=font)

    # line 2 (the date)
    draw.text(( widthtarget-160+hoffset, heighttarget-60+voffset), date, fontcolor, font=fontsmall)

    try: os.makedirs( os.path.dirname(new_filename) )
    except: pass
    
    img.save(new_filename, quality=90)

    return new_filename







textfile_fname = os.path.abspath(current_directory + "/temp/imagepaths.txt")
start_time = time.time()
delete_counter = 0
pics = []

if rebuild_pic_list:

    print ( "Making a listing of all the files in %s" % pics_dname )

    pics_raw = os.listdir(pics_dname)
    print ( "Found %s files in the directory..." % len(pics_raw) )
    for p in pics_raw:

        fname_full = os.path.abspath(pics_dname + "/" + p)

        try: ext = os.path.splitext(p)[1].lower()
        except: continue

        if ext != ".jpeg" and ext != ".jpg": continue # skip non image files

        # check filesizes
        fsize = os.stat(fname_full).st_size
        if fsize < 2000:
            print ( "Discarding %s because it's %s bytes..." % (fname_full, fsize) )

            # delete it? %% should just move it to /deleted or something
            os.unlink(fname_full)

            delete_counter += 1
            continue    


        # add a timestamp?
        if add_timestamps: fname_full = overlay_timestamp(fname_full)


        pics.append(fname_full)


        # hard limit the number of pics?
        if number_of_pics_limit:
            if len(pics) > number_of_pics_limit:
                print ( "Limited the number of pics to number_of_pics_limit of %s (now have %s)" % (number_of_pics_limit, len(pics) ) )
                break        




    
    print ( "After sorting, there's %s pics (%s pics deleted)..." % (len(pics), delete_counter) )





        






    # make the text file
    #file 'E:\images\png\images__%3d.jpg'
    #file 'E:\images\jpg\images__%3d.jpg'
    try: os.makedirs( os.path.dirname(textfile_fname) )
    except: pass

    output = ""
    for p in pics:
        
        line = "file '%s'\n" % p
        output += line

    handle = open(textfile_fname, "w")
    handle.write(output)
    handle.close()

    print ( "Done creating pic listing file %s" % textfile_fname )


else:

    print ( "Re-using the old pic list because 'rebuild_pic_list' is set to False...." )






# if the output filename exists, add a number to it
original_fname = output_fname
for i in range(2, 50):
    if not os.path.exists(output_fname): break
    else:
        try: ext = os.path.splitext(original_fname)[1]
        except: ext = ".mp4"
        output_fname = os.path.splitext(original_fname)[0] + "-" + str(i) + ext
        output_fname = os.path.abspath(output_fname)

try: os.makedirs( os.path.dirname(output_fname) )
except: pass





########################
# compose FFmpeg command
########################

cmd = '"%s" ' % ffmpeg
cmd += "-y " # say "yes" to overwrite the target file if present

# INPUT FRAMERATE (good = 80)
# This is how many FPS it will use on the input.
# Set the output FRS separately below.
# For example if this is 80 FPS and the output is 30 FPS, ffmpeg will drop frames, slowing down the timelapse.
cmd += "-r 80 " # framerate. Youtube recommends 24, 25, 30, 48, 50 or 60 fps


cmd += '-f concat -safe 0 -i "%s" ' % textfile_fname # -safe 0 parameter prevents Unsafe file name error 
cmd += "-vcodec libx264 "




# RESOLUTION (this param must be after vcodec?)
# source images are 1000x562
# I think both numbers must be even
cmd += "-s 1280x720 " 
#cmd += "-s 1920x1080 " 


# AMOUNT OF COMPRESSION
# 0 is losses, 23 is default, 51 is worst possible quality. 17 - 28 is the usual range, with 17 being
# essentially lossless.
cmd += "-crf 18 " # was 20

# not sure if this line helps any... To get higher quality output in theory.
cmd += "-preset slow " 




# use every Nth frame... (here 5).
# from https://superuser.com/questions/1156837/using-every-nth-image-in-sequence-to-create-video-using-ffmpeg
#cmd += "-vf \"select='not(mod(n,5))',setpts=N/30/TB\" "


# OUTPUT FRAMERATE
# (good = 30)
# If removed it will use the input framerate.
# If it's slower than the input frramerate will drop frames.
cmd += "-r 30 " # 


cmd += '"%s"' % output_fname

print ( "\nWill use the following ffmpeg command:\n" )
print cmd

# save the command just for goofs
handle = open(current_directory + "/last_cmd.txt", "w")
handle.write(cmd)
handle.close()


if pics: print ( "Starting to build timelapse from %s pics..." % len(pics) )
p = subprocess.Popen(cmd)
p.communicate()




# print a triumphant finishing message
total_time = int(time.time() - start_time) #
total_time_hms = time.strftime('%H:%M:%S', time.gmtime(total_time)) # format the time as hh:mm:ss
print ( "\nDone building %s in %s seconds" % (output_fname, total_time_hms) )




