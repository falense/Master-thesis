

import os
import shutil
import re

from subprocess import call



temp_folder = "./temp"

def make_video(post_fix):
    images = os.listdir("./")

    def filter_images(imagename):
        if imagename[-5:] == ("%s.png" % post_fix):
            return True
        else:
            return False
    frame_names = filter(filter_images,images)
    
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    def get_key(filename):
        
        m = re.search('Angle spread ([0-9]*)', filename)
        return int(m.group(1))
    frame_names = sorted(frame_names, key =get_key)

    for i,frame_name in enumerate(frame_names):
        print get_key(frame_name)
        dst = os.path.join(temp_folder,"%s.png" % i)
        print frame_name
        shutil.copy(frame_name,dst)
    
    call("ffmpeg -r 6 -i temp/%d.png video" + post_fix + ".avi" , shell=True)
    
    shutil.rmtree(temp_folder)
make_video("1")
make_video("2")
