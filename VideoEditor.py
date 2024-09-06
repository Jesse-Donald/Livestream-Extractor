from moviepy.editor import *
from datetime import datetime
from getconfig import getTimes

def trimVideo()

    config = getTimes()

    sermonStart = datetime.fromisoformat(config['Sermon Start'])
    sermonEnd = datetime.fromisoformat(config['Sermon Start'])
    streamStart = datetime.fromisoformat(config['Sermon Start'])
    streamEnd = datetime.fromisoformat(config['Sermon Start'])

    clipStart = sermonStart - streamStart
    clipEnd = sermonEnd - streamStart
    
    clip = VideoFileClip("stream.mp4")

    editedClip = clip.sublcip(clipStart.secconds, clipEnd.secconds)

    editedClip.write_videofile("editedstream.mp4")
